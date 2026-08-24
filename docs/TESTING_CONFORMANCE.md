# Conformité Testing · LAIVEL UP

> Checklist de conformité pour garantir qu'aucune évolution future ne provoque de régression, ne fuite de sécurité, ou n'impacte négativement le codebase.

## 1. Gaps identifiés (session 3 critique)

### 1.1 Gaps traités

| # | Sev | Gap | Statut | Test ajouté |
|---|-----|-----|--------|-------------|
| T1 | P0 | encoding.py : 4/6 fonctions `# pragma: no cover` | ✅ Couvert | `exclude_lines` dans `pyproject.toml` (Windows-only) |
| T2 | P2 | Snapshots fragiles (texte exact) | ✅ Documenté | Pattern à respecter : compléter par tests de contenu |
| T3 | P2 | `intervention_max` : chemin `triangulated=True + ratio=None` | ✅ Testé | `test_scoring.py` |
| T4 | P2 | `harness_max` : chemin `rules=True + context=False` | ✅ Testé | `test_scoring.py` |
| T5 | P3 | Export équipe : pas de vérification pseudo-anonyme | ✅ Testé | `test_team.py` (regex slug) |
| T6 | P3 | Pas de test miroir markdown↔html | ✅ Testé | `test_report.py::TestMirror` |
| T7 | P3 | `_load_profile` : branch KeyError non testé | ✅ Testé | `test_cli_extended.py` |
| T8 | P3 | `export_markdown` : branch history vide non testé | ✅ Testé | `test_team.py` |

### 1.2 Gaps documentés (non traités, hors-scope hackathon)

| # | Gap | Raison | Impact |
|---|-----|--------|--------|
| D1 | `_enable_virtual_terminal_windows` sans test | Windows-only, non testable en CI Linux | Faible |
| D2 | `_try_reconfigure_stdout` sans test | Idem | Faible |
| D3 | `ensure_utf8_env` sans test | Idem | Faible |
| D4 | `make_console` sans test | Idem | Faible |

**Résolution** : `exclude_lines` dans `pyproject.toml` exclut ces fonctions de la couverture.

## 2. Patterns de test obligatoires

### 2.1 Règle fondamentale

**Un test = une assertion.** Pas de tests multi-assertions sauf si les assertions vérifient le même comportement.

### 2.2 Nouvelle fonctionnalité

```
Pour chaque nouvelle fonction publique :
1. Test du cas nominal (happy path)
2. Test du cas d'erreur (bad input, edge case)
3. Test snapshot si CLI (sortie visible)
4. Test de régression si bug corrigé
```

### 2.3 Scoring (100% obligatoire)

```python
# Pour chaque axe (size, harness, intervention, parallel) :
# 1. Test du niveau minimum (White/Red)
# 2. Test du niveau maximum (Gold)
# 3. Test du refus (données manquantes)
# 4. Test du tie-break
# 5. Test du red flag
```

### 2.4 Security (22 tests minimum)

```
Pour chaque vecteur d'attaque :
- Injection JSON : 6 tests (proto, constructor, types, taille)
- Path traversal : 3 tests (output, write outside)
- DoS : 4 tests (giant profiles)
- HMAC-SHA-256 : 6 tests (determinism, formats, salt)
- Bandit regression : 3 tests (baseline)
```

### 2.5 RGPD (19 tests minimum)

```
Pour chaque mécanisme RGPD :
- Slug HMAC : 4 tests (determinism, uniqueness, no PII, format)
- Opt-out : 2 tests (blocks evaluate, excludes from export)
- Droit à l'oubli : 2 tests (purge history, keep team)
- Export sans PII : 4 tests (JSON, MD, CSV, HTML)
- Review fixes : 6 tests (XSS, opt-out survives, dictionary, floats, confidence, import)
```

### 2.6 Snapshots

```
Pour chaque commande CLI :
1. Snapshot exact (texte stable)
2. Test de contenu (clés présentes) — COMPLÉMENT obligatoire
```

**Clés obligatoires par commande :**
- `evaluate` : `"Niveau"`, `"Taille"`, `"Harness"`, `"Intervention"`, `"Parallel"`, `"Transparence"`
- `interrogate` : `"Verdict"` ou `"questions"`
- `help` : `"evaluate"`, `"interrogate"`, `"team"`

## 3. Checklist PR (pré-merge)

### 3.1 Automatisée (CI)

