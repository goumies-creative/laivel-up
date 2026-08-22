# ADR-0004 : Grille d'évaluation — 4 axes, 7 niveaux, seuils confiance

**Status** : Accepted  
**Date** : 2026-08-15  
**Décideurs** : Romy Alula

## Contexte

Hackathon AIDD = évaluation du niveau d'adoption de l'IA dans le développement. Grille officielle à implémenter.

## Décision

| Axe | Description | Cellules |
|-----|-------------|----------|
| **Size** | Taille des features livrées | S→Red, M→Blue, L/XL→Gold |
| **Harness** | Outils d'ingénierie contextuelle | prompts→Red, context→Blue, +behavior→Green/Copper, +retry→Silver/Gold |
| **Intervention** | Fréquence des reprises après coup | majorité→Red, partie→Blue, étapes clés→Green/Copper, jamais→Silver/Gold |
| **Parallel** | Nombre de chantiers simultanés | 0→White, 1/2→Green, 3+→Copper/Gold |

**7 niveaux cumulatifs** : White(0), Red(1), Blue(2), Green(3), Copper(4), Silver(5), Gold(6)

**Règle AND** : un niveau n'est atteint que si tous ses axes le sont (min des maxima).

**Seuils confiance** :
- ≥0.5 : axe décidé
- <0.5 : refus de trancher (équité)
- Pic isolé : signalé en preuve, niveau sur l'habituel

## Conséquences

- `scoring.py` : 4 fonctions scorers, 1 evaluateur AND
- Refus > deviner : données insuffisantes → questions
- Équité : pas de verdict plus bas que les données prouvent

## Liens
- Code : `src/laivelup/scoring.py`
- Tests : `tests/test_scoring*.py`
- Doc : `METHODE.md`
