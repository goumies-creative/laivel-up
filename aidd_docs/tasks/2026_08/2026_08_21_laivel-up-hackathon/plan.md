---
type: plan
date: 2026-08-21
status: in-progress
objective: >
  Construire le plan optimal pour le hackathon LAIVEL UP : CLI d'évaluation AIDD
  qui répond aux 4 critères du jury, documentation continue, qualité MIT, orchestration aidd-dev-00-sdlc.
spec_path: aidd_docs/tasks/2026_08/2026_08_21_laivel-up-hackathon/spec.md
reviewed_sha: null
---

# Plan — LAIVEL UP Hackathon Build

## Phase 0 — Infra pré-28/08 (8 commits)

| # | Fichiers | Validation |
|---|----------|------------|
| 0.1 | `schemas/profile.schema.json` | Structure JSON Schema v1 profil AIDD |
| 0.2 | `src/laivelup/schema.py` + intégration `_load_profile()` | Exit 2 sur JSON invalide |
| 0.3 | `scripts/calibrate.py` skeleton | Interface CLI prête |
| 0.4 | `grille/profils-officiels/expected.json.template` | Template 4 profils |
| 0.5 | `.github/workflows/ci.yml` + job `calibrate` | CI verte par défaut |
| 0.6 | `docs/GRID_QUICKREF.md` | Tableau grille → code |
| 0.7 | `scripts/calibrate.py` enrichi | Diff par axe + suggestions fix |
| 0.8 | `docs/QUICKSTART_JUDGES.md` | Commandes 1-ligne juges |

## Phase 1 — Calibration officielle 28/08 (4 commits)

| # | Fichiers | Validation |
|---|----------|------------|
| 1.1 | Copy 4 profils officiels → `grille/profils-officiels/` | Format vérifié |
| 1.2 | `grille/profils-officiels/expected.json` | Niveaux 4 profils remplis |
| 1.3 | CI job `calibrate` activé | CI verte |
| 1.4 | Fix scoring si décalage | Itératif jusqu'à vert |

## Phase 3 — Robustesse (4 commits)

| # | Fichiers | Validation |
|---|----------|------------|
| 3.1 | `tests/test_load.py` | 1k profils + équipe 50 < 5s |
| 3.2 | `tests/test_schema_compat.py` | Tous exemples valident |
| 3.3 | `scripts/benchmark.py` | p50/p95 artefacts CI |
| 3.4 | `pyproject.toml` → `per-file-ignores` | Ruff clean |

## Phase 2 — Demo + Archi + Extending (4 commits)

| # | Fichiers | Validation |
|---|----------|------------|
| 2.1 | `scripts/demo.py` | Scénario 2 min scripté |
| 2.2 | `docs/architecture.mmd` | Mermaid complet |
| 2.3 | `docs/EXTENDING.md` | Guide contribution |
| 2.4 | `examples/run_all_examples.sh` | Tous cas de figure |

## Phase 4 — Hooks/Plugins (3 commits, optionnel)

| # | Fichiers | Validation |
|---|----------|------------|
| 4.1 | `src/laivelup/hooks.py` | Protocol EvaluatorHook |
| 4.2 | `src/laivelup/plugins.py` | entry_points discovery |
| 4.3 | `examples/custom-axis-risk/` | Plugin axe "Risque" |

## Phase 5 — Release Automation (3 commits)

| # | Fichiers | Validation |
|---|----------|------------|
| 5.1 | `.github/workflows/release.yml` | Tag v* → PyPI + GH Release |
| 5.2 | `CHANGELOG.md` | Keep a Changelog auto |
| 5.3 | `scripts/version_bump.py` | Bump cohérent |

## Phase 6 — Final Polish + Vidéo (4 commits)

| # | Fichiers | Validation |
|---|----------|------------|
| 6.1 | `README.md` → "Pour les juges" | Onboarding juges |
| 6.2 | `METHODE.md` → grille ↔ code | Traçabilité |
| 6.3 | Vidéo 2 min (asciinema + agg + Aegisub + Clipchamp) | Rendu validé |

## Références

| Document | Emplacement | Usage |
|----------|-------------|-------|
| `asciinema-cli-demo-workflow.md` | `docs/solutions/best-practices/` (workspace core) | Workflow complet enregistrement → GIF → MP4 → sous-titres |
| `GRID_QUICKREF.md` | `docs/` (projet laivel-up) | Mapping grille officielle → code ligne par ligne |
| `QUICKSTART_JUDGES.md` | `docs/` (projet laivel-up) | Commandes 1-ligne pour les juges |
| 6.4 | Tag `v0.2.0-hackathon` + push + formulaire | RENDU FINAL |

## Décisions

| Décision | Raison |
|----------|--------|
| Phase 3 (load tests) AVANT Phase 2 (demo) | Robustesse avant démo |
| Phase 4 (hooks) optionnelle | 2h d'investissement, gros signal communauté |
| Schema JSON Schema v1 | Validation stricte, fail fast |
| calibrate.py avec diff par axe | Réduit friction 28/08 à ~10 min |
| GRID_QUICKREF.md | Mapping grille → code ligne par ligne |
| Vidéo : asciinema + agg + Aegisub + Clipchamp | Gratuit, professionnel, pas de visage/voix |
| Guide workflow démo | `asciinema-cli-demo-workflow.md` dans best-practices workspace | Workflow complet : commands → .cast → .gif → .mp4 → sous-titres |
