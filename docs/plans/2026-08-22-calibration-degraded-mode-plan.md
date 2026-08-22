---
type: plan
date: 2026-08-22
status: in-progress
spec_path: aidd_docs/tasks/2026_08/2026_08_22_calibration-degraded-mode/spec.md
---

# Plan — Mode dégradé calibration (Plan B)

## Phase S1 — Scripts squelettes (2h)

| # | Fichiers | Validation |
|---|----------|------------|
| S1.1 | `scripts/calibrate_degraded.py` | `--help` + format table/markdown/json |
| S1.2 | `scripts/apply_calibration_fix.py` | `--help` + `--dry-run` par défaut |
| S1.3 | `scripts/release_hackathon.sh` | `--help` + dry-run tag |

## Phase S2 — Tests (1h)

| # | Fichiers | Validation |
|---|----------|------------|
| S2.1 | `tests/test_calibrate_degraded.py` | 6 tests skeleton |
| S2.2 | `tests/test_install_clean.py` | 3 tests skeleton |

## Phase S3 — Intégration CI (30 min)

| # | Fichiers | Validation |
|---|----------|------------|
| S3.1 | `.github/workflows/ci.yml` (+job calibrate-degraded) | CI verte |

## Phase S4 — Validation dry-run (30 min)

| # | Action | Validation |
|---|--------|------------|
| S4.1 | `python scripts/calibrate_degraded.py --official-dir exemples/ --expected grille/profils-officiels/expected.json --output diagnostic-dryrun.json --format table` | Sortie table lisible |
| S4.2 | `python scripts/apply_calibration_fix.py --scenario A --diagnostic diagnostic-dryrun.json --dry-run` | Pas d'erreur |

## Phase S5 — Commit + push (15 min)

| # | Action | Validation |
|---|--------|------------|
| S5.1 | Commit workspace core (solution + ADR + CONCEPTS + ONTOLOGY) | git status clean |
| S5.2 | Commit repo LAIVEL UP (spec + plan + scripts + tests + CI) | git status clean |
| S5.3 | Push both | CI verte |
