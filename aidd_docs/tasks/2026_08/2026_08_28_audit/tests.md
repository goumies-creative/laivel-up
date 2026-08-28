# Audit Tests Pillar — LAIVEL UP

**Date :** 2026-08-28
**Score global :** 7.5 / 10
**Couverture estimée :** ~88 % branch (threshold 85 % configuré)
**Nombre de tests :** ~230 (dont 10 property-based, 8 snapshot, 5 security subdirs)
**Stack test :** pytest 8+, hypothesis, pytest-snapshot, pytest-cov, bandit

---

## Résumé exécutif

La suite de tests est **solide et bien structurée** pour un projet hackathon. Le moteur `scoring.py` (cœur métier) est le mieux couvert avec un seuil 100 % branch configuré. Les tests RGPD/sécurité sont un vrai plus. Cependant, il existe des **zones d'ombre critiques** : les modes JSON/quiet du CLI, la couche `_filter_fields`, le trim historique team, et les edge cases de sérialisation JSON ne sont pas testés. Les property-based tests couvrent uniquement l'axe `pr_sizes`, ignorant les 3 autres axes et les traces booléennes.

---

## 1. Couverture critique par module

### 1.1 scoring.py (cible 100 %) — ✅ BON

**Couverture estimée :** ~98 %

Les 4 cellules (`size_max`, `harness_max`, `intervention_max`, `parallel_max`) sont testées via parametrize (7 niveaux) + edge cases. `normalize_profile` a 15+ tests d'erreur. `_as_float`/`_as_int` sont couverts.

| Severity | File:Line | Issue | Suggested Fix | Effort |
|----------|-----------|-------|---------------|--------|
| LOW | `src/laivelup/scoring.py:380-386` | Variance branch (`ratio < 0.5` dans `evaluate`) testée mais pas directement sur le ratio exact | Ajouter un test avec 5 PR (XL, S, S, S, S) pour vérifier que `variance` est set | XS |
| LOW | `src/laivelup/scoring.py:415-419` | Silver sans `agents_autonomous` → question bonus non testée en isolation | Test dédié vérifiant que `next_steps` contient la phrase "Silver" + "agents" | XS |

### 1.2 cli.py — ⚠️ GAPS DÉTECTÉS

**Couverture estimée :** ~82 %

| Severity | File:Line | Issue | Suggested Fix | Effort |
|----------|-----------|-------|---------------|--------|
| **HIGH** | `src/laivelup/cli.py:293-296` | `_filter_fields()` — aucune unit test directe | Ajouter `test_filter_fields` avec cas : champ présent, absent, multiple, chaîne vide | S |
| **HIGH** | `src/laivelup/cli.py:306-346` | Mode `--json`/`--quiet` — la sortie JSON n'est jamais vérifiée (structure, clés) | Ajouter test `--json` vérifiant `json.loads(r.output)` et présence de `level`, `axes`, `next_steps` | S |
| **HIGH** | `src/laivelup/cli.py:337-345` | `--fail-on` — exit code 1 non vérifié quand le niveau est inférieur | Ajouter test avec profil RED + `--fail-on GREEN` → exit 1 | S |
| MEDIUM | `src/laivelup/cli.py:169-172` | `--version` callback — testé en snapshot mais pas en assertions directes | Pas critique (snapshot le couvre), mais ajouter `assert '0.1.0' in r.output` | XS |
| MEDIUM | `src/laivelup/cli.py:82` | `MAX_JSON_MB = 2` — la borne exacte (2 MB) n'est pas testée, seulement "gros fichier" | Test avec fichier de 2.1 MB exact pour confirmer la limite | S |
| LOW | `src/laivelup/cli.py:541-553` | `_parse_retry_ratio` — pas de test pour les cas limite (0%, 100%, très grands nombres) | Ajouter `test_parse_zero_percent`, `test_parse_100_percent`, `test_parse_large_number` | XS |

### 1.3 team.py — ⚠️ TRIM HISTORIQUE NON TESTÉ

**Couverture estimée :** ~85 %

