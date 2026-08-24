# Deep Dive Performance — LAIVEL UP

**Date** : 2026-08-24
**Méthode** : persona *Performance Oracle* (agent `references/agents/performance-oracle.md`, skills `ce-compound`/`ce-plan` du plugin compound-engineering, cache local `~/.cache/opencode/...`) appliquée manuellement au code actuel — lecture directe de `src/laivelup/*.py`, `scripts/generate_profile.py`, `scripts/benchmark.py`, `scripts/ci_evaluate.py`, `.github/workflows/aidd-eval.yml`, comparaison avec l'audit performance du 23/08 (`performance.md`) et le deep dive adversarial du 24/08 (`adversarial-deep-dive.md`).
**Angle** : pas juste « y a-t-il un goulot », mais complexité algorithmique, coût I/O/process, et projection à l'échelle (×10/×100) — sans profiler exécutable disponible dans cet environnement (heuristique statique, comme l'audit du 23/08).

## 0. Ce qui était déjà signalé le 23/08 — état aujourd'hui

Contrairement aux 3 bugs critiques de sécurité/persistance résolus entre le 23/08 et le 24/08 (voir `adversarial-deep-dive.md` §0), le finding performance principal du 23/08 est **toujours présent tel quel** dans le code :

- `scripts/generate_profile.py:46-47` (`_detect_pr_sizes`) : toujours un sous-processus `git diff --stat` par commit, jusqu'à 50 itérations séquentielles. Pas corrigé.

En revanche, la recommandation « 🟢 minor » du 23/08 sur `benchmark.py` **a été traitée** : le script a maintenant un mode `--in-process` (`run_benchmark_inprocess`) en plus du benchmark subprocess, et l'exécute systématiquement en complément dans `main()`. Ça, c'est fait.

## 1. Performance Summary

Le moteur de scoring (`scoring.py`) et le rendu (`report.py`) sont propres : tout est O(1) par rapport au volume réel de données (4 axes fixes, listes bornées), aucune boucle imbriquée sur des collections non bornées, aucun pattern N+1 côté stockage (JSON local, pas de DB). Le point chaud n'est pas le moteur d'évaluation — c'est la **génération de profil côté CI** (`generate_profile.py`), qui tourne à chaque `pull_request: [opened, synchronize]`, donc à chaque push sur une PR et pas une seule fois par PR.

## 2. Critical Issues

Aucun. Rien ne dépasse le budget CI (`timeout-minutes: 5`) au volume actuel du repo (hackathon, quelques dizaines de commits). Le point ci-dessous devient critique seulement en projection à l'échelle (§4).

## 3. Optimization Opportunities

### 3.1 `_detect_pr_sizes` — jusqu'à 51 process `git` séquentiels au lieu de 1

**Fichier** : `scripts/generate_profile.py:33-49`

```python
def _detect_pr_sizes(repo: Path, user: str) -> list[str]:
    log = _git(repo, ["log", "--author=" + user, "--format=%H", "--merges", "--since=1 year ago"])
    ...
    for commit_hash in log.splitlines()[:50]:
        stats = _git(repo, ["diff", "--stat", commit_hash + "^1", commit_hash])
```

Chaque `_git()` spawn un process (`subprocess.run`, `timeout=30`). Sur un runner GitHub Actions, le coût de démarrage d'un process `git` tourne autour de 15-40ms — sur 50 itérations séquentielles, ça ajoute environ **0,75 à 2 secondes** de pur overhead de spawn (avant même le coût du `diff --stat` lui-même), à *chaque* run du workflow, qui se déclenche sur `opened` **et** `synchronize`.

**Correctif** (celui déjà recommandé le 23/08, prêt à appliquer) — un seul `git log --shortstat` au lieu de 1+50 process :

```python
def _detect_pr_sizes(repo: Path, user: str) -> list[str]:
    """Classe les PRs de l'utilisateur par taille (S/M/L/XL) via un seul appel git."""
    log = _git(repo, [
        "log", "--author=" + user, "--merges", "--since=1 year ago",
        "--format=@@%H", "--shortstat",
    ])
    if not log:
        return []

    sizes: list[str] = []
    current_files = 0
    for line in log.splitlines():
        if line.startswith("@@"):
            if current_files:
                sizes.append(_bucket_size(current_files))
            current_files = 0
        else:
            match = re.search(r"(\d+) files? changed", line)
            if match:
                current_files = int(match.group(1))
    if current_files:
        sizes.append(_bucket_size(current_files))

    return sizes[:50] if sizes else ["M"]


def _bucket_size(total: int) -> str:
    if total <= 3:
        return "S"
    if total <= 10:
        return "M"
    if total <= 30:
        return "L"
    return "XL"
```

Gain : 51 process → 1 process. Effort : S. C'est un refactor local à une fonction pure ; aucun test existant n'exerce directement `generate_profile.py`, donc un `tests/test_generate_profile.py` dédié serait le bon endroit pour verrouiller le comportement avant/après le remplacement.

⚠️ **Nuance à vérifier avant merge** : `git diff commit^1 commit` calcule le diff contre le **premier parent uniquement**. `git log --shortstat` sur les mêmes commits de merge donne par défaut le diff combiné vs tous les parents, ce qui peut légèrement changer les totaux sur des merges non-fast-forward complexes. À contrôler avec un `git diff` manuel sur 2-3 commits réels du repo avant de basculer — `git log -m --first-parent --shortstat` est l'option la plus proche du comportement actuel si l'écart se confirme.

### 3.2 `_detect_retries_after_fact` / `_detect_parallel_projects` — entrée non bornée avant troncature

**Fichier** : `scripts/generate_profile.py:100-108, 124-138`

`_detect_retries_after_fact` fait `git log --all --since=1 year ago` (toutes les refs, pas juste la branche courante) puis tronque à `lines[:100]` **après** avoir matérialisé toute la sortie en mémoire. Sur le repo actuel c'est instantané, mais `--all` marche toutes les refs — sur un historique plus profond ou plus de branches distantes trackées, le coût de `git log` croît avec le total de commits sur 1 an toutes branches confondues, pas avec les 100 lignes réellement utilisées.

`_detect_parallel_projects` fait deux appels `git branch` (un `--merged`, un sans filtre) là où l'information pourrait tenir en un seul avec post-traitement Python — mineur, 2 process contre 51 pour 3.1, pas la même urgence.

**Recommandation** (pas urgente) : borner le `git log` en amont plutôt qu'en aval :
```python
log = _git(repo, [
    "log", "--author=" + user, "--format=%H %s",
    "--since=1 year ago", "--all", "-n", "100",
])
```
Ça déplace la troncature de « après matérialisation complète en Python » à « git s'arrête après 100 commits » — gain marginal aujourd'hui, protection gratuite si le repo grossit.

### 3.3 `fetch-depth: 0` dans `aidd-eval.yml` — clone complet à chaque run

**Fichier** : `.github/workflows/aidd-eval.yml:32-35`

```yaml
- name: Checkout repo
  uses: actions/checkout@v4
  with:
    fetch-depth: 0  # Historique complet pour analyse
```

Nécessaire aujourd'hui (les analyses `--since=1 year ago` ont besoin de l'historique complet), mais c'est un clone entier à chaque push sur chaque PR. Négligeable au volume actuel. À surveiller : c'est le paramètre qui fera le plus mal en premier si le repo grossit significativement — avant même que la boucle de 3.1 redevienne un vrai goulot.

## 4. Scalability Assessment

| Dimension | Aujourd'hui | ×10 | ×100 |
|---|---|---|---|
| Commits analysés par `_detect_pr_sizes` (plafond actuel) | ≤50 | ≤50 (plafond inchangé) | ≤50 (plafond inchangé) |
| Process `git` spawnés/run (si 3.1 non corrigé) | jusqu'à 51 | jusqu'à 51 (le plafond protège déjà) | jusqu'à 51 |
| Taille du clone (`fetch-depth: 0`) | quelques Mo | proportionnel à l'historique | devient le coût dominant, avant la boucle git |
| Volume `git log --all` avant troncature (3.2) | trivial | croît avec commits×branches | idem, non plafonné côté commande |

Le plafond `[:50]` dans `_detect_pr_sizes` protège déjà contre une explosion algorithmique — pas de O(n²) caché, le nombre de process reste borné même si le repo grossit à l'infini. Le vrai risque, c'est une **constante trop élevée par process** (spawn overhead × 51) répétée à chaque push, pas une complexité qui dérape. Le vrai risque de dérive à l'échelle, c'est `fetch-depth: 0` (3.3) et le `git log --all` non plafonné (3.2) — pas la boucle déjà bornée.

## 5. Recommended Actions (priorisé)

1. **3.1 — Batcher `_detect_pr_sizes`** : fix du 23/08 toujours pas appliqué. Effort S, gain net (51→1 process), zéro risque fonctionnel si le contrôle `--merges` vs `-m --first-parent` est vérifié sur 2-3 commits réels avant merge.
2. **3.2 — Plafonner `git log -n 100`** en amont plutôt qu'en aval en Python, pour `_detect_retries_after_fact`. Effort XS, à faire en même temps que 1.
3. **3.3 — Surveiller `fetch-depth: 0`** : pas d'action aujourd'hui ; si le repo grossit sérieusement, premier paramètre à revoir (ex. `fetch-depth: 400` avec fallback si les analyses `--since` ratent des commits plus anciens).
4. **Aucune action requise** sur `scoring.py`, `report.py`, `team.py`, `cli.py` — tout est déjà borné (4 axes fixes, `_MAX_HISTORY=100`, `_MAX_MEMBERS=50`, cap JSON 2 Mo côté CLI). Bon travail défensif déjà en place, rien à optimiser côté moteur.

## Coverage

- **Scanned** : `src/laivelup/scoring.py`, `report.py`, `team.py`, `cli.py`, `model.py`, `scoring_defaults.py` ; `scripts/generate_profile.py`, `benchmark.py`, `ci_evaluate.py` ; `.github/workflows/aidd-eval.yml`.
- **Skipped** : pas de profiler exécutable dans cet environnement (idem audit 23/08) — analyse statique + calcul manuel du coût de spawn process. Aucune mesure réelle de latence CI (runners GitHub Actions non accessibles depuis ce chat) ; les chiffres « 0,75-2s » sont une estimation d'ordre de grandeur pour un spawn `git` sur Linux, pas une mesure sur ce repo précis. À valider avec `time` en conditions réelles si le sujet devient bloquant avant la deadline.
