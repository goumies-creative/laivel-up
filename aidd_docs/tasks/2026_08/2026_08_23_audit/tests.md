# Codebase Audit: tests — goumies-creative-laivel-up

Excellente culture de test sur le moteur (100% branch sur `scoring.py` via ADR-0009, property-based avec hypothesis, snapshots, suite sécurité dédiée) — mais deux angles morts précis laissent passer les deux bugs critiques du reste de l'audit.

- **Date**: 2026-08-23
- **Scope**: `tests/`
- **Health**: poor
- **Findings**: 2 critical, 0 warning, 0 minor

## Findings

| Sev | Category | Location | Issue | Suggested fix | Effort |
| --- | --- | --- | --- | --- | --- |
| 🔴 | tests | `tests/test_cli_extended.py` (classe `TestTeamCommands`, ex. `test_team_export_md`, `test_team_evaluate`) | Ces tests des commandes `team evaluate`/`team export` ne vérifient que `r.exit_code == 0`, jamais le contenu réel du fichier exporté ni la présence des membres créés en amont — ils masquent complètement le bug de persistance (cf. code-quality/architecture : chaque commande recrée un `Team` vide). | Ajouter des assertions sur le contenu (`out.read_text()` contient les membres attendus, `data["members"]` non vide) pour transformer ces tests en véritables tests de bout en bout | M |
| 🔴 | tests | `tests/test_install_clean.py:29-38` (`test_cli_version`) | Après une install propre non-éditable (`pip install .`, testée juste au-dessus), ce test n'exécute que `laivelup evaluate --help` — jamais une vraie évaluation (`laivelup evaluate exemples/profil-maison-1.json`). C'est exactement le chemin qui casse (résolution du schéma, cf. architecture). `tests/test_schema_compat.py:1-7` documente d'ailleurs explicitement ce problème connu sans jamais le faire couvrir en install réelle. | Étendre `test_install_clean.py` pour exécuter une vraie commande `evaluate` sur un profil d'exemple après install non-éditable — aurait détecté la régression avant publication | S |

## Top actions

1. Étendre `test_install_clean.py` avec une vraie commande `evaluate` post-install — le fix le moins cher et le plus rentable de tout l'audit (S, détecte le bug le plus critique).
2. Renforcer les assertions de `TestTeamCommands` sur le contenu exporté, pas seulement le code de sortie.

## Coverage

- **Scanned**: tests (`tests/*.py`, `tests/security/*.py`, config `pytest`/`coverage` dans `pyproject.toml`)
- **Skipped**: rapport de couverture live (`pytest --cov`) — pas d'outil d'exécution de code sur la machine de l'utilisatrice dans cet environnement d'audit ; l'inspection s'appuie sur lecture statique des fichiers de test et sur les seuils déclarés (`--cov-fail-under=85`, 100% sur `scoring.py` via ADR-0009). Points forts à noter : pyramide de tests saine (majorité unitaire + `CliRunner` in-process, peu de tests `@pytest.mark.slow`/`install`), tests property-based (hypothesis) et snapshots présents.