| Severity | File:Line | Issue | Suggested Fix | Effort |
|----------|-----------|-------|---------------|--------|
| **HIGH** | `src/laivelup/team.py:194-195` | `if len(team.history) > _MAX_HISTORY: team.history = team.history[-_MAX_HISTORY:]` — aucune unit test pour le trim à 100 entrées | Ajouter test : créer équipe, évaluer 101 fois, vérifier que `len(history) == 100` et que les anciennes entrées sont tronquées | S |
| MEDIUM | `src/laivelup/team.py:32-39` | `_validate_team_name` — non testée directement (seulement via CLI) | Tests unitaires : nom vide, chars spéciaux, 65 chars, underscore OK, tiret OK | S |
| MEDIUM | `src/laivelup/team.py:82-102` | `load_team` — le fallback `generate_team_salt()` quand `data.get('salt')` est absent n'est pas testé | Test avec JSON d'équipe sans clé `salt` → vérifier que le team est chargé avec un salt généré | XS |
| LOW | `src/laivelup/team.py:229-254` | `export_json` — le filtre `opt_out` dans `history` est testé mais le cas où un history entry n'a pas de clé `slug` ne l'est pas | Ajouter test avec history entry malformée (sans `slug`) | XS |

### 1.4 schema.py — ✅ BON

**Couverture estimée :** ~90 %

Le fallback `_validate_minimal` est bien testé. `validate_profile` (jsonschema) est testé via les fichiers exemples.

| Severity | File:Line | Issue | Suggested Fix | Effort |
|----------|-----------|-------|---------------|--------|
| MEDIUM | `src/laivelup/schema.py:38-41` | Le branch `except ImportError` (jsonschema absent) n'est pas testé | Mock `jsonschema` pour lever ImportError → vérifier que `_validate_minimal` est appelé | M |
| LOW | `src/laivelup/schema.py:54-110` | `_validate_minimal` — le cas `name`=None (pas une string) n'est pas testé | Ajouter test avec `'name': 123` | XS |

### 1.5 report.py — ✅ BON

**Couverture estimée :** ~88 %

`render_markdown` et `render_html` couvrent les branches decided/undecided/errors. `write_reports` testé avec et sans HTML.

| Severity | File:Line | Issue | Suggested Fix | Effort |
|----------|-----------|-------|---------------|--------|
| LOW | `src/laivelup/report.py:173-175` | `_slug` dans report.py est un wrapper — testé indirectement, pas en unit test | Suffisant car testé via `test_slug_in_filename` | XS |

### 1.6 model.py — ✅ PAS DE TESTS REQUIS

Dataclasses pures, pas de logique métier. Les tests des consommateurs (scoring, team) couvrent le comportement.

### 1.7 encoding.py — ✅ BON

**Couverture estimée :** ~85 %

`supports_utf8` et `ascii_fallback` testés sur 6 combinaisons de plateformes/encodages. Les fonctions Windows-only sont en `pragma: no cover`.

### 1.8 questions.py, scoring_defaults.py, utils.py — ✅ BON

Constantes et fonctions utilitaires bien couvertes par les tests des consommateurs.

---

## 2. Test Pyramid (balance unit / integration / E2E)

| Type | Nombre | % | Évaluation |
|------|--------|---|------------|
| **Unit** (scoring, model, schema, encoding, utils) | ~170 | 74 % | ✅ Bon ratio |
| **Integration** (CLI invoke, team ops, export) | ~50 | 22 % | ✅ Suffisant |
| **E2E** (install clean, demo, load) | ~10 | 4 % | ✅ Acceptable pour hackathon |

**Verdict :** La pyramide est saine. Le ratio unit > integration > E2E est respecté. Pas de sur-dépendance aux E2E.

---

## 3. Flakiness Risks

| Severity | File | Issue | Mitigation |
|----------|------|-------|------------|
| MEDIUM | `tests/test_load.py:27` | `time.perf_counter()` — le seuil 5s peut échouer sur CI lent | Le `LOAD_TEST_MAX_SECONDS` env var est déjà configurable ✅ |
| MEDIUM | `tests/test_bandit_regression.py:27-28` | `subprocess.run(['python', '-m', 'bandit', ...])` — dépend de bandit installé dans le venv | Le marker `@pytest.mark.security` permet de skipper |
| LOW | `tests/test_install_clean.py:22-24` | Test install dépend d'un venv propre, skipped sur Windows | Déjà géré par `@pytest.mark.skipif` |
| LOW | `tests/test_calibrate_degraded.py:139` | `Path('/tmp/test_sd')` — chemin hardcoded, pas `tmp_path` | Remplacer par `tmp_path` pour éviter les conflits |

---

## 4. Assertion Quality

