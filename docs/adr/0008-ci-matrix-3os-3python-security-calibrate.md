# ADR-0008 : CI Matrix — 3 OS × 3 Python, security + calibrate

**Status** : Accepted  
**Date** : 2026-08-18  
**Décideurs** : Romy Alula

## Contexte

CI/CD pour un outil cross-platform. Matrix de compatibilité.

## Décision

| Job | Contenu |
|-----|---------|
| **lint** | ruff + mypy (Ubuntu, Python 3.11) |
| **test** | Matrix : Ubuntu × Win × Mac × Py3.11/3.12/3.13 |
| **security** | bandit + pip-audit + `pytest tests/security/` |
| **install** | `pip install .` + verify CLI (3 OS) |
| **calibrate** | `scripts/calibrate.py` (skip si expected.json absent) |

## Conséquences

### Positives
- 9 combinaisons OS × Python testées
- Sécurité intégrée (bandit + pip-audit + tests sécurité)
- Calibration automatique post-28/08

### Négatives
- CI longue (~10 min) — acceptable pour hackathon

## Liens
- Code : `.github/workflows/ci.yml`