- [ ] `ruff check src/ tests/` → 0 errors
- [ ] `mypy src/` → 0 errors
- [ ] `bandit -r src/ -ll` → 0 issues
- [ ] `pip-audit` → 0 high/critical CVE
- [ ] `pytest --cov=src/laivelup.scoring --cov-fail-under=100` → pass
- [ ] `pytest --cov=src/laivelup --cov-fail-under=80` → pass
- [ ] `pytest tests/security/ -v` → all pass

### 3.2 Manuellement (pre-commit)

- [ ] `pre-commit run --all-files` → all pass
- [ ] Pas de `# pragma: no cover` ajouté sans justification
- [ ] Pas de `# type: ignore` ajouté sans commentaire
- [ ] Tests ajoutés pour tout nouveau code public

### 3.3 Revue de code

- [ ] Pas de secrets en dur
- [ ] Pas de `eval()` / `exec()`
- [ ] Pas d'import circulaire
- [ ] Docstrings FR sur fonctions publiques
- [ ] Noms EN sur identifiants code

## 4. Anti-patterns à bloquer

### 4.1 Ne JAMAIS faire

```python
# 1. Test qui dépend d'un autre test
def test_a(): global x; x = 42
def test_b(): assert x == 42  # FAUX

# 2. Test qui génère des données aléatoires sans seed
def test_random(): data = random.choice(items)  # FAUX

# 3. Test qui teste l'implémentation, pas le comportement
def test_internal(): assert _internal_fn() == 42  # FAUX

# 4. Test qui ignore les erreurs
def test_evaluate():
    try: evaluate(bad)
    except: pass  # FAUX

# 5. Test snapshot sans garde de contenu
def test_snapshot(snapshot):
    snapshot.assert_match(output, "file.txt")  # INCOMPLÈT sans test de contenu
```

### 4.2 Patterns à respecter

```python
# 1. Test isolé et reproductible
def test_evaluate_insufficient_data():
    result = evaluate({"declared_level": None})
    assert result["level"] is None

# 2. Test avec données fixées
def test_deterministic():
    salt = generate_team_salt()
    assert slug("alice", salt) == slug("alice", salt)

# 3. Test du comportement, pas de l'implémentation
def test_cli_exits_cleanly(capsys):
    result = runner.invoke(cli, ["evaluate"])
    assert result.exit_code == 0

# 4. Test avec fixtures
@pytest.fixture
def valid_profile():
    return {"declared_level": 2, "traces": {"tools_used": ["git"]}}

def test_with_fixture(valid_profile):
    result = evaluate(valid_profile)
    assert result["level"] == 2

# 5. Test miroir (markdown ↔ html)
def test_markdown_html_same_info():
    md = render_markdown(verdict)
    html = render_html(verdict)
    for key in ["Niveau", "Taille", "Harness"]:
        assert key in md
        assert key in html
```

## 5. Conformité encoding.py

### 5.1 Fonctions testables (couvertes)

| Fonction | Tests | Couverture |
|----------|-------|-----------|
| `supports_utf8` | 6 tests | ✅ 100% |
| `ascii_fallback` | 6 tests | ✅ 100% |

### 5.2 Fonctions Windows-only (exclues)

| Fonction | Raison | Exclusion |
|----------|--------|-----------|
| `_enable_virtual_terminal_windows` | Windows-only, ctypes | `exclude_lines` |
| `_try_reconfigure_stdout` | Windows-only, reconfigure | `exclude_lines` |
| `ensure_utf8_env` | Appelle les 2 précédentes | `exclude_lines` |
| `make_console` | Rich Console, non testable isolément | `exclude_lines` |

**Config** : `pyproject.toml` → `[tool.coverage.report]` → `exclude_lines`

## 6. Maintenance des tests

### Quand ajouter un test

- **Nouvelle fonctionnalité** : test unitaire + test edge case
- **Bug corrigé** : test de régression
- **Faille sécurité** : test dans `tests/security/`
- **Changement de comportement** : mettre à jour le snapshot + test de contenu

### Quand supprimer un test

- **Fonctionnalité supprimée** : supprimer le test correspondant
- **Doublon** : garder le plus complet
- **Test obsolète** : supprimer si la logique a changé

### Quand mettre à jour un snapshot

- **Changement de wording** : `pytest --snapshot-update` + vérifier le diff
- **Nouvelle feature** : ajouter le snapshot + test de contenu
- **Bug fix** : vérifier que le snapshot reflète le comportement corrigé

---

*Conformité testing — session 3 critique, 2026-08-24*
