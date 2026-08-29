---
artifact_contract: ce-unified-plan/v1
artifact_readiness: implementation-ready
product_contract_source: ce-brainstorm
date: 2026-08-22
status: confirmed
execution: code
---

# Plan B Calibration Degraded — Implementation Plan

## Goal Capsule

**Objective:** Résoudre le gap entre les seuils hardcoded de `scoring.py` et les scripts Plan B qui les référencent, en extrayant les constantes en dict structuré et en adaptant les scripts pour supporter les modes diagnostic/apply.

**Product authority:** LAIVEL UP hackathon repo (goumies-creative/laivel-up), deadline 31/08 12h.

**Open blockers:** Aucun.

**Product Contract preservation:** Unchanged.

---

## Implementation Units

### IU1 — SCORING_DEFAULTS extraction (R1, R2)

**Fichiers:** `src/laivelup/scoring.py`

**Constantes à extraire:**
- CONFIDENCE_THRESHOLD (0.5)
- CONFIDENCE_PEAK (0.9)
- CONFIDENCE_MEDIUM (0.8)
- CONFIDENCE_LOW (0.4)
- CONFIDENCE_HARNESS_ONLY (0.7)
- RETRIES_PER_LEVEL (dict gold/copper_or_green/blue)
- SIZE_LEVEL (dict S/M/L/XL → Level.RED/BLUE/GOLD)

**Tests:** `tests/test_scoring_defaults.py` — 5 tests (existence, valeurs, types, evaluate identique)

---

### IU2 — calibrate_degraded.py modes (R3, R4, R5)

**Fichiers:** `scripts/calibrate_degraded.py`

**Modifications:**
- Import SCORING_DEFAULTS depuis scoring.py
- Ajouter --strict flag (argparse)
- Mode graceful: try/except par profil + log
- Mode strict: raise sur premier invalide

**Tests:** +3 tests (strict, graceful, reads defaults)

---

### IU3 — apply_calibration_fix.py modes (R6, R7, R8)

**Fichiers:** `scripts/apply_calibration_fix.py`

**Modifications:**
- --thresholds option (chemin JSON seuils attendus)
- Logique patch SCORING_DEFAULTS en place
- --dry-run par défaut, --apply pour exécuter

**Tests:** Nouveau `tests/test_apply_calibration_fix.py` — 6 tests

---

### IU4 — release_hackathon.sh complet (R9, R10)

**Fichiers:** `scripts/release_hackathon.sh`

**Modifications:**
- Vérification gh CLI installé
- Vérification CI verte via gh run list
- gh release create avec notes
- Résumé clair par étape

---

### IU5 — Tests (R11, R12, R13)

**Tests à ajouter:**
- test_scoring_defaults.py: 5 tests
- test_calibrate_degraded.py: +3 tests
- test_apply_calibration_fix.py: 6 tests

---

### IU6 — CI update (R14)

**Fichiers:** `.github/workflows/ci.yml`

**Modification:** Job calibrate-degraded déjà ajouté. Vérifier upload artifact.

---

## Execution Sequence

1. IU1 (SCORING_DEFAULTS) — PRIORITÉ, tout dépend de là
2. IU5 (tests scoring defaults) — validation IU1
3. IU2 (calibrate_degraded modes) — dépend IU1
4. IU3 (apply_calibration_fix modes) — dépend IU1
5. IU4 (release script) — indépendant
6. IU6 (CI) — déjà fait, vérifier
7. Commit + push + rituel

## Risks

- SIZE_LEVEL doit mapper vers Level enum, pas des strings
- apply_calibration_fix.py doit lire/écrire le source Python correctement
- Release script nécessite gh CLI installé localement
