# Stratégie de Tests · LAIVEL UP

> Stratégie de test pour un outil CLI d'évaluation AIDD — garantir fiabilité, sécurité, et reproductibilité.

## 1. Classification des tests

| Catégorie | Répertoire | Exigence | Outil |
|-----------|------------|----------|-------|
| Unitaires | `tests/` | 80% couverture globale | pytest + coverage |
| Sécurité | `tests/security/` | Tous passent | pytest + bandit |
| Property-based | `tests/` | Invariantes fondamentaux | hypothesis |
| Snapshot | `tests/` | Sorties CLI stables | pytest-snapshot |
| Regression | `tests/` | Scoring = 100% | pytest-cov |

## 2. Hiérarchie de couverture

```
scoring.py     → 100%  (cœur métier — zéro compromis)
model.py       → 95%+  (structurant)
team.py        → 95%+  (RGPD, partage)
report.py      → 85%+  (sorties)
cli.py         → 80%+  (chemins principaux)
encoding.py    → 80%+  (cross-platform)
schema.py      → 80%+  (validation)
```

**Règle** : scoring.py ne peut jamais être en dessous de 100%. Les autres modules visent 80% minimum.

## 3. Tests unitaires

### Principes

- **Un test = une assertion** : chaque test vérifie UNE chose
- **Isolation** : pas de dépendance entre tests
- **Reproductibilité** : mêmes entrées → mêmes sorties (seed hypothesis固定的)
- **Nommage** : `test_<ce_qu'on_teste>_<ce_qu'on_s attend>`

### Exemples de tests critiques

```python
def test_score_abstains_on_insufficient_data():
    """La Décodeuse refuse quand les données manquent."""
    result = evaluate(giant_profile)
    assert result["level"] is None

def test_slug_uses_hmac_sha256_not_md5():
    """RGPD : HMAC-SHA-256 obligatoire, jamais MD5."""
    assert "hmac" in inspect.getsource(slug)
    assert "sha256" in inspect.getsource(slug)

def test_parallel_max_cannot_be_zero():
    """Divide-by-zero : parallel_max doit être > 0."""
    assert profile.parallel_max >= 1
```

## 4. Tests property-based (Hypothesis)

### Invariantes fondamentaux

```python
from hypothesis import given, strategies as st

@given(st.dictionaries(st.text(), st.text()))
def test_evaluate_never_crashes(profile):
    """Evaluate ne doit jamais crasher quelle que soit l'entrée."""
    result = evaluate(profile)
    assert "level" in result

@given(st.text(min_size=1))
def test_slug_is_always_valid(name):
    """Le slug doit toujours être un identifiant valide."""
    s = slug(name, generate_team_salt())
    assert len(s) <= 40
    assert "-" in s
```

### Stratégies custom

```python
# Profils valides aléatoires
valid_profile = st.fixed_dictionaries({
    "declared_level": st.integers(min_value=1, max_value=4),
    "traces": st.fixed_dictionaries({
        "tools_used": st.lists(st.text(min_size=1), max_size=10),
        "parallel_projects": st.integers(min_value=0, max_value=50),
    })
})
```

## 5. Tests snapshot

### Utilisation

```python
def test_evaluate_basic_snapshot(snapshot):
    """Sortie stable pour un profil basique."""
    result = evaluate(basic_profile)
    snapshot.assert_match(json.dumps(result, indent=2), "basic_profile.json")
```

### Normalisation

Le `_normalize()` dans les tests strip les codes ANSI et normalise les espaces :

```python
def _normalize(text: str) -> str:
    """Supprime les codes ANSI et normalise les espaces."""
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    text = ansi_escape.sub('', text)
    return re.sub(r'\s+', ' ', text).strip()
```

## 6. Tests de sécurité

### Répertoire `tests/security/`

| Fichier | Tests | Couvre |
|---------|-------|--------|
| `test_json_injection.py` | 6 | Injection via JSON malveillant |
| `test_path_traversal.py` | 3 | Manipulation de chemins |
| `test_dos_profil_giant.py` | 4 | Profils géants (>1MB) |
| `test_sha256_anonymization.py` | 6 | RGPD HMAC-SHA-256 + salt |
| `test_bandit_regression.py` | 3 | Pas de nouvelles failles |

### Répertoire `tests/` — Tests RGPD (session 3)

| Fichier | Tests | Couvre |
|---------|-------|--------|
| `test_team_rgpd.py` | 19 | HMAC salt, XSS escape, confidence, opt-out, team name validation |
| `test_scoring.py` (+2) | 2 | float("inf") rejection, non-integer float rejection |

### Pre-commit hooks (sécurité)

Les tests security sont inclus dans le hook `pytest-fast` de pre-commit :
```yaml
- id: pytest-fast
  entry: pytest -q -x --ignore=tests/fixtures/ --ignore=tests/test_calibrate.py
```

Cela garantit qu'aucune faille sécurité n'est introduite localement avant le commit.

### Baseline bandit

```bash
# Générer la baseline
python -m bandit -r src/ -f json > tests/security/bandit-baseline.json

# Vérifier pas de régression
pytest tests/security/test_bandit_regression.py
```

