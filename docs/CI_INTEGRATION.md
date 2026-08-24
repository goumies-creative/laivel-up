# Intégration CI/CD (GitHub Actions)

LAIVEL UP peut évaluer automatiquement le niveau AIDD des développeurs à chaque PR.

## Setup rapide

1. **Copier le workflow** dans votre repo :
```bash
cp .github/workflows/aidd-eval.yml /chemin/vers/votre-repo/.github/workflows/
```

2. **Copier les scripts** :
```bash
cp scripts/generate_profile.py scripts/ci_evaluate.py /chemin/vers/votre-repo/scripts/
```

3. **Installer la dépendance** :
```bash
pip install laivelup
```

4. **Push et créer une PR** → le workflow se déclenche automatiquement.

## Fonctionnement

### Déclenchement

| Événement | Comportement |
|-----------|--------------|
| `pull_request` (opened, synchronize) | Évalue l'auteur de la PR |
| `workflow_dispatch` | Évalue un utilisateur spécifique (input) |

### Workflows

| Workflow | Déclenchement | Contenu |
|----------|---------------|---------|
| `aidd-eval.yml` | PR (opened, synchronize) | Évaluation AIDD automatique |
| `pr-quality-gate.yml` | PR (vers main) | Quality gate : ruff + mypy + bandit + coverage |
| `ci.yml` | Push + PR | CI matrix 3OS × 3Python |
| `release.yml` | Tag v* | Build + PyPI + GitHub Release |

### Permissions requises

```yaml
permissions:
  contents: read          # Lire le code
  pull-requests: write    # Poster le commentaire
```

### Étapes du workflow

1. **Checkout** : Clone le repo avec historique complet (`fetch-depth: 0`)
2. **Python** : Installe Python 3.11
3. **Dependencies** : `pip install -e .`
4. **Auteur** : Détecte l'auteur (PR ou input manuel)
5. **Profil** : Génère le profil via `generate_profile.py`
6. **Évaluation** : Évalue le niveau AIDD via `ci_evaluate.py`
7. **Commentaire** : Poste le verdict sur la PR
8. **Artifacts** : Sauve `profile.json` et `verdict.md` (30 jours)

## Personnalisation

### Modifier les seuils de PR sizes

Dans `scripts/generate_profile.py`, adapter la fonction `_detect_pr_sizes()` :

```python
if total <= 3:      # Seuil S
    sizes.append("S")
elif total <= 10:   # Seuil M
    sizes.append("M")
elif total <= 30:   # Seuil L
    sizes.append("L")
else:               # Seuil XL
    sizes.append("XL")
```

### Ajouter des fichiers de contexte

Dans `_detect_context_versioned()` :

```python
context_files = [
    "CLAUDE.md", "AGENTS.md", ".cursorrules",
    # Ajouter vos fichiers ici
]
```

### Exécuter manuellement

```bash
# Via GitHub UI
Actions → AIDD Evaluation → Run workflow → entrer le handle

# Via CLI (gh)
gh workflow run aidd-eval.yml -f user=alice
```

## Sortie

Le workflow génère deux artefacts :

### `verdict.md` (commentaire PR)

```markdown
## Évaluation AIDD · LAIVEL UP

Niveau : 🔹 Blue
Axe plancher : size

| Axe | Niveau | Confiance |
|-----|--------|-----------|
| Taille | 🔹 Blue | 80% |
| Harness | 🔺 Red | 70% |
| Intervention | 🥇 Gold | 80% |
| En parallèle | 🟢 Green | 80% |
```

### `profile.json` (profil complet)

Le profil JSON complet avec toutes les traces extraites.

## Limites connues

- **PR sizes** : Basé sur le nombre de fichiers (pas lignes). Moins précis que l'API GitHub.
- **Repos très petits** : Si < 5 merges, les données sont insuffisantes pour trancher.
- **Forks** : Le workflow analyse le repo cloné, pas les forks distants.
- **Rate limit** : Pas de problème (pas d'API GitHub utilisée en local).

## Dépannage

### "Refus de trancher (données insuffisantes)"

Le profil généré n'a pas assez de données. Vérifier :
- L'utilisateur a des merges dans le repo
- Le repo a un historique suffisant (> 5 commits)

### "Profil invalide"

Le schéma de validation a échoué. Vérifier la sortie de `generate_profile.py --verbose`.

### Workflow ne se déclenche pas

Vérifier les permissions du token GitHub :
- `contents: read`
- `pull-requests: write`

## Roadmap

### Post-Hackathon

- **GitHub API GraphQL** : Extraction précise via API (additions/deletions, workflow runs)
- **Cache** : Éviter les appels API répétés
- **Multi-utilisateurs** : Évaluer toute l'équipe d'un coup
- **Webhooks** : Auto-éval sur push (pas seulement PR)
