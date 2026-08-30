# Prompt coverage 90 · closing gaps — LAIVEL UP

> Utiliser avec **Claude Desktop** (compte gratuit).
> Copier-coller ce prompt dans une nouvelle session, puis laisser Claude
> orchestrer les skills AIDD et Compound Engineering.
> Ne pas utiliser OpenCode + DeepSeek pour cette tache (contenu didactique,
> risque memoire — voir `AGENTS.md`).

---

## Contexte

**Projet :** LAIVEL UP — CLI d'evaluation du niveau d'adoption de l'AI-Driven
Development (AIDD) des developpeurs. 4 axes, 7 niveaux, regle AND, refus de
deviner.

**Workspace :** `C:\Users\Romy\Desktop\GoumiesLand\GoumiesCreative-Agency\hackathons\goumies-creative-laivel-up`

**Etat actuel (30/08) :**

| Metrique | Valeur |
|----------|--------|
| Tests | 436 passent, 5 deselected |
| Coverage totale | **85 %** (2134 stmts, 322 miss) |
| Seuil `pyproject.toml` | `fail_under = 85` |
| Cible | **90 %** |
| Branch | `main` |

**Fichiers deja traites cette session :**

- `tests/test_cli_extended.py` — 25+ nouveaux tests (team errors, verbose,
  red flags, schema, version, --color, etc.)
- `tests/test_scripts.py` — 15+ nouveaux tests (benchmark, ci_evaluate,
  demo, version_bump)
- `src/laivelup/report.py` — badge verdict agrandi (10.1.e)

**Skills disponibles :**

| Framework | Skills utiles ici |
|-----------|-------------------|
| AIDD v5.4.2 | `aidd-dev-01-plan` (plan), `aidd-dev-02-implement` (executor Sonnet), `aidd-dev-05-review` (checker Opus), `aidd-dev-03-assert` (validation) |
| Compound Engineering | `ce-code-review`, `ce-plan`, `ce-simplify-code` |

**Principe AIDD :** aucun agent ne juge son propre travail. Executor (Sonnet)
implemente, Checker (Opus) verifie.

---

## Objectif

1. **Coverage 85 % → 90 %+** en ciblant uniquement les sections TESTABLE.
2. **Marquer UNTESTABLE** avec `# pragma: no cover` (pas de mock force).
3. **Verifier les plan items** deja traites et signaler les restants bloques.

---

## Analyse des ecarts par fichier

### Legende

| Tag | Signification | Action |
|-----|---------------|--------|
| TESTABLE | Logique pure, mockable | Ecrire un test |
| UNTESTABLE_RICH | Rendu Rich / print console | `# pragma: no cover` |
| UNTESTABLE_SUBPROCESS | subprocess / argparse / file I/O lourd | `# pragma: no cover` ou test d'integration plus tard |

### `src/laivelup/cli.py` — 452 stmts, 88 %, 53 miss

| Lignes | Code | Tag | Test / action |
|--------|------|-----|---------------|
| 225-230 | `declared_level` inconnu → `KeyError` + exit 2 | TESTABLE | Deja couvert par `test_declared_level_inconnu` — verifier assertion `exit_code == 2` |
| 337-346 | `_print_verdict` : box `DONNEES INVALIDES` | UNTESTABLE_RICH | `# pragma: no cover` sur le bloc `if verdict.data_errors:` |
| 369-373 | `_print_verdict` : boucle `red_flags` | UNTESTABLE_RICH | `# pragma: no cover` sur la boucle `for f in verdict.red_flags:` |
| 384-399 | `_print_verdict` : bloc `verbose` | UNTESTABLE_RICH | `# pragma: no cover` sur `if is_verbose:` |
| 455-460 | `evaluate` : branche non-TTY `write_reports` + print chemins | UNTESTABLE_SUBPROCESS | Laisser tel quel (depend de TTY reel) |
| 466 | `evaluate` : warning `--fail-on` avec verdict `None` | TESTABLE | `runner.invoke(app, ['evaluate', profil_minimal, '--fail-on', 'RED', '--no-html'])` |
| 481 | `evaluate` : message `FAIL: niveau X < Y` | TESTABLE | Profil BLUE + `--fail-on GOLD` en mode non-json (forcer TTY via `CliRunner`) |
| 661-663 | `team create` : `create_team` raise `ValueError` | TESTABLE | `monkeypatch.setattr(cli, 'create_team', lambda *a, **k: (_ for _ in ()).throw(ValueError('x')))` |
| 690-691 | `team evaluate` : `load_team` raise `ValueError` | TESTABLE | `team evaluate Nonexistent slug profil` → `exit_code == 2` |
| 697-699 | `team evaluate` : membre non trouve + liste slugs | TESTABLE | `team evaluate Alpha wrong-slug profil` → assert slugs dans output |
| 742-744 | `team export` : `load_team` raise | TESTABLE | `team export Nonexistent` → `exit_code == 2` |
| 767-769 | `team opt-out` : `load_team` raise | TESTABLE | `team opt-out Nonexistent slug` → `exit_code == 2` |
| 796-798 | `team remove` : `load_team` raise | TESTABLE | `team remove Nonexistent slug` → `exit_code == 2` |
| 852 | `calibrate` : `result.errors > 0` branch | TESTABLE | Profils avec mismatch attendu → assert message d'erreur |

### `src/laivelup/team.py` — 180 stmts, 91 %, 16 miss

| Lignes | Code | Tag | Test / action |
|--------|------|-----|---------------|
| 37 | `_validate_team_name` : regex invalide | TESTABLE | `create_team('', ['a'])` ou `create_team('a/b', ['a'])` → `ValueError` |
| 56 | `save_team` : parent is symlink | TESTABLE | `monkeypatch` `Path.is_symlink` → `True` |
| 86-89 | `save_team` : cleanup fichier temp | TESTABLE | Mock `Path.replace` raise, verifier temp supprime |
| 100 | `load_team` : fichier > 1 Mo | TESTABLE | Ecrire JSON > 1 Mo, assert `ValueError` |
| 107-108 | `load_team` : `Level[key]` KeyError | TESTABLE | JSON avec `level: "INVALID"` |
| 158 | `create_team` : > 50 membres | TESTABLE | `create_team('x', ['m']*51)` → `ValueError` |
| 213 | `evaluate_member` : trim history > 100 | TESTABLE | Pre-remplir 101 entrees, evaluer, assert 100 |
| 227, 243 | `remove_member` / `set_opt_out` : membre non trouve | TESTABLE | Appel avec slug inexistant |
| 285, 326, 345 | `export_*` : membre opt-out skippe | TESTABLE | Creer team, `set_opt_out(slug, True)`, exporter, verifier absent |

### `src/laivelup/schema.py` — 63 stmts, 94 %, 4 miss

| Lignes | Code | Tag | Test / action |
|--------|------|-----|---------------|
| 23-24 | `_load_schema` : `FileNotFoundError` | TESTABLE | `monkeypatch.setattr(schema_mod, '_SCHEMA_PATH', Path('/nope'))` |
| 39-41 | `validate_profile` : `ImportError` jsonschema | TESTABLE | `monkeypatch` import jsonschema → `ImportError`, verifier fallback `_validate_minimal` |

### `src/laivelup/report.py` — 167 stmts, 96 %, 6 miss

| Lignes | Code | Tag | Test / action |
|--------|------|-----|---------------|
| 90-93 | `_glossary_tooltip` : terme trouve | TESTABLE | Appel avec terme connu du glossaire |
| 1001, 1007 | `write_reports` : path traversal | TESTABLE | Mock `slug` → `../evil`, assert `ValueError` |

### `src/laivelup/calibrate_core.py` — 67 stmts, 84 %, 11 miss

| Lignes | Code | Tag | Test / action |
|--------|------|-----|---------------|
| 62 | `_load_expected` : pas de cle `levels` | TESTABLE | JSON `{"levels": {}}` |
| 86-94 | `run_calibration` : profil non dans expected → SKIP | TESTABLE | Dossier avec profil absent de expected |
| 100-118 | UNDECIDED attendu mais decide → FAIL | TESTABLE | Profil vide + expected GOLD |
| 130-148 | Decide mais mauvais niveau → FAIL | TESTABLE | Profil BLUE + expected GOLD |

### `scripts/generate_profile.py` — 159 stmts, 65 %, 55 miss

| Lignes | Code | Tag | Test / action |
|--------|------|-----|---------------|
| 73-79 | `_bucket_size` | TESTABLE | Pure function, test direct |
| 166, 170, 175 | `_detect_retries_after_fact` | TESTABLE | Mock `_git` return |
| 54-68, 136-138, 221, 261, 266 | Detection git/filesystem | UNTESTABLE_SUBPROCESS | `# pragma: no cover` |
| 248, 274-278 | Print verbose | UNTESTABLE_RICH | `# pragma: no cover` |
| 299-329 | `main()` | UNTESTABLE_SUBPROCESS | `# pragma: no cover` |

### `scripts/extract_official_profile.py` — 131 stmts, 69 %, 40 miss

| Lignes | Code | Tag | Test / action |
|--------|------|-----|---------------|
| 138, 157-161, 167, 185, 192 | Extractors | TESTABLE | Appels directs avec echantillons |
| 223-224 | `session.md` read | TESTABLE | tmp dir avec session.md |
| 236-306 | `main()` | UNTESTABLE_SUBPROCESS | `# pragma: no cover` |

### `scripts/apply_calibration_fix.py` — 109 stmts, 55 %, 49 miss

| Lignes | Code | Tag | Test / action |
|--------|------|-----|---------------|
| 38-42, 62-63, 72-73 | Error handling, guards | TESTABLE | JSON malforme, mismatch > 2 |
| 94-98 | dry_run replacement | TESTABLE | Monkeypatch fichiers |
| 117-143, 215-234 | Non-dry-run + main() | UNTESTABLE_SUBPROCESS | `# pragma: no cover` |

### `scripts/benchmark.py` — 64 stmts, 55 %, 29 miss

| Lignes | Code | Tag |
|--------|------|-----|
| 43-44, 49, 107-149 | Subprocess + main() | UNTESTABLE_SUBPROCESS — `# pragma: no cover` |

---

## Plan items — etat et actions

### Deja traites cette session (ne pas refaire)

| Item | Fichier | Verif |
|------|---------|-------|
| 9.1.a `add_completion=True` | `src/laivelup/cli.py:71` | `grep add_completion` |
| 9.1.b `--color/--no-color` | `src/laivelup/cli.py:169-183` | `grep "color.*no-color"` |
| 9.1.c couleurs Rich | `src/laivelup/cli.py:250-258` `LEVEL_RICH_COLORS` | Table NIVEAU coloree |
| 9.1.d `epilog` | `src/laivelup/cli.py:422,497` | `grep epilog` |
| 10.1.a-d accessibilite HTML | `src/laivelup/report.py` | ARIA, contrastes, prefixes |
| 10.1.e hierarchie badge | `src/laivelup/report.py:563-575` | Badge 1.6rem vs h1 1rem |

### Bloques (ne pas tenter)

| Item | Raison |
|------|--------|
| 1.3 URL CONTRIBUTING | Attend repo public |
| 1.6 PyPI publish | Attend push final |

### Manuel (hors scope de ce prompt)

| Item | Action |
|------|--------|
| 2.2 Video muette | `docs/VIDEO_PRODUCTION.md` — tourner 2 min max, verifier son coupe |
| 2.4 Formulaire rendu | Deadline 31/08 12h — ne pas rater |
| 2.5 Revue copy | Prompt dedie : `docs/prompts/revue-copy-francaise.md` |

---

## Strategie d'execution (3 vagues)

### Vague 1 — Quick wins TESTABLE (~45 min)

Ordre par ROI (impact coverage / effort) :

1. `schema.py` — 2 tests, 10 min
2. `report.py` — 3 tests, 15 min
3. `calibrate_core.py` — 6 tests, 20 min
4. `team.py` — 12 tests, 45 min
5. `cli.py` error paths — 10 tests, 30 min

**Fichiers cibles :** `tests/test_schema_extended.py`, `tests/test_report.py`,
`tests/test_calibrate.py`, `tests/test_team.py` (etendre), `tests/test_cli_extended.py` (etendre).

### Vague 2 — Pragma UNTESTABLE (~15 min)

Ajouter `# pragma: no cover` sur :

- `src/laivelup/cli.py:337`, `369`, `384` (blocs Rich)
- `scripts/generate_profile.py:248`, `274`, `299` (print + main)
- `scripts/extract_official_profile.py:236` (main)
- `scripts/apply_calibration_fix.py:117`, `215` (non-dry-run + main)
- `scripts/benchmark.py:43`, `107` (subprocess + main)

### Vague 3 — Verification (~15 min)

```bash
python -m pytest tests/ -m "not install and not slow" --timeout=120 \
  --ignore=tests/security --cov=src/laivelup --cov=scripts \
  --cov-report=term-missing --override-ini="addopts="
# Cible : TOTAL >= 90%
python -m ruff check src/ tests/
python -m mypy src/laivelup/
```

---

## Contraintes

- **Un test = une assertion** (`TESTING_STRATEGY.md`)
- **Isolation** : pas de dependance entre tests, `tmp_path` pour tout I/O
- **Nommage** : `test_<ce_qu'on_teste>_<ce_qu'on_attend>`
- **Ne pas modifier le comportement existant** — uniquement tests + pragma
- **Tous les tests existants doivent continuer a passer**
- **Respecter `AGENTS.md`** : accents francais, `·` pas `—`, Bunny Fonts, espaces autour de `/`
- **Budget contexte** : < 60 K tokens par session (ne pas charger tout le vault)

---

## Workflow AIDD recommande

```
1. aidd-dev-01-plan     → plan phase depuis ce prompt
2. aidd-dev-02-implement → executor (Sonnet) ecrit les tests phase par phase
3. aidd-dev-05-review    → checker (Opus) verifie code + behavior + relevancy
4. aidd-dev-03-assert    → valide que coverage >= 90% et ruff/mypy OK
```

---

## Sortie attendue

| Livrable | Emplacement |
|----------|-------------|
| Tests quick wins | `tests/test_schema_extended.py` etc. (extension) ou `tests/test_coverage_gaps.py` (nouveau) |
| Pragma | Directement dans `src/laivelup/cli.py` et `scripts/*.py` |
| Coverage | `TOTAL >= 90%` sur `src/laivelup + scripts` |
| Aucun warning | `ruff check` et `mypy` verts |

---

## Exemple de demande pour Claude Desktop

```
Couvre les ecarts restants vers 90 % en suivant
docs/prompts/coverage-90-closing-gaps.md :

- Vague 1 : quick wins TESTABLE (schema, report, calibrate_core, team, cli)
- Vague 2 : pragma: no cover sur UNTESTABLE_RICH/SUBPROCESS
- Vague 3 : verification coverage + ruff/mypy

Utilise aidd-dev-01-plan puis aidd-dev-02-implement.
```
