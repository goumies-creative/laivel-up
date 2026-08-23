# Codebase Audit: code-quality — goumies-creative-laivel-up

Le moteur de scoring est propre et bien testé, mais le câblage CLI ↔ Team Tracker est resté inachevé : les commandes `team` recréent un état vide à chaque appel.

- **Date**: 2026-08-23
- **Scope**: codebase entière (`src/`, `scripts/`)
- **Health**: poor
- **Findings**: 3 critical, 2 warning, 1 minor

## Findings

| Sev | Category | Location | Issue | Suggested fix | Effort |
| --- | --- | --- | --- | --- | --- |
| 🔴 | code-quality | `src/laivelup/cli.py:230` | `team_evaluate` instancie `Team(name=team_name)` à chaque appel (aucune persistance) puis crée un objet ad hoc via `type("Member", (), {...})()` au lieu du `MemberSnapshot` du domaine. L'évaluation réelle passe par `evaluate()` brut, pas par `evaluate_member()`. | Charger/sauvegarder l'équipe depuis un store JSON avant d'appeler `evaluate_member()` (déjà importé, jamais utilisé) | M |
| 🔴 | code-quality | `src/laivelup/cli.py:266` | `team_export` exporte toujours une équipe vide : `team = Team(name=team_name)` recrée un objet sans membres ni historique avant chaque export. | Charger l'état persistant avant export | S |
| 🔴 | code-quality | `src/laivelup/cli.py:281,302` | `team_opt_out` et `team_remove` échouent systématiquement (`ValueError: Membre non trouvé`) car ils opèrent sur un `Team` neuf et vide — ces deux sous-commandes ne peuvent jamais réussir. | Idem : ajouter une couche de persistance partagée | S |
| 🟡 | code-quality | `src/laivelup/cli.py:29` | Import mort : `evaluate_member` est importé depuis `team.py` mais n'est appelé nulle part dans `cli.py` — trace du câblage CLI↔Team laissé inachevé. | Utiliser `evaluate_member()` une fois la persistance ajoutée, ou retirer l'import | S |
| 🟡 | code-quality | `scripts/apply_calibration_fix.py:127,146` | `apply_scenario_b` et `apply_scenario_c` impriment un message de succès (« Regenerated expected.json », « Added "Known Gaps"... ») même hors `--dry-run`, sans exécuter aucune action réelle (`# TODO: implement...`). | Implémenter les scénarios B/C, ou lever `NotImplementedError` plutôt que simuler un succès | M |
| 🟢 | code-quality | `scripts/calibrate_degraded.py:87,104` | Le diagnostic dégradé utilise un vocabulaire d'axes générique (`specification/planning/implementation/validation`) sans rapport avec les 4 axes réels du moteur (`AXES` dans `model.py`), et `computed = declared` ne calcule rien — le diagnostic recopie juste la valeur déclarée. | Documenter que ce sont des placeholders (grille officielle attendue le 28/08), ou aligner sur `laivelup.model.AXES` | S |

## Top actions

1. Ajouter une couche de persistance (JSON local) au `Team` Tracker et brancher `cli.py` dessus — résout les 3 findings critiques `team_*` d'un coup (résout aussi le finding tests correspondant).
2. Traiter `evaluate_member` : soit l'utiliser réellement, soit le retirer — signal clair que le câblage est incomplet.
3. Remplacer les faux succès de `apply_calibration_fix.py` scénarios B/C par une erreur explicite tant qu'ils ne sont pas implémentés.

## Coverage

- **Scanned**: code-quality (`src/laivelup/*.py`, `scripts/*.py`)
- **Skipped**: none — pas d'outil de complexité cyclomatique automatisé disponible dans cet environnement (pas d'exécution sur la machine de l'utilisatrice) ; l'analyse s'appuie sur lecture statique du code, sans changement apporté.