| File | Pattern | Évaluation |
|------|---------|------------|
| `test_scoring.py:156` | `assert verdict.decided, f'devrait trancher : {verdict.next_steps}'` | ✅ Message d'erreur explicite |
| `test_cli.py:33` | `assert 'introuvable' in r.output.lower() or 'trouv' in r.output.lower()` | ⚠️ Le `or 'trouv'` est trop permissif |
| `test_team_rgpd.py:67` | `assert 'alice' not in slug.lower() or slug.startswith('alice')` | ⚠️ Le `or` rend le test inutile (commence toujours par alice) |
| `test_cli_extended.py:168` | `assert r.exit_code != 0` | ⚠️ Pas de message d'erreur, pas de vérification du code exact |
| `test_properties.py:93-94` | `assert 0.0 <= axis.confidence <= 1.0` avec message | ✅ Excellent |

---

## 5. Mock Usage

| Scope | Usage | Évaluation |
|-------|-------|------------|
| `test_interactive.py` | `monkeypatch.setattr(cli.Prompt, 'ask', ...)` | ✅ Approprié — simule l'input utilisateur |
| `test_encoding.py` | `patch.object(sys, 'stdout', ...)` | ✅ Nécessaire pour simuler stdout win32 |
| `test_calibrate.py` | `monkeypatch.setattr('calibrate.PROFILES_DIR', ...)` | ✅ Isole le filesystem |
| `test_demo.py` | `subprocess.run` sans mock | ✅ Teste le vrai script |

**Verdict :** Pas de sur-mock. Les mocks sont utilisés uniquement quand nécessaire (stdin, filesystem, plateforme).

---

## 6. Security Test Coverage

| Domaine | Test | Couvert |
|---------|------|---------|
| Path traversal | `test_path_traversal.py` (3 tests) | ✅ |
| JSON injection / `__proto__` | `test_json_injection.py` (6 tests) | ✅ |
| DoS (profil giant) | `test_dos_profil_giant.py` (4 tests) | ✅ |
| SHA-256 anonymization | `test_sha256_anonymization.py` (6 tests) | ✅ |
| Bandit regression | `test_bandit_regression.py` (3 tests) | ✅ |
| RGPD opt-out | `test_team_rgpd.py` (12 tests) | ✅ |
| XSS in export HTML | `test_team_rgpd.py:254-265` | ✅ |
| **SQL injection** | — | ❌ Non applicable (pas de SQL) |
| **SSRF** | — | ❌ Non applicable (pas de réseau) |
| **Injection dans les rapports MD/HTML** | Le `escape()` de `html` est utilisé | ✅ (testé via XSS test) |

---

## 7. Property-Based Tests (Hypothesis)

**Couverture :** ~10 strategies, 100 examples each

| Invariant | Stratégie | Évaluation |
|-----------|-----------|------------|
| Verdict toujours cohérent | `st_pr_sizes` | ⚠️ Couvre uniquement `pr_sizes` |
| Confiance 0-1 | `st_pr_sizes` | ⚠️ Même limitation |
| Next steps non vides | `st_pr_sizes` | ⚠️ Même limitation |
| Sans données → refuse | `st_pr_sizes` | ✅ |
| Ratio non triangulé → refuse | `st_ratio` | ✅ |
| Égalité tailles → refuse | `st_pr_size × 2` | ✅ |

**Gap critique :** Les property tests ne varient que `pr_sizes`. Ils ne testent pas les invariants avec des traces `context_versioned`, `retries_after_fact`, `parallel_projects`, etc. Un profil généré avec des booléens aléatoires + ratios aléatoires couvrirait bien plus de branches.

---

## 8. Missing Test Categories

| Catégorie | Présente | Notes |
|-----------|----------|-------|
| Unit tests | ✅ | Bien couvertes |
| Integration tests | ✅ | CLI invoke, team ops |
| E2E tests | ✅ | Install clean, demo |
| Snapshot tests | ✅ | 8 snapshots stables |
| Property-based tests | ⚠️ | Partielles (1 axe sur 4) |
| Security tests | ✅ | 5 sous-dossiers, 22 tests |
| Load/performance tests | ✅ | 2 tests (1k profils, 50 membres) |
| **Negative tests** | ⚠️ | Présentes mais pas systématiques |
| **Boundary tests** | ⚠️ | Borne MAX_JSON_MB testée indirectement |
| **Regression tests** | ✅ | Bandit baseline, maison profiles |
| **Chaos/adversarial tests** | ⚠️ | Injection JSON oui, mais pas de Unicode hostile |

---

## 9. Findings Critiques (Top 5)

### F1 : `_filter_fields` non testé
- **Severity :** HIGH
- **File :** `src/laivelup/cli.py:293-296`
- **Impact :** Le filtrage JSON (`--fields`) peut silencieusement omettre des données ou tout inclure
- **Fix :** 3 tests unitaires : champ existant, champ absent, multi-champs
- **Effort :** XS

### F2 : Mode `--json` sorti non vérifié
- **Severity :** HIGH
- **File :** `src/laivelup/cli.py:320-325`
- **Impact :** La structure JSON n'est pas validée — des consommateurs CI/agent peuvent casser
- **Fix :** Test avec `json.loads(r.output)` + vérification des clés `level`, `axes`, `next_steps`
- **Effort :** S

### F3 : `--fail-on` exit code non vérifié
- **Severity :** HIGH
- **File :** `src/laivelup/cli.py:337-345`
- **Impact :** La gate CI peut ne pas bloquer quand elle devrait
- **Fix :** Test profil RED + `--fail-on GREEN` → exit 1, profil BLUE + `--fail-on RED` → exit 0
- **Effort :** S

### F4 : Team history trim (100 entrées) non testé
- **Severity :** MEDIUM
- **File :** `src/laivelup/team.py:194-195`
- **Impact :** Le trim peut mal fonctionner sans qu'on le sache (perte de données historiques)
- **Fix :** Test bouclant 101 évaluations, vérifiant `len(history) == 100` et que les 100 plus récentes sont conservées
- **Effort :** S

### F5 : Property tests ne couvrent que 1 axe
- **Severity :** MEDIUM
- **File :** `tests/test_properties.py:73-144`
- **Impact :** Les invariants ne sont vérifiés que sur des profils avec `pr_sizes` variable, pas sur des profils complets
- **Fix :** Ajouter une stratégie `st_full_profile` générant des traces complètes (4 axes) et tester les invariants sur celle-ci
- **Effort :** M

---

## 10. Observations Positives

1. **Fixture conftest.py :** L'isolation du répertoire `.laivelup/teams/` via `monkeypatch` est un pattern excellent — aucun test ne pollue le filesystem réel
2. **Sécurité proactive :** Le dossier `tests/security/` avec 5 fichiers de test est rarement vu dans des projets hackathon
3. **Hypothesis :** L'utilisation de property-based testing montre une maturité au-dessus de la moyenne
4. **Snapshots :** Les 8 snapshots stabilisent le format de sortie CLI, utile pour les refactors
5. **Load tests :** Les tests de charge (1k profils, 50 membres) avec seuil configurable sont une bonne pratique
6. **Calibration tests :** Les scripts `calibrate.py` et `calibrate_degraded.py` sont bien testés, rare pour des outils internes
7. **RGPD :** Les tests d'opt-out, de droit à l'oubli, et de non-fuite PII dans les exports sont complets

---

## 11. Plan d'Action Recommandé

| Priorité | Action | Effort | Impact |
|----------|--------|--------|--------|
| P0 | Ajouter tests `_filter_fields` (3 tests) | XS | Couvre gap critique |
| P0 | Ajouter test `--json` mode (vérifier structure) | S | Protège les consommateurs CI |
| P0 | Ajouter test `--fail-on` exit code (2 tests) | S | Protège les gates CI |
| P1 | Ajouter test team history trim (1 test) | S | Vérifie la limite 100 |
| P1 | Ajouter property test `st_full_profile` (4 axes) | M | Couvre 4x plus de branches |
| P2 | Ajouter test `_validate_team_name` (4 tests) | S | Couvre validation entrée |
| P2 | Ajouter test `MAX_JSON_MB` borne exacte (1 test) | XS | Confirme la limite |
| P2 | Fixer `Path('/tmp/test_sd')` dans `test_calibrate_degraded.py` | XS | Évite les conflits CI |
| P3 | Renforcer assertions `or trop permissives` (2 tests) | XS | Réduit faux positifs |

---

## 12. Métriques de Couverture par Module

| Module | Tests | Branches estimées | Couverture estimée | Seuil |
|--------|-------|-------------------|-------------------|-------|
| `scoring.py` | ~50 | ~45 | ~98 % | 100 % |
| `cli.py` | ~40 | ~60 | ~82 % | 85 % |
| `team.py` | ~30 | ~40 | ~85 % | 85 % |
| `schema.py` | ~18 | ~20 | ~90 % | 85 % |
| `report.py` | ~20 | ~25 | ~88 % | 85 % |
| `encoding.py` | ~12 | ~15 | ~85 % | 85 % |
| `scoring_defaults.py` | 5 | 5 | 100 % | 85 % |
| `model.py` | 0 (pure data) | 0 | N/A | N/A |
| `utils.py` | ~8 | ~6 | ~90 % | 85 % |
| `questions.py` | 0 (constants) | 0 | N/A | N/A |

---

*Audit généré par OpenCode — pillar tests — 2026-08-28*
