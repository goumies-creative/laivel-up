---
artifact_contract: ce-unified-plan/v1
artifact_readiness: requirements-only
product_contract_source: ce-brainstorm
date: 2026-08-22
status: confirmed
execution: code
---

# Plan B Calibration Degraded — Requirements-Only Unified Plan

## Goal Capsule

**Objective:** Résoudre le gap entre les seuils hardcoded de `scoring.py` et les scripts Plan B qui les référencent, en extrayant les constantes en dict structuré et en adaptant les scripts pour supporter les modes diagnostic/apply.

**Product authority:** LAIVEL UP hackathon repo (goumies-creative/laivel-up), deadline 31/08 12h.

**Open blockers:** Aucun — toutes les décisions sont prises, scope confirmé.

---

## Product Contract

### Summary

Extraire les seuils hardcoded de `scoring.py` (RETRIES_PER_LEVEL, _SIZE_LEVEL, CONFIDENCE_THRESHOLD, CONFIDENCE_LOW) en dict `SCORING_DEFAULTS` modifiable. Adapter `calibrate_degraded.py` et `apply_calibration_fix.py` pour lire/patcher ce dict. Ajouter modes : diagnostic read-only + apply auto-patch + release complet avec CI check.

### Requirements

**Scoring config extraction**

- **R1** — `scoring.py` expose un dict `SCORING_DEFAULTS` contenant toutes les constantes de seuils (RETRIES_PER_LEVEL, _SIZE_LEVEL, CONFIDENCE_THRESHOLD, CONFIDENCE_LOW) modifiables par les scripts Plan B.
- **R2** — La logique de scoring existante utilise `SCORING_DEFAULTS` au lieu des valeurs hardcoded. Le comportement identique est préservé (aucun changement fonctionnel).

**Diagnostic degraded mode**

- **R3** — `calibrate_degraded.py` lit les valeurs actuelles de `SCORING_DEFAULTS` et les compare aux profils officiels. Sortie : JSON + table markdown par défaut, `--format json|table|markdown` pour switcher.
- **R4** — Le diagnostic produit un `diagnostic.json` avec : timestamp, axes, résultats par profil (declared, computed, axis_deltas, red_flags), summary (total_mismatch, blocking, recommended_action).
- **R5** — Mode `--strict` : fail fast sur profil invalide. Mode par défaut : graceful degradation (skip + log, continue sur profils restants).

**Apply calibration fix**

- **R6** — `apply_calibration_fix.py` lit `diagnostic.json` et patche `SCORING_DEFAULTS` dans `scoring.py` pour les scénarios A (patch seuils) et B (réécrire mapping).
- **R7** — `--dry-run` par défaut : affiche les changements sans les appliquer. `--apply` : applique réellement.
- **R8** — Source des seuils : auto-depuis-diagnostic par défaut, `--thresholds expected.json` en option pour fournir des seuils manuellement.

**Release automation**

- **R9** — `release_hackathon.sh` crée un tag git annoté, push le tag, crée une GitHub Release via `gh release create`, et vérifie que la CI est verte avant de procéder.
- **R10** — Le script affiche un résumé clair de chaque étape et s'arrête en cas d'erreur.

**Tests**

- **R11** — Tests existants (143+) continuent de passer. Nouveaux tests pour SCORING_DEFAULTS, diagnostic, apply, release.
- **R12** — `test_calibrate_degraded.py` : ≥6 tests (import, help, diagnose empty, diagnose with profiles, format table, format markdown).
- **R13** — `test_install_clean.py` : ≥2 tests (pip install, CLI help).

**CI/CD**

- **R14** — Job `calibrate-degraded` dans `ci.yml` : skip si `expected.json` absent, upload `diagnostic.json` comme artifact.

### Key Decisions

- **SCORING_DEFAULTS dans scoring.py** (pas fichier externe) : zéro dépendance supplémentaire, changement minimal, facile à reviewer.
- **Mode dual diagnostic/apply** : flexibilité maximale sous stress.
- **Release complet** : tag + push + GitHub Release + CI check — pas de demi-mesure le 31/08.
- **Graceful degradation par défaut** : un profil corrompu ne bloque pas les 3 autres.

### Scope Boundaries

**In scope :**
- Extraction SCORING_DEFAULTS dans scoring.py
- Adaptation calibrate_degraded.py (modes diagnostic + apply)
- Adaptation apply_calibration_fix.py (dry-run + apply)
- Release script complet
- Tests skeleton
- CI job calibrate-degraded

**Out of scope :**
- Modification de la logique de scoring (seuils seulement)
- Ajout de nouveaux axes d'évaluation
- Interface web ou API
- Tests de charge (Phase 3 du planning existant)
- Hooks/plugins (Phase 4 du planning existant)

### Acceptance Examples

**Exemple 1 — Diagnostic standard :**
```bash
python scripts/calibrate_degraded.py \
  --official-dir grille/profils-officiels/ \
  --expected grille/profils-officiels/expected.json \
  --output diagnostic.json
```
→ Produit `diagnostic.json` avec 4 profils analysés, deltas par axe, red flags.

**Exemple 2 — Apply scénario A :**
```bash
python scripts/apply_calibration_fix.py \
  --scenario A \
  --diagnostic diagnostic.json \
  --apply
```
→ Patche `SCORING_DEFAULTS` dans `scoring.py`, relance tests.

**Exemple 3 — Release :**
```bash
bash scripts/release_hackathon.sh 0.2.0-hackathon
```
→ Crée tag v0.2.0-hackathon, push, GitHub Release, vérifie CI.