## 7. Tests CLI (end-to-end)

### Commandes testées

```bash
# Aide
laivelup --help
laivelup evaluate --help
laivelup team --help

# Évaluation basique
echo '{"declared_level": 2}' | laivelup evaluate
laivelup evaluate --profile valid.json

# Team tracker
laivelup team create --name "Alpha" --members "alice,bob"
```

### CI Matrix

| OS | Python | Statut |
|----|--------|--------|
| Ubuntu | 3.11 | ✅ |
| Ubuntu | 3.12 | ✅ |
| Ubuntu | 3.13 | ✅ |
| Windows | 3.11 | ✅ |
| Windows | 3.12 | ✅ |
| Windows | 3.13 | ✅ |
| macOS | 3.11 | ✅ |
| macOS | 3.12 | ✅ |
| macOS | 3.13 | ✅ |

## 8. Anti-patterns à éviter

### ✗ Ne pas faire

```python
# 1. Test qui depend d'un autre test
def test_a():
    global shared_state
    shared_state = 42

def test_b():
    assert shared_state == 42  # FAUX : depend de test_a

# 2. Test qui genere des donnees aleatoires sans seed
def test_random():
    data = random.choice(items)  # FAUX : non reproductible

# 3. Test qui teste l'implementation, pas le comportement
def test_internal_function():
    assert _internal_fn() == 42  # FAUX : teste l'implementation

# 4. Test qui ignore les erreurs
def test_evaluate():
    try:
        evaluate(bad_profile)
    except Exception:
        pass  # FAUX : on ignore l'erreur
```

### ✓ Bonnes pratiques

```python
# 1. Test isole et reproductible
def test_evaluate_insufficient_data():
    result = evaluate({"declared_level": None})
    assert result["level"] is None  # Comportement attendu

# 2. Test avec donnees fixees
def test_deterministic():
    salt = generate_team_salt()
    assert slug("alice", salt) == slug("alice", salt)  # Toujours pareil

# 3. Test du comportement, pas de l'implementation
def test_cli_exits_cleanly(capsys):
    result = runner.invoke(cli, ["evaluate"])
    assert result.exit_code == 0  # Sortie propre

# 4. Test avec fixtures
@pytest.fixture
def valid_profile():
    return {"declared_level": 2, "traces": {"tools_used": ["git"]}}

def test_with_fixture(valid_profile):
    result = evaluate(valid_profile)
    assert result["level"] == 2
```

## 9. Exécution des tests

### Commandes

```bash
# Tous les tests
pytest -q

# Avec couverture
pytest --cov=src/laivelup --cov-report=term-missing

# Tests de sécurité uniquement
pytest tests/security/ -v

# Tests property-based (plus long)
pytest --hypothesis-seed=0 tests/

# Tests snapshot (mise à jour)
pytest --snapshot-update
```

### Seuils

| Métrique | Seuil | Action |
|----------|-------|--------|
| Couverture globale | ≥ 80% | Bloque le merge |
| scoring.py | = 100% | Bloque le merge |
| Tests sécurité | 100% passent | Bloque le merge |
| Ruff errors | 0 | Bloque le merge |
| Mypy errors | 0 | Bloque le merge |

## 10. Maintenance des tests

### Quand ajouter un test

- **Nouvelle fonctionnalité** : test unitaire + test edge case
- **Bug corrigé** : test de regression
- **Faille securite** : test dans `tests/security/`
- **Changement de comportement** : mettre à jour le snapshot

### Quand supprimer un test

- **Fonctionnalité supprimée** : supprimer le test correspondant
- **Doublon** : garder le plus complet
- **Test obsolète** : supprimer si la logique a changé

### Revue des tests

Les tests sont revues en même temps que le code :
- **Couverture** : vérifier que les nouveaux chemins sont testés
- **Clarté** : un test = une assertion
- **Vitesse** : les tests lents doivent être marqués `@pytest.mark.slow`

## 11. Pre-commit hooks

### Configuration

Le fichier `.pre-commit-config.yaml` définit 3 hooks :

| Hook | Outil | Contenu |
|------|-------|---------|
| `ruff` | ruff-pre-commit | Lint + formatage Python |
| `mypy` | mirrors-mypy | Vérification de types |
| `pytest-fast` | local | Tests rapides + security |

### Installation

```bash
# Installer pre-commit
pip install pre-commit

# Activer les hooks
pre-commit install

# Tester sur tous les fichiers
pre-commit run --all-files
```

### Usage

Les hooks s'exécutent automatiquement à chaque `git commit`. Pour ignorer temporairement :

```bash
# Passer le hook ruff
git commit --no-verify -m "WIP: ..."

# Exécuter manuellement
pre-commit run ruff --all-files
pre-commit run pytest-fast --all-files
```

### Obligation

- **Jusqu'au 31/08** (hackathon) : pre-commit obligatoire
- **Après le 31/08** : optionnel (recommandé)

### Conformité

Voir `docs/TESTING_CONFORMANCE.md` pour la checklist complète de conformité testing.
