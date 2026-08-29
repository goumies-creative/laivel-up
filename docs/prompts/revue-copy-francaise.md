# Prompt de revue copy française — LAIVEL UP

> Utiliser avec Claude Desktop (compte gratuit). Copier-coller ce prompt
> dans une nouvelle session, puis fournir les fichiers à réviser.

---

## Contexte

LAIVEL UP est un CLI d'évaluation du niveau d'adoption de l'AI-Driven Development
des développeurs. Tous les textes affichés aux utilisateurs (CLI, rapports,
documentation) doivent être en **français correct, intelligible et accessible**.

## Règles de revue

### 1. Langue
- **Français correct** : pas de fautes d'orthographe, de grammaire ou de syntaxe
- **Pas de franglais** : remplacer les anglicismes par des équivalents français
  quand ils existent et sont compris (ex: "passer en revue"而非 "reviewer")
- **Pas de jargon technique inutile** : expliquer les termes techniques quand
  ils sont nécessaires

### 2. Inclusif
- **"des développeurs"** (masculin pluriel incluant) plutôt que "un développeur"
- Pas de double écriture ("développeuses et développeurs") sauf si le contexte
  l'exige explicitement

### 3. Terminologie cohérente
- **"niveau d'adoption de l'AIDD"** (pas "niveau AIDD")
- **"AI-Driven Development"** (pas "AIDD" dans les textes explicatifs)
- **"laivelup"** (pas "LAIVEL UP" dans le code, sauf dans les titres)

### 4. Interdits
- **Pas de "La Décodeuse"** dans la CLI ou les rapports
- **Pas de référence au repo du hackathon** ou au trailer officiel
- **Pas d'emojis** dans le code source (autorisés dans la doc Markdown)
- **Pas de points de suspension** après des phrases complètes

### 5. Accessibilité
- Phrases courtes (max 25 mots)
- Voix active
- Verbes à l'infinitif pour les instructions
- Structures simples (sujet-verbe-complément)

## Fichiers à réviser

Fournir les fichiers suivants un par un :

| Fichier | Priorité | Ce qu'on vérifie |
|---------|----------|------------------|
| `src/laivelup/cli.py` | HAUTE | Help texts, messages d'erreur, docstrings |
| `src/laivelup/scoring.py` | HAUTE | Messages progress_for_axis, next_steps |
| `src/laivelup/report.py` | MOYENNE | Labels rapports MD/HTML |
| `src/laivelup/team.py` | MOYENNE | Messages d'erreur |
| `README.md` | HAUTE | Sections visibles par les juges |
| `METHODE.md` | MOYENNE | Description de la méthode |
| `CONTRIBUTING.md` | BASSE | Guide contributeur |
| `scripts/demo.py` | HAUTE | Commentaires asciinema |

## Sortie attendue

Pour chaque fichier, produire un tableau :

| Ligne | Avant | Après | Raison |
|-------|-------|-------|--------|
| 71 | `Évaluation du niveau AIDD d'un développeur.` | `Évaluation du niveau d'adoption de l'AIDD des développeurs.` | Terminologie + inclusif |

Puis un résumé :
- **Nombre de corrections** appliquées
- **Fichiers modifiés**
- **Points d'attention** (si une reformulation est nécessaire pour le sens)

## Exemple de demande

```
Révise la copy française de src/laivelup/cli.py en appliquant les règles
du prompt de revue copy. Produis un tableau de corrections et un résumé.
```
