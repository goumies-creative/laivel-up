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

### Convention de nommage

**Identifiants du code en anglais, docstrings en français.**

| Élément | Langue |
|---------|--------|
| Noms de variables/fonctions/classes | EN |
| Docstrings | FR |
| Messages d'erreur | EN |
| Commentaires | FR |
| Noms de fichiers | EN |
| Contenu visible (CLI) | FR |

Raisons : pas de switching mental à la lecture, convention open-source, signature La Décodeuse.

### Tests

- **Coverage minimale** : 80% globale, 100% pour `scoring.py`
- **Tests sécurité** : `pytest tests/security/` — répertoire dédié
- **Property-based** : tests hypothesis pour les invariantes
- **Snapshot** : sorties CLI capturées et vérifiées
- **CI matrix** : tests sur Ubuntu, Windows, macOS × Python 3.11, 3.12, 3.13
- **Baseline bandit** : versionné dans `tests/security/bandit-baseline.json`

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

## Profils officiels

Les profils bruts (dossier `../laivel-up/profiles`) doivent être convertis
avant usage :

```bash
# Extraire et standardiser les profils
python scripts/extract_official_profile.py --source ../laivel-up/profiles

# Vérifier la calibration
python scripts/calibrate.py --expected grille/profils-officiels/expected.json --diff
```

> ⚠️ Ne jamais évaluer un fichier non standardisé. Voir `docs/GRID_QUICKREF.md`
> pour le mapping complet des champs.

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

## Release Process

### Prérequis

1. **PyPI token** : compte PyPI → API tokens → Create token → scope "Project: laivel-up"
2. **GitHub secret** : repo Settings → Secrets → Actions → `PYPI_API_TOKEN` = `pypi-...`
3. **CHANGELOG.md** : documenter les changements dans la section `[version]`

### Bumper la version

```bash
# SemVer strict : patch, minor, major
python scripts/version_bump.py patch   # 0.1.0 → 0.1.1
python scripts/version_bump.py minor   # 0.1.1 → 0.2.0
python scripts/version_bump.py major   # 0.2.0 → 1.0.0
```

Le script :
1. Met à jour `version` dans `pyproject.toml`
2. Met à jour `__version__` dans `src/laivelup/__init__.py`
3. Crée un commit `chore(release): vX.Y.Z`
4. Crée un tag `vX.Y.Z`
5. Push (si `--push`)

### Lancer la release

```bash
# Push le tag pour déclencher le workflow
git push origin main --tags
```

Le workflow `.github/workflows/release.yml` :
1. Build le package (whl + tar.gz)
2. Test l'installation sur 3OS × 3Python
3. Publish sur PyPI
4. Crée une GitHub Release avec les notes du CHANGELOG

### Vérification post-release

```bash
# Vérifier PyPI
pip install laivelup==X.Y.Z

# Vérifier GitHub Release
gh release view vX.Y.Z -R goumies-creative/laivel-up
```

## Code de conduite

Respectueux, inclusif, bienveillant. Pas de jugement sur les personnes,
seulement sur les traces techniques observables.