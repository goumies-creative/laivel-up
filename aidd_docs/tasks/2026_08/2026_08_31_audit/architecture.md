---
name: architecture-audit
description: Audit du pilier architecture — conformance ADRs/diagramme, coupling, god-modules
argument-hint: goumies-creative-laivel-up
---

# Architecture Audit: goumies-creative-laivel-up

Architecture CLI Python « laivelup » conforme aux ADRs, avec 2 god-modules et 3 artefacts d'érosion.

- **Date**: 2026-08-31
- **Scope**: src/laivelup/, build/, scripts/, docs/adr/, docs/architecture.mmd
- **Health**: fair
- **Findings**: 0 critical, 4 warning, 3 minor

## Findings

| Sev | Category     | Location | Issue | Suggested fix | Effort |
| --- | ------------ | -------- | ----- | ------------- | ------ |
| 🟡  | architecture | `src/laivelup/cli.py:1-985` | **God-module 985 lignes** — combine routing CLI, parsing questions, fusion réponses (`_merge_answer`), détection niveaux (`_LEVELS_BY_KEYWORD`), feedback, formatting. Responsabilités multiples : interaction utilisateur + mutation profil + logique métier. | Extraire `interrogate.py` (question parsing + merge + feedback) et `level_detect.py` (keyword→level). cli.py ne garde que le routing Typer (~200l). | L |
| 🟡  | architecture | `src/laivelup/report.py:1-1051` | **God-module 1051 lignes** — combine rendering MD, rendering HTML, glossaire, références, CSS inline, sérialisation JSON (`verdict_to_dict`). Trois responsabilités distinctes : formats de sortie + contenu pédagogique + sérialisation. | Séparer `report_content.py` (glossaire, références), `report_md.py`, `report_html.py`. `verdict_to_dict` vers `model.py` ou `serialization.py`. | L |
| 🟡  | architecture | `docs/architecture.mmd:1-106` | **Diagramme obsolète** — 4 modules absents du diagramme mais présents dans src/ : `calibrate_core.py`, `calibrate_dashboard.py`, `_completion_patch.py`, `tui/`. Le diagramme ne reflète plus la structure réelle. | Mettre à jour architecture.mmd pour ajouter les modules calibration, le patch Typer, et mentionner le statut du tui/ (squelette vide). | S |
| 🟡  | architecture | `build/lib/laivelup/` | **Érosion architecturale** — build/ contient une copie stale de 14 fichiers Python (cli.py, report.py, scoring.py, etc.) dupliquant src/. Même si .gitignore l'exclut, il est présent dans le workspace et les outils (gc-report) le scannent. | Supprimer build/ du workspace. Ajouter build/ à .gitignore si pas déjà fait (✅ déjà présent). Vérifier que les outils d'audit excluent build/. | S |
| 🟢  | architecture | `src/laivelup/tui/` | **Squelette mort** — Sous-dossiers (mascot/, screens/, viewmodels/, widgets/) vides (seul __pycache__/ présent). Aucun .py. Non référencé dans architecture.mmd. Architecture planifiée mais jamais implémentée. | Soit implémenter le TUI (Textual), soit supprimer le dossier pour éviter la confusion. | S |
| 🟢  | architecture | `src/laivelup/cli.py:41` | **Import calibrate_dashboard dans CLI** — Le dashboard HTML de calibration est importé au chargement de cli.py, couplant le CLI au rendering calibration. Or, `calibrate_core.py` est un module réutilisable séparé (ADR-0013). | Déplacer l'import de `generate_calibrate_html` derrière un lazy import dans la commande `calibrate` uniquement. | S |
| 🟢  | architecture | `src/laivelup/team.py:25` | **team.py → scoring.py** — Le module team importe directement `evaluate` depuis scoring. Selon architecture.mmd, team devrait dépendre de model.py (couche Core) et non directement de scoring. Couplage acceptable mais pas aligné sur le diagramme. | Documenter que team.py est un consommateur de scoring (pas un Core module pur) ou ajuster le diagramme pour montrer cette dépendance. | S |

## Top actions

1. **Extraire les god-modules** (F1, F2) — cli.py et report.py combinés = 2036 lignes. Découper par responsabilité : CLI routing, question parsing, report MD, report HTML, glossaire. Impact : maintenabilité, lisibilité, testabilité. Handoff → `ce-refactor`.
2. **Mettre à jour architecture.mmd** (F3) — Ajouter calibrate_core, calibrate_dashboard, _completion_patch. Statut tui/ (squelette). Aligner le diagramme sur la réalité du code. Effort S.
3. **Nettoyer build/** (F4) — Supprimer le dossier stale. Vérifier que les outils CI/audit l'excluent. Effort S.

## Coverage

- **Scanned**: architecture
- **Skipped**: code-quality, security, dependencies, performance, tests, ui (audit pilier unique, conformément à la demande)
