# Codebase Audit: goumies-creative-laivel-up (7 piliers)

Les fondations sont bonnes (sécurité, CI 3 OS × 3 Python, moteur de scoring à 100% de couverture branch, culture de test riche), mais deux bugs critiques et croisés touchent les deux fonctionnalités phares que le README met en avant : `evaluate` après une install standard, et l'ensemble des commandes `team`.

- **Date**: 2026-08-23
- **Scope**: `C:\Users\Romy\Desktop\GoumiesLand\GoumiesCreative-Agency\hackathons\goumies-creative-laivel-up` (hors `.git`, caches, `__pycache__`)
- **Health**: poor
- **Findings**: 7 critical, 9 warning, 3 minor (19 au total)

## Findings

| Sev | Category | Location | Issue | Suggested fix | Effort |
| --- | --- | --- | --- | --- | --- |
| 🔴 | architecture | `src/laivelup/schema.py:13` | Violation ADR-0011 : `_SCHEMA_PATH` (3× `.parent`) n'est valide qu'en install éditable. Après `pip install .` / `pipx install laivelup` / `uv tool install laivelup` (méthodes documentées au README, y compris pour les juges du hackathon), `evaluate`/`interrogate` plantent (`RuntimeError` non rattrapé). Déjà connu et contourné dans les tests (`tests/test_schema_compat.py:1-7`) sans être corrigé en prod. | Déplacer `schemas/` sous `src/laivelup/schemas/`, `importlib.resources` + `package-data` | M |
| 🔴 | dependencies | `pyproject.toml:30-31` | Aucun `[tool.setuptools.package-data]` : `schemas/profile.schema.json` n'est pas empaqueté dans le wheel — cause racine du finding architecture ci-dessus. | Ajouter `package-data` après déplacement du schéma sous `src/laivelup/` | M |
| 🔴 | tests | `tests/test_install_clean.py:29-38` | Après install non-éditable, seul `evaluate --help` est testé — jamais une vraie évaluation. Le test qui aurait détecté la régression ci-dessus s'arrête juste avant. | Étendre le test avec une vraie commande `evaluate` sur un profil d'exemple | S |
| 🔴 | code-quality | `src/laivelup/cli.py:230` | `team evaluate` recrée un `Team` vide à chaque appel et bricole un objet `type("Member", ...)` au lieu du domaine (`MemberSnapshot`) — aucune persistance. | Charger/sauvegarder l'équipe (JSON) avant d'appeler `evaluate_member()` | M |
| 🔴 | code-quality | `src/laivelup/cli.py:266` | `team export` exporte toujours une équipe vide (0 membre, 0 historique). | Idem : charger l'état persistant avant export | S |
| 🔴 | code-quality | `src/laivelup/cli.py:281,302` | `team opt-out` et `team remove` échouent systématiquement (`ValueError`) — ces sous-commandes ne peuvent jamais réussir. | Idem persistance partagée | S |
| 🔴 | tests | `tests/test_cli_extended.py` (`TestTeamCommands`) | Les tests des commandes `team` ne vérifient que le code de sortie, jamais le contenu — masquent complètement les 3 bugs `team_*` ci-dessus. | Assertions sur le contenu réel exporté | M |
| 🟡 | architecture | `docs/architecture.mmd` | Diagramme officiel : 5 scripts sur 10 absents, dont ceux qui alimentent `aidd-eval.yml` (fonctionnalité visible). | Mettre à jour le diagramme | S |
| 🟡 | architecture | `src/laivelup/team.py` | Aucune fonction `load_team`/`save_team` ; frontière CLI↔domaine non actée par une ADR. | ADR dédiée + fonctions de persistance | M |
| 🟡 | code-quality | `src/laivelup/cli.py:29` | Import mort `evaluate_member` — jamais appelé, trace du câblage inachevé. | Utiliser ou retirer l'import | S |
| 🟡 | code-quality | `scripts/apply_calibration_fix.py:127,146` | Scénarios B/C affichent un succès sans exécuter aucune action réelle (`# TODO`). | Implémenter ou lever `NotImplementedError` | M |
| 🟡 | dependencies | `requirements.lock:1-8` | Lockfile dev incomplet : ni `jsonschema` (dépendance runtime), ni les 9 outils `[dev]` déclarés. | Régénérer le lockfile avec `.[dev]` | S |
| 🟡 | performance | `scripts/generate_profile.py:46-47` | `_detect_pr_sizes` : un sous-processus `git diff --stat` par commit (jusqu'à 50), non batché. | Un seul `git log --shortstat` agrégé | M |
| 🟡 | security | `.github/workflows/aidd-eval.yml` | `verdict.md` interpolé dans un template literal JS sans échappement avant de poster le commentaire de PR. | Échapper `` ` ``/`${` ou passer par une variable d'env | S |
| 🟡 | ui | `src/laivelup/cli.py:215` | Message « Équipe créée » laisse croire à une persistance inexistante. | Message honnête tant que le fix n'est pas livré | S |
| 🟡 | ui | `src/laivelup/cli.py:268` | `team export` affiche un succès même pour un export vide. | Signaler l'état « équipe vide » | S |
| 🟢 | code-quality | `scripts/calibrate_degraded.py:87,104` | Vocabulaire d'axes générique déconnecté de `model.AXES` ; `computed = declared` ne calcule rien. | Documenter comme placeholder ou aligner sur `AXES` | S |
| 🟢 | performance | `scripts/benchmark.py:24-40` | Benchmark dominé par le cold-start de l'interpréteur, pas la logique de scoring. | Ajouter un micro-benchmark in-process | S |
| 🟢 | ui | `src/laivelup/report.py:99-149` | Rapport HTML sans repère sémantique `<main>`. | Envelopper le contenu dans `<main>` | S |

## Top actions

1. **Corriger `schema.py:13` + empaqueter `schemas/` correctement** (architecture + dependencies) — sans ça, `laivelup evaluate` plante pour quiconque installe le package comme le recommande le README, juges du hackathon inclus.
2. **Étendre `test_install_clean.py` avec une vraie commande `evaluate` post-install** (tests) — le correctif le moins cher (S) et le plus rentable : il aurait détecté le point 1 avant publication.
3. **Ajouter une persistance JSON au Team Tracker et brancher `cli.py` dessus** (code-quality + architecture) — résout d'un coup les 3 commandes `team` cassées et le finding tests correspondant.
4. **Renforcer les assertions de `TestTeamCommands`** sur le contenu réel exporté, pas seulement le code de sortie.
5. **Régénérer `requirements.lock`** pour qu'il couvre réellement les dépendances déclarées (`jsonschema` + outils `[dev]`).

## Coverage

- **Scanned**: code-quality, architecture, security, dependencies, performance, tests, ui — sur `src/laivelup/`, `scripts/`, `tests/`, `.github/workflows/`, `docs/adr/`, `docs/architecture.mmd`, `pyproject.toml`, `requirements.lock`, `schemas/`.
- **Skipped**: exécution live d'outils (`pytest --cov`, `bandit`, `pip-audit`, profiler) — pas d'outil d'exécution de code disponible sur la machine de l'utilisatrice dans cet environnement d'audit ; analyse fondée sur lecture statique croisée (code + tests + CI + README + ADR), sans aucune modification apportée au code. Atténuant : `.github/workflows/ci.yml` fait déjà tourner lint, mypy, tests sur 3 OS × 3 versions Python, bandit, pip-audit et la suite `tests/security/` à chaque push — l'outillage qualité est en place, ce sont deux angles morts précis (persistance Team, install non-éditable) qui laissent passer les findings critiques.
