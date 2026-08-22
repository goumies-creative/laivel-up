# GRID_QUICKREF.md — Mapping grille officielle → code

> Référence rapide pour comprendre comment chaque cellule de la grille AIDD
> est implémentée dans le scoring LAIVEL UP.

## Axe Taille → `scoring.py :: size_max()`

| Cellule grille | Niveau max | Condition code |
|----------------|------------|----------------|
| S | RED | `pr_sizes` domine sur "S" |
| M | BLUE | `pr_sizes` domine sur "M" |
| L | GOLD | `pr_sizes` domine sur "L" |
| XL | GOLD | `pr_sizes` domine sur "XL" |

- **Pic isolé** : si la taille max est minoritaire (< 50%), signalé en `variance` mais le niveau reste sur l'habituel (taille la plus fréquente).
- **Égalité** : deux tailles à égalité → confiance basse → refus.

## Axe Harness → `scoring.py :: harness_max()`

| Cellule grille | Niveau max | Condition code |
|----------------|------------|----------------|
| rien | WHITE | aucun signal d'adoption |
| prompts | RED | `prompts` ou tout signal présent, pas de context |
| context engineering | BLUE | `context_versioned = True` |
| context + behavior | COPPER | `context_versioned + agent_rules_versioned` |
| context + behavior + boucles | GOLD | `context_versioned + agent_rules_versioned + retry_loops` |

- La distinction Silver/Gold ne relève pas du harness (elle est dans l'intervention).

## Axe Intervention → `scoring.py :: intervention_max()`

| Cellule grille | Niveau max | Condition code |
|----------------|------------|----------------|
| après coup, majorité | RED | `retries_after_fact > 0.5` |
| après coup, partie | BLUE | `retries_after_fact <= 0.5` |
| étapes clés | GREEN/COPPER | `retries_after_fact <= 0.2` |
| jamais | SILVER | `retries_after_fact <= 0.05` |
| jamais + agents autonomes | GOLD | `retries_after_fact <= 0.05 + agents_autonomous` |

- **Non triangulé** : `retries_triangulated = False` → confiance 0.4, sous le seuil → refus.

## Axe En parallèle → `scoring.py :: parallel_max()`

| Cellule grille | Niveau max | Condition code |
|----------------|------------|----------------|
| 0 | WHITE | `parallel_projects = 0` |
| 1-2 | GREEN | `parallel_projects < 3` |
| 3 + tous menés au bout | GOLD | `parallel_projects >= 3 + projects_completed >= 3` |
| 3 mais non confirmé | GREEN (faible) | `parallel_projects >= 3 + projects_completed = None` |

## Règle AND

Le niveau global est le **minimum** des niveaux de tous les axes.
Exemple : taille=Gold, harness=Blue, intervention=Red, parallel=Green → niveau Red (axe plancher).

## Fichiers clés

| Fichier | Rôle |
|---------|------|
| `src/laivelup/scoring.py` | Moteur d'évaluation (cellules + refus) |
| `src/laivelup/model.py` | `Level`, `AxisScore`, `Verdict`, `ProfileData` |
| `schemas/profile.schema.json` | Validation des profils JSON |
| `scripts/calibrate.py` | Comparaison verdicts vs attendus |
| `grille/aidd.md` | Grille officielle complète |
