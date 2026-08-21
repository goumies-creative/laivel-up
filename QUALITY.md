# Standards de Qualité · LAIVEL UP

> Exigences de qualité pour un projet CLI commercial-grade, MIT, production-ready.

## Exigences non-négociables

### 1. Sécurité

| Standard | Outil | Seuil |
|----------|-------|-------|
| Aucune faille haute/critique | bandit | 0 issues |
| Aucune CVE dans les deps directes | pip-audit | 0 high/critical |
| License MIT | LICENSE + headers | 100% fichiers .py |
| Pas de secrets en dur | bandit B105/B106 | 0 findings |
| SHA-256 pour hashing | hashlib | Pas de SHA-1 |

### 2. Qualité de code

| Standard | Outil | Seuil |
|----------|-------|-------|
| Aucune erreur de lint | ruff check | 0 errors |
| Aucune erreur de type | mypy --strict | 0 errors |
| Python 3.11+ | pyproject.toml | requires-python |
| Type hints sur toutes les fonctions publiques | mypy | 100% |

### 2.1 Convention de nommage FR→EN

**Identifiants du code en anglais, docstrings en français.**

| Élément | Langue | Raison |
|---------|--------|--------|
| Noms de variables/fonctions/classes | EN | Convention open-source, réduit le mapping mental à la lecture |
| Docstrings | FR | Signature La Décodeuse, accessible aux non-anglophones |
| Messages d'erreur | EN | Convention Python, interopérabilité |
| Commentaires | FR | Documentation interne, accessibilité |
| Noms de fichiers | EN | Convention universelle, pas d'accents dans les chemins |
| Contenu visible (CLI) | FR | UX pour l'utilisateur final |

**Avant/après (exemples LAIVEL UP) :**

```python
# ✗ Avant (FR) — switching mental à la lecture
taille_max(profile)
parallele_max(profile)
reprises_apres_coup

# ✓ Après (EN) — naturel en lecture code
size_max(profile)
parallel_max(profile)
retries_after_fact
```

**Bénéfices :**
- Pas de switching FR/EN quand on lit le code
- Convention respectée par les outils (ruff, mypy, IDE)
- Docstrings FR = signature La Décodeuse (pas de neurotype, pas de jargon technique)

### 3. Tests

| Standard | Outil | Couverture |
|----------|-------|-----------|
| Tests unitaires | pytest | Tous les chemins critiques |
| Tests property-based | hypothesis | Invariantes fondamentaux |
| Tests snapshot | pytest-snapshot | Sorties CLI stables |
| Tests team tracker | pytest | Module team complet |
| CI matrix | GitHub Actions | Ubuntu × Win × Mac × Py3.11/3.12/3.13 |

### 4. CI/CD

| Job | Contenu |
|-----|---------|
| lint | ruff + mypy |
| test | Matrix OS × Python |
| security | bandit + pip-audit |
| install | pip install + verify CLI |

### 5. Documentation

| Document | Contenu |
|----------|---------|
| README.md | Installation, usage rapide, commandes, structure |
| METHODE.md | Algorithme complet, grille, heuristiques |
| CONTRIBUTING.md | Standards, dev local, PR process |
| LICENSE | MIT complet |
| docs/asciinema-cli-demo-workflow.md | Workflow démo vidéo : asciinema → GIF → MP4 → sous-titres |

### 6. Installation

| Méthode | Commande |
|---------|----------|
| pip | `pip install laivelup` |
| pipx | `pipx install laivelup` |
| uv | `uv tool install laivelup` |
| Dev | `pip install -e ".[dev]"` |

## Méthodes signature intégrées

### La Décodeuse

- **Refus > deviner** : données insuffisantes → questions, pas de niveau arbitraire
- **Questions ciblées** : chaque refus génère des questions pour lever l'incertitude
- **Rotation anti-boucle** : pas de question déjà posée

### Human After All

- **Équité structurelle** : aucun neurotype demandé ni inféré
- **Pseudo-anonyme** : slug RGPD pour les rapports partagés
- **Pas de jugement personne** : seulement des traces observables
- **Accessibilité** : sortie par défaut lisible, technique en `--verbose`

## Vérification pré-merge

```bash
# 1. Tests
pytest -q  # 100% vert

# 2. Lint
ruff check src/ tests/  # 0 errors

# 3. Type check
mypy src/  # 0 errors

# 4. Security
bandit -r src/  # 0 issues
pip-audit  # 0 high/critical

# 5. Install
pip install . && laivelup --help
```