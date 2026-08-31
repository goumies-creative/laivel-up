# Codebase Audit: performance — goumies-creative-laivel-up

Pillier performance — audit du 2026-08-28, lecture seule sur `src/laivelup/` + `scripts/`.

- **Date** : 2026-08-28
- **Scope** : `src/laivelup/*.py`, `scripts/generate_profile.py`, `scripts/benchmark.py`
- **Méthode** : analyse statique des fichiers sources (pas de profiler exécutable). Lecture ciblée des patterns chauds : boucles, I/O, compilation regex, sous-processus, mémoire, string building.
- **Health** : good
- **Findings** : 0 critical, 3 warnings, 4 minor

## Résumé

Le moteur de scoring (`scoring.py`) est propre : complexité O(1) par évaluation (4 axes fixes, listes bornées). Le rendu (`report.py`) est correct (list + join). Les vrais points chauds sont : (1) la compilation regex répétée dans `cli.py:_merge_answer()` et `generate_profile.py`, (2) les imports locaux inutiles dans `team.py`, et (3) la création répétée d'un dict de scorers dans `evaluate()`. Le finding `generate_profile.py:_detect_pr_sizes` signalé le 23/08 est maintenant corrigé (single `git log --shortstat`).

## Findings

| # | Sev | Category | Location | Issue | Suggested fix | Effort |
|---|-----|----------|----------|-------|---------------|--------|
| 1 | 🟡 | regex | `cli.py:577` | `_merge_answer()` compile `rf'\b{size}\b'` via `re.search()` à chaque itération de la boucle `for size in ('S','M','L','XL')`. Pattern dynamique, mais 4 appels `re.search()` par réponse. | Pré-calculer les patterns ou utiliser `size.lower() in low.split()` (la réponse est en minuscule). | XS |
| 2 | 🟡 | regex | `generate_profile.py:131-132` | `_detect_retry_loops()` compile `re.search(r'retry\|rerun\|...', content, re.I)` à chaque appel de fonction. Le pattern ne change jamais. | Monter le `re.compile()` au niveau module (constant `RETRY_PATTERN`). | XS |
| 3 | 🟡 | import-local | `team.py:34` | `_validate_team_name()` fait `import re` à chaque appel au lieu du niveau module. Surcharge de lookup sur la stack d'imports à chaque exécution. | Déplacer `import re` en haut du fichier. | XS |
| 4 | 🟢 | caching | `scoring.py:367-372` | `evaluate()` recrée le dict `scorers = {'size': size_max, ...}` à chaque appel. Petit coût mais inutilement répété. | Déclarer `SCORERS` au niveau module (constante). | XS |
| 5 | 🟢 | regex | `generate_profile.py:160` | `_detect_retries_after_fact()` compile `fix_patterns = re.compile(...)` à chaque appel. Pattern constant. | Monter au niveau module. | XS |
| 6 | 🟢 | regex | `generate_profile.py:219` | `_detect_agents_autonomous()` compile `re.search(r'schedule\|workflow_dispatch\|...', content)` à chaque appel. | Monter au niveau module. | XS |
| 7 | 🟢 | redundancy | `team.py:273,337` | `export_markdown()` et `export_html()` calculent chacune `opt_out_slugs = {s for s,m in team.members.items() if m.opt_out}` indépendamment. | Extraire en helper ou passer en paramètre. | XS |

## Détails

### Finding 1 — Regex dynamique dans `_merge_answer()`

**Fichier** : `cli.py:572-619`

La fonction `_merge_answer()` gère 7 questions différentes. Pour la question `PR_SIZES` (ligne 577), elle exécute :

```python
matched = [size for size in ('S', 'M', 'L', 'XL') if re.search(rf'\b{size}\b', answer)]
```

Ceci compile 4 patterns regex dynamiques par appel. La réponse est déjà en minuscule (`low = answer.strip().lower()`), donc `re.search(rf'\b{s}\b', answer)` pourrait être remplacé par `s in low.split()` ou `s.lower() in answer.lower().split()` — pas besoin de regex pour des mots entiers quand les tokens sont séparés par des espaces.

Pour les autres branches (lignes 598, 608, 613), les patterns sont fixes et pourraient être des constantes module.

**Impact** : xs — 4 appels `re.search()` simples par réponse. Pas mesurable à l'échelle actuelle (un seul profil à la fois).

**Fix suggéré** :
```python
# Avant (4 regex par appel)
matched = [size for size in ('S','M','L','XL') if re.search(rf'\b{size}\b', answer)]

# Après (0 regex)
tokens = set(low.split())
matched = [s for s in ('s','m','l','xl') if s in tokens]
```

### Finding 2 — Regex compilée dans `_detect_retry_loops()`

**Fichier** : `scripts/generate_profile.py:117-139`

```python
def _detect_retry_loops(repo: Path) -> bool:
    ...
    for workflow in path.glob('*.yml'):
        content = workflow.read_text(...)
        if re.search(r'retry|rerun|re-run|continue-on-error|timeout-minutes', content, re.I):
            return True
```

Le pattern `re.compile(r'retry|rerun|...', re.I)` est créé à chaque exécution de la fonction. Le pattern ne change jamais.

**Impact** : xs — le script tourne 1 fois par profil généré.

