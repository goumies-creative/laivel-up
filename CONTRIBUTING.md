# Contribuer à LAIVEL UP

Merci de votre intérêt pour LAIVEL UP !

## Standards de qualité

Ce projet suit des standards élevés pour garantir la fiabilité et la sécurité :

### Code

- **Python 3.11+** : utilisation des type hints modernes (`X | None`, `list[str]`)
- **Ruff** : linting et formatage (`ruff check src/ tests/`)
- **Mypy** : vérification de types (`mypy src/`)
- **Bandit** : scan de sécurité (`bandit -r src/`)
- **Zéro warning** : aucun warning mypy ou ruff avant merge

### Tests

- **Coverage minimale** : tous les chemins critiques testés
- **Property-based** : tests hypothesis pour les invariantes
- **Snapshot** : sorties CLI capturées et vérifiées
- **CI matrix** : tests sur Ubuntu, Windows, macOS × Python 3.11, 3.12, 3.13

### Sécurité

- **MIT License** : en-tête copyright sur chaque fichier `.py`
- **Pas de secrets** : jamais de credentials en dur
- **SHA-256** : pour le pseudo-anonymisation (pas SHA-1)
- **pip-audit** : audit des dépendances en CI

## Développement local

```bash
# Cloner
git clone https://github.com/ai-driven-dev/laivel-up.git
cd laivel-up

# Installer en mode dev
pip install -e ".[dev]"

# Lancer les tests
pytest

# Linter
ruff check src/ tests/

# Type check
mypy src/

# Security scan
bandit -r src/
```

## Structure des commits

Format conventionnel :

```
<type>(<scope>): <description>

<corps optionnel>

<footer optionnel>
```

Types : `feat`, `fix`, `docs`, `test`, `refactor`, `ci`, `chore`

## Pull Requests

1. Fork et branche depuis `main`
2. Ajouter des tests pour toute nouvelle fonctionnalité
3. Passer tous les checks CI (ruff, mypy, bandit, tests)
4. Mettre à jour la documentation si nécessaire
5. Demander une review

## Code de conduite

Respectueux, inclusif, bienveillant. Pas de jugement sur les personnes,
seulement sur les traces techniques observables.