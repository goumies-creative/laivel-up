# Codebase Audit: tests

Pilier « tests » du projet goumies-creative-laivel-up — audit read-only du 2026-08-31.

- **Date**: 2026_08_31
- **Scope**: tests/ + coverage_report.txt + pyproject.toml config
- **Health**: good
- **Findings**: 0 critical, 4 warning, 3 minor

## Findings

| Sev | Category | Location | Issue | Suggested fix | Effort |
| --- | --- | --- | --- | --- | --- |
| 🟡 | tests | `tests/test_team.py:16-27` | Tests importent `_slug` (fonction privée) directement — couplage implémentation. Les tests RGPD testent le comportement anonymisation via les exports, pas via `_slug`. | Supprimer les imports `_slug` dans les tests non-RGPD ; tester l'anonymisation via export JSON/CSV uniquement. | S |
| 🟡 | tests | `tests/test_snapshots.py` | 13 snapshots (syrupy) vs ~20 tests unitaires scoring — pyramide inversée pour le noyau critique. Les snapshots captent le format Rich, pas la logique métier. | Ajouter des tests unitaires de regression sur les cas limites du scoring (déjà bien couvert par hypothesis, mais les snapshots debuguent le format, pas la logique). | S |
| 🟡 | tests | `tests/test_load.py:22,37` | Tests de charge marqués `@pytest.mark.slow` mais pas de skip conditionnel en CI (timeout 5s fixe). Si CI lent, ces tests flakent. | Ajouter `@pytest.mark.skipif` sur variable d'env ou marker `slow` exclu par défaut via `-m "not slow"`. | S |
| 🟡 | tests | `tests/test_install_clean.py:47-55` | Tests install clean invoquent `laivelup` via subprocess sans vérifier l'installation réelle (pip install -e .). Peuvent passer en dev mais échouer en CI clean. | Documenter les prérequis (venv activé, package installé) ou ajouter un guard `pytest.importorskip` sur le CLI. | S |
| 🟢 | tests | `tests/conftest.py:11-16` | `_isolate_team_dir` est `autouse=True` pour tous les tests, y compris ceux qui n'utilisent pas team. Overhead minime mais inutile. | Restreindre le fixture aux tests qui l'utilisent (scope=module ou marker). | S |
| 🟢 | tests | `tests/test_demo.py` | Tests structurels lisent le fichier demo.py comme texte (shebang, imports) au lieu de l'importer. Fragiles si refactoring. | Convertir en tests d'import + exécution mockée (déjà fait dans TestDemoExecution). Supprimer les tests structurels redondants. | S |
| 🟢 | tests | `pyproject.toml:170-173` | mutmut config `runner = "python -m pytest ..."` — commande inline non testée en CI. Les survivants mutmut ne sont pas rejétés automatiquement. | Ajouter un script CI `mutmut run && mutmut results` ou documenter le workflow manuel dans TESTING_STRATEGY.md. | S |

## Top actions

1. **Revoir le couplage `_slug` dans test_team.py** — Les tests RGPD (`test_team_rgpd.py`) testent correctement le comportement via exports. Les imports `_slug` dans `test_team.py` sont un couplage implémentation mineur mais inutile. Effort S.
2. **Exclure les tests `slow` en CI** — `test_load.py` et `test_install_clean.py::test_cli_evaluate_real` risquent de flaker sur CI lent. Ajouter un marker `slow` exclu par défaut ou un skipif. Effort S.
3. **Réduire les tests structurels de demo.py** — `TestDemoStructure` (6 tests) lit le fichier comme texte ; `TestDemoExecution` le teste déjà en import. Supprimer la redondance. Effort S.

## Coverage

Le rapport de couverture (`coverage_report.txt`) affiche **384 passed, 5 deselected** en 20.26s. La config pytest exige **85% branch** minimum (`--cov-fail-under=85 --cov-branch`).

**Modules couverts par les tests :**

| Module | Couverture | Notes |
| --- | --- | --- |
| `scoring.py` | 100% requis | Mutmut config + property tests hypothesis |
| `team.py` | ≥85% | RGPD, export, persistence, error paths |
| `cli.py` | ≥85% | evaluate, interrogate, team, JSON, fail-on, completion |
| `schema.py` | ≥85% | validate_profile + _validate_minimal |
| `report.py` | ≥85% | render_markdown, render_html, write_reports |
| `encoding.py` | ≥85% | supports_utf8, ascii_fallback (Windows-specific en pragma:no cover) |
| `model.py` | N/A | Dataclasses pures, testées via scoring |
| `questions.py` | N/A | Constantes, testées via test_interactive |
| `scripts/*.py` | ≥85% | benchmark, ci_evaluate, demo, version_bump |

**Tests specialisés :**

- **Security** : bandit regression, path traversal, JSON injection, DoS profil giant (4 fichiers)
- **RGPD** : pseudo-anonymisation, opt-out, droit à l'oubli, export sans PII, sanitize generate_profile
- **Hypothesis** : 6 property tests (invariants, équité, normalisation)
- **Snapshots** : 13 snapshots syrupy (CLI output formatting)
- **Load** : 2 tests performance (1k profils, team 50 membres < 5s)

**Skipped :** Aucun skip sans raison identifié. Les `5 deselected` du coverage report sont les tests marqués `slow` ou `install` non exécutés par défaut.

**Pyramide :** Léger surbascisement snapshots vs unitaires, mais compensé par hypothesis (property-based) et les tests security. Acceptable pour un hackathon.
