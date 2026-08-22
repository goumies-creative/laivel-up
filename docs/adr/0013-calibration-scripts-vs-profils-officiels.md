# ADR-0013 : Calibration — scripts/calibrate.py vs profils officiels

**Status** : Accepted  
**Date** : 2026-08-20  
**Décideurs** : Romy Alula

## Contexte

Vérifier que l'outil produit les bons résultats sur les profils officiels du hackathon.

## Décision

- **Script** : `scripts/calibrate.py` compare sorties vs `expected.json`
- **Profils officiels** : 4 profils publiés le 28/08 12h
- **CI** : job `calibrate` skip si expected.json absent
- **Modes** : `--diff` (afficher écarts), `--fix` (suggestions), `--template` (générer template)

## Conséquences

### Positives
- Calibration automatique
- Détection régression vs profils officiels

### Négatives
- Attente 28/08 pour expected.json

## Liens
- Code : `scripts/calibrate.py`
- CI : `.github/workflows/ci.yml`
