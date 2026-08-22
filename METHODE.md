# Méthode d'évaluation AIDD

> Document de référence pour l'algorithme d'évaluation LAIVEL UP.
> Aligné sur la grille officielle AI-Driven Dev.

## Vision

L'outil évalue le niveau d'adoption **AI-Driven Development** d'un développeur
en se basant sur des **traces observables** (pas sur ce que la personne dit de
soi). Il applique la méthode **La Décodeuse** : quand les données manquent ou
se contredisent, l'outil refuse de trancher et pose des questions ciblées plutôt
que de deviner.

## Grille d'évaluation

| Niveau | Size | Harness | Intervention | Parallel |
|--------|------|---------|-------------|----------|
| **White** | — | — | — | 0 projet |
| **Red** | S | Prompts | Majorité reprise | 1 projet |
| **Blue** | M | + Contexte | Partielle | 1 projet |
| **Green** | L | + Rules | Étapes clés | 1 projet |
| **Copper** | L-XL | + Rules | Étapes clés | 3 projets complétés |
| **Silver** | L-XL | + Loops | Jamais | 3 projets complétés |
| **Gold** | L-XL | + Loops + Agents | Jamais (autonomes) | 3 projets complétés |

## Algorithme

### 1. Normalisation du profil

Le profil d'entrée est validé et normalisé :

- `pr_sizes` : liste de tailles (S, M, L, XL)
- `context_versioned` : booléen (mémoire projet)
- `agent_rules_versioned` : booléen (règles agents)
- `retry_loops` : booléen (boucles de relance)
- `retries_after_fact` : ratio 0-1 (reprise après coup)
- `retries_triangulated` : booléen (triangulation)
- `parallel_projects` : entier ≥ 0
- `projects_completed` : entier ≥ 0
- `agents_autonomous` : booléen

**Règle** : si une valeur est invalide (booléen là où on attend un nombre, etc.),
l'outil retourne des erreurs et refuse de trancher.

### 2. Score par axe

Chaque axe est évalué indépendamment :

| Axe | Algorithme | Confiance |
|-----|-----------|-----------|
| **Size** | Taille la plus fréquente (dominante) | Croît avec le nombre de PR |
| **Harness** | Cumulatif : prompts → contexte → rules → loops | Fixe selon le palier |
| **Intervention** | Ratio de reprise vs seuils décroissants | Basse si non triangulé |
| **Parallel** | Nombre de projets et complétude | Basse si complétude inconnue |

### 3. Règle AND (min des maxima)

```python
global_level = min(score_taille, score_harness, score_intervention, score_parallel)
```

Un niveau n'est atteint que si **tous** les axes le sont. L'axe le plus faible
(« axe plancher ») détermine le niveau global.

### 4. Conditions de refus

L'outil refuse de trancher si :

- Une donnée est invalide (type incorrect, valeur hors limites)
- Un axe n'a pas de niveau déterminé (données manquantes)
- La confiance d'un axe est < 0.5
- Une égalité parfaite empêche d'identifier l'habituel

### 5. Questions de levée d'incertitude

Quand l'outil refuse, il génère des questions ciblées pour lever l'ambiguïté.
Ces questions sont reprises en mode `interrogate`.

## Heuristiques d'entretien (mode Décodeuse)

Le mode `interrogate` pose les questions du moteur et fusionne les réponses
libres dans les traces avant de re-scorer.

### Ratio de reprise

- « 60 % » → 0.6 (pourcentage)
- « 0.5 » → 0.5 (ratio brut, ne pas diviser par 100)
- « 0,5 » → 0.5 (virgule française acceptée)
- « 1 fois sur 2 » → 0.5 (fraction)
- « 150% » → 1.0 (borné à 1)
- Réponse sans chiffre → pas de mutation

### Tailles de PR

- Seules les majuscules (S, M, L, XL) sont reconnues
- « je l'utilise » ne crée PAS une fausse PR L (élision)
- Dé-duplication entre tours

### Niveau déclaré

- Détecté par mots entiers en français ou anglais
- « or » (conjonction) et « argent » (monnaie) sont exclus

### Chantiers

- Deux nombres : parallèle puis complétés
- « tous menés au bout » → même nombre que parallèle

## Équité structurelle

- **Jamais de verdict plus bas** que ce que les données prouvent
- **Valeur inconnue** → refus + question, pas de niveau arbitraire
- **Hyperfocus** : pic signalé en preuve, niveau reste sur l'habituel
- **White** : décidé par la grille (cellule « parallel = 0 »), jamais deviné
- **Neurotype** : jamais demandé, jamais inféré
- **Pseudo-anonyme** : slug RGPD pour les rapports partagés

## Traçabilité grille ↔ code

| Élément grille | Fichier | Fonction/Const | Ligne |
|----------------|---------|----------------|-------|
| Niveaux (White→Gold) | `model.py` | `Level` enum | 17-25 |
| Labels niveaux | `model.py` | `LEVEL_LABELS` | 27-35 |
| 4 axes | `model.py` | `AXES` | 37 |
| Labels axes | `model.py` | `AXIS_LABELS` | 40-45 |
| Règle AND | `scoring.py` | `evaluate()` | globale |
| Seuils confiance | `scoring_defaults.py` | `SCORING_DEFAULTS` | globale |
| Seuils taille (S/M/L/XL) | `scoring_defaults.py` | `SIZE_LEVEL` | dict |
| Retries par palier | `scoring_defaults.py` | `RETRIES_PER_LEVEL` | dict |
| Validation profil | `schema.py` | `validate_profile()` | globale |
| Rapport MD | `report.py` | `write_reports()` | globale |
| CLI | `cli.py` | `app` (Typer) | globale |

## Limites

- La séniorité n'est pas mesurée
- La qualité de code n'est pas évaluée
- Le neurotype n'est pas considéré
- Un niveau reflète une adoption observée, pas une valeur humaine