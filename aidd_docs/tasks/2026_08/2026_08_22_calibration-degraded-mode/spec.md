---
type: spec
date: 2026-08-22
status: approved
objective: >
  Implémenter le mode dégradé calibration (Plan B) pour LAIVEL UP :
  diagnostic structuré si calibrate.py échoue sur les profils officiels (28/08),
  avec 3 scénarios pré-décidés et scripts d'application automatique.
acceptance_criteria:
  - calibrate_degraded.py produit diagnostic.json avec axes, deltas, confiance
  - 3 scénarios (A: patch seuils, B: réécrire mapping, C: as-is) documentés
  - apply_calibration_fix.py applique scénario A ou B avec --dry-run
  - release_hackathon.sh automatise tag+push+formulaire
  - Tests skeleton validés (pytest vert)
  - CI job calibrate-degraded ajouté (skip si expected.json absent)
  - ADR-017 pré-rédigé dans docs/adr/
---

# Spec — Mode dégradé calibration (Plan B)

## Contexte

Le hackathon AI-Driven Dev (28-31/08/2026) publie 4 profils officiels le 28/08 à 12h.
`calibrate.py` compare les résultats du scoring contre des valeurs attendues.
Si la grille officielle a des axes, seuils ou poids différents, le calibration job CI échoue.
Pas de calibration = pas de validation = pas de démo crédible pour le jury.

## Objectif

Implémenter un mode dégradé qui permet de :
1. Diagnostiquer en < 10 min l'écart exact (mapping brut axe→valeur)
2. Choisir entre 3 scénarios d'action (patch seuils, réécrire mapping, livrer as-is)
3. Ne pas bloquer le reste du planning (load tests, demo, vidéo, release)

## Scope

| Composant | Fichier | Responsabilité |
|-----------|---------|----------------|
| Diagnostic | `scripts/calibrate_degraded.py` | Lit profils officiels, produit diagnostic.json |
| Décision | `docs/adr/0017-calibration-degraded-mode.md` | ADR pré-rédigé avec 3 scénarios |
| Exécution | `scripts/apply_calibration_fix.py` | Applique patch scoring (scénarios A/B) |
| Release | `scripts/release_hackathon.sh` | Release atomique tag+push+formulaire |
| Tests | `tests/test_calibrate_degraded.py` | Tests du diagnostic sur profils maison |
| Tests | `tests/test_install_clean.py` | Test install propre venv vierge |
| CI | `.github/workflows/ci.yml` (+job calibrate-degraded) | Job CI pour le diagnostic |

## Contraintes

- Délai : 28/08 12h publication → 31/08 12h deadline (72h)
- Pas de contact avec les organisateurs pour clarifier le format
- Le CLI doit rester fonctionnel même si calibration échoue
- Scripts en Python avec Typer/Rich (cohérent avec le CLI existant)

## Vérification

- `pytest tests/test_calibrate_degraded.py` vert
- `pytest tests/test_install_clean.py` vert
- `calibrate_degraded.py --help` fonctionne
- `apply_calibration_fix.py --help` fonctionne
- `release_hackathon.sh --help` fonctionne
- CI verte (calibrate-degraded job skip si expected.json absent)