**Fix suggéré** : `_RETRY_PATTERN = re.compile(r'retry|rerun|re-run|continue-on-error|timeout-minutes', re.I)` au niveau module.

### Finding 3 — Import local `re` dans `_validate_team_name()`

**Fichier** : `team.py:34`

```python
def _validate_team_name(name: str) -> None:
    import re  # <-- import à chaque appel
    if not name or not re.fullmatch(r'[a-zA-Z0-9_-]{1,64}', name):
        ...
```

Python met les modules en cache dans `sys.modules`, donc le coût est un dict lookup répété sur la stack d'imports. Inutile et non idiomatique.

**Impact** : xs — appelé 1 fois par création d'équipe.

**Fix** : Déplacer `import re` au début du fichier.

### Finding 4 — Dict `scorers` recréé dans `evaluate()`

**Fichier** : `scoring.py:367-372`

```python
def evaluate(profile: ProfileData) -> Verdict:
    ...
    scorers = {
        'size': size_max,
        'harness': harness_max,
        'intervention': intervention_max,
        'parallel': parallel_max,
    }
    for axe in AXES:
        level, confidence, evidence = scorers[axe](profile.traces)
```

Le dict est recréé à chaque appel. Les 4 fonctions ne changent jamais.

**Impact** : xs — le coût de création d'un dict de 4 éléments est négligeable (<1µs). C'est un code smell plus qu'un vrai problème de perf.

**Fix** : `SCORERS = {'size': size_max, ...}` au niveau module.

### Finding 5-6 — Regex compilées dans `generate_profile.py`

**Fichiers** : `generate_profile.py:160`, `generate_profile.py:219`

Deux autres patterns regex constants compilés à l'intérieur de fonctions :
- `fix_patterns = re.compile(r'\b(fix|correct|amend|revert|patch|oops)\b', re.I)` (ligne 160)
- `re.search(r'schedule|workflow_dispatch|repository_dispatch', content)` (ligne 219)

**Impact** : xs — le script tourne 1 fois par profil.

**Fix** : Constantes module.

### Finding 7 — `opt_out_slugs` calculé en double

**Fichier** : `team.py:273,337`

`export_markdown()` et `export_html()` calculent toutes les deux :
```python
opt_out_slugs = {s for s, m in team.members.items() if m.opt_out}
```

**Impact** : xs — le set est tiny (max 50 membres).

**Fix** : Extraire en helper `team.opt_out_slugs()` ou passer le set calculé en paramètre.

## Constat global

| Zone | Verdict |
|------|---------|
| `scoring.py` (moteur) | Propre. O(1) par évaluation, 4 axes fixes, listes bornées. Le dict `scorers` recréé (finding 4) est un code smell mais pas un goulot. |
| `report.py` (rendu) | Propre. List + join, pas de concaténation en boucle. |
| `cli.py` (interface) | Acceptable. Les regex dynamiques (finding 1) sont les plus notables mais bornées (4 appels par réponse). |
| `team.py` (gestion équipe) | Propre. `_MAX_HISTORY=100`, `_MAX_MEMBERS=50`. Les imports locaux (finding 3) sont le seul point. |
| `generate_profile.py` (génération) | Le finding `git diff --stat` ×50 du 23/08 est corrigé. Les regex non précompilées (findings 2,5,6) restent. |
| `schema.py` (validation) | Bon — lazy load + cache du schema. Import `jsonschema` intentionnel (optional dep). |
| `encoding.py` (UTF-8) | Propre. `ascii_fallback()` est un dict lookup, pas une boucle lente. |
| `benchmark.py` | Propre — in-process + subprocess, timeout configuré. |

## Pas de problèmes trouvés (confirmé)

- **N+1 patterns** : aucun. Pas de DB, pas de requêtes imbriquées. Les appels `git` dans `generate_profile.py` sont bornés (7 appels fixes).
- **Mémoire** : aucun retaining path anormal. `_MAX_HISTORY=100` protège `team.history`. Les profils sont des dicts petits.
- **Sous-processus** : timeout=30 sur tous les `_git()` et subprocess du benchmark. Nécessaires (analyse git locale).
- **Async** : pas pertinent — CLI synchrone, pas de serveur web. Un seul profil à la fois.
- **String concat dans boucles** : aucun — partout c'est list + join ou f-string directe.
- **`fetch-depth: 0`** : toujours nécessaire pour les analyses `--since=1 year ago` dans `aidd-eval.yml`. Non modifiable tant que le clone complet est requis.

## Couverture

- **Scanned** : `src/laivelup/scoring.py`, `report.py`, `team.py`, `cli.py`, `model.py`, `scoring_defaults.py`, `schema.py`, `encoding.py`, `questions.py` ; `scripts/generate_profile.py`, `benchmark.py`.
- **Skipped** : pas de profiler exécutable — analyse statique uniquement. Les chiffres de latence (ex: spawn process ~15-40ms) sont des estimations, pas des mesures.
- **Comparaison audit précédent** : le finding critique `_detect_pr_sizes` ×50 (23/08) est maintenant corrigé (single `git log --shortstat`). Le `--in-process` benchmark (23/08) est en place. Trois nouveaux findings regex/import identifiés, tous de sévérité xs-s.
