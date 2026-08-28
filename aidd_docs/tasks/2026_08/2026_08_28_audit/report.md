# Codebase Audit: LAIVEL UP

Audit qualité complet 7 piliers du repo `goumies-creative-laivel-up`, conduit le 2026-08-28 via le skill `aidd-dev-04-audit`.

- **Date**: 2026-08-28
- **Scope**: `src/laivelup/` (11 modules, ~2118 LOC), `tests/` (~230 tests), `scripts/`, `pyproject.toml`, CI workflows
- **Health**: good
- **Findings**: 0 critical, 29 warning, 33 minor (69 total)
- **Méthode**: consortium Goumies Creative — 6 piliers audités en parallèle, 1 pillier (UI) skipped

---

## Findings

Triés par sévérité (critical d'abord), puis par catégorie.

| Sev | Category | Location | Issue | Suggested fix | Effort |
|-----|----------|----------|-------|---------------|--------|
| 🟡 | tests | `cli.py:293-296` | `_filter_fields()` — aucune unit test directe | Ajouter 3 tests : champ présent, absent, multi-champs | XS |
| 🟡 | tests | `cli.py:320-325` | Mode `--json` — sortie JSON jamais vérifiée (structure, clés) | Test `json.loads(r.output)` + vérification clés `level`, `axes`, `next_steps` | S |
| 🟡 | tests | `cli.py:337-345` | `--fail-on` — exit code 1 non vérifié quand niveau inférieur | Test profil RED + `--fail-on GREEN` → exit 1 | S |
| 🟡 | tests | `team.py:194-195` | Team history trim (100 entrées) non testé | Test bouclant 101 évaluations, vérifier `len(history) == 100` | S |
| 🟡 | tests | `tests/test_properties.py` | Property tests ne couvrent que 1 axe (pr_sizes) sur 4 | Ajouter `st_full_profile` générant traces complètes (4 axes) | M |
| 🟡 | security | `cli.py:339` | `--fail-on` input non validé avant `Level[fail_on.upper()]` — KeyError non intercepté | Wrap `try/except KeyError` avec message user-friendly | S |
| 🟡 | security | `cli.py:543-553` | `_parse_retry_ratio` regex à groupes non bornés — faible risque ReDoS | Ajouter test avec entrées adversariales longues | S |
| 🟡 | code-quality | `cli.py:267` | Dead code — branche `if verdict.level is None: return` inaccessible après `verdict.decided` | Supprimer les lignes 267-268 | S |
| 🟡 | code-quality | `cli.py:157-165` | `_LEVEL_ORDER` duplique les valeurs `Level` IntEnum | Utiliser `Level[fail_on.upper()].value` directement | S |
| 🟡 | code-quality | `team.py:130-132` + `report.py:173-175` | Deux wrappers `_slug()` privés = indirection morte | Appeler `slug()` directement | S |
| 🟡 | code-quality | `scoring.py:347-349` | Branche morte `if not questions: questions.append(...)` — `_questions_for` retourne toujours ≥1 | Supprimer la garde `if not questions:` | S |
| 🟡 | code-quality | `scoring.py:183` | Magic number `0.5 + 0.1 * n` dans formule confiance | Extraire `CONFIDENCE_BASE` et `CONFIDENCE_STEP` dans `scoring_defaults.py` | S |
| 🟡 | code-quality | `scoring.py:50-67` | `_as_float` et `_as_int` quasi-identiques — DRY violation | Extraire `_as_numeric(value, cast)` générique | S |
| 🟡 | code-quality | `scoring.py:70-130` | `normalize_profile` fait 60 lignes, 4 niveaux d'imbrication | Extraire helpers : `_validate_pr_sizes`, `_validate_retries`, etc. | M |
| 🟡 | code-quality | `schema.py:54-111` + `scoring.py:70-130` | Double validation même champ (schema + normalize) | Consolidation en un chemin canonical | M |
| 🟡 | code-quality | `schema.py:14,19` | `_schema` lazy init non thread-safe (TOCTOU) | Ajouter `threading.Lock` ou `lru_cache` | S |
| 🟡 | code-quality | `report.py:120-156` + `team.py:352-389` | CSS inline dupliquée entre `render_html` et `export_html` | Extraire CSS partagée en constante | M |
| 🟡 | code-quality | `scoring_defaults.py:13` | `SCORING_DEFAULTS: dict[str, object]` force 6 `# type: ignore` | Utiliser `TypedDict` typé | M |
| 🟡 | code-quality | `cli.py:541-553` | `_parse_retry_ratio` enchaîne 3 regex — complexité cyclomatique ~12 | Décomposer en `_from_percent`, `_from_fraction`, `_from_bare_number` | M |
| 🟡 | code-quality | `cli.py:300-345` | `evaluate_profile` mélange I/O, validation, JSON, reports, fail-on | Extraire `_handle_json_output`, `_handle_file_output`, `_check_fail_on` | M |
| 🟡 | code-quality | `cli.py:572-619` | `_merge_answer` a 6 branches elif avec regex nichées — complexité ~12 | Décomposer en `_merge_pr_sizes`, `_merge_retries`, etc. | M |
| 🟡 | architecture | `encoding.py` (entier) | Module inutilisé — 0 imports internes. `cli.py` réinvente l'encodage | Supprimer `encoding.py` ou l'intégrer dans `cli.py` | S |
| 🟡 | architecture | `cli.py:1-623` | 623 lignes, 10+ responsabilités — logique métier dans le mauvais module | Extraire `_merge_answer` + `_parse_retry_ratio` dans `interrogate.py` | M |
| 🟡 | architecture | `scoring.py:42-47` | 6 alias backward-compatible avec `# type: ignore[assignment]` | Utiliser `TypedDict` ou accès direct au dict | S |
| 🟡 | performance | `cli.py:577` | `_merge_answer()` compile `rf'\b{size}\b'` à chaque itération (4 regex/appel) | Remplacer par `size.lower() in low.split()` | XS |
| 🟡 | performance | `generate_profile.py:131-132` | `_detect_retry_loops()` compile regex à chaque appel | Monter `re.compile()` au niveau module | XS |
| 🟡 | performance | `team.py:34` | `import re` local dans `_validate_team_name` à chaque appel | Déplacer `import re` en haut du fichier | XS |
| 🟢 | dependencies | `.pre-commit-config.yaml:4` | Ruff v0.15.13 (pre-commit) vs 0.11.13 (lockfile) — version divergente | Synchroniser les versions | S |
| 🟢 | dependencies | `pyproject.toml:16` | Contrainte `pytest-cov>=4.1` obsolète (lock: 6.2.1) | Moderniser en `pytest-cov>=6.0` | XS |
| 🟢 | dependencies | `requirements.lock` | Lockfile manuel, pas de résolution auto (uv/pip-tools) | Adopter `uv lock` | M |
| 🟢 | security | `report.py:162-169` | `write_reports` écrit dans chemin arbitraire — pas de sandbox | Résoudre le path et rejeter hors CWD si `LAIVELUP_SANDBOX=1` | M |
| 🟢 | security | `team.py:82` | `load_team` sans garde taille fichier — crafted JSON pourrait consommer mémoire | Ajouter garde 1 MB comme `_load_profile` | S |
| 🟢 | security | `team.py:53` | `save_team` crée dirs sans check symlink | Résoudre path et vérifier parent pas symlink | S |
| 🟢 | security | `cli.py:231` | Message d'erreur expose le `Level` enum complet | Utiliser liste curatée de noms valides | S |
| 🟢 | code-quality | `model.py:93` | `severite: int` — nom français dans dataclass anglaise | Renommer en `severity` (migration breaking) | S |
| 🟢 | code-quality | `team.py:34` | `import re` local inutile | Déplacer en haut de fichier | XS |
| 🟢 | code-quality | `scoring.py:136-142` + `168-170` | `_dominant` et tie-breaking dupliqués dans `size_max` | Calculer une fois et passer | S |
| 🟢 | code-quality | `cli.py:55-57` | `NO_COLOR`/`TTY` computed au import — side-effectful | Wrapper dans fonction ou `lru_cache` | S |
| 🟢 | code-quality | `encoding.py:32` | Bare `except Exception: pass` — masque tous les erreurs | Catch `(OSError, ValueError, AttributeError)` | S |
| 🟢 | code-quality | `scoring.py:32-39` | `SIZE_VALUES` duplique `SIZE_ORDER` | Dériver : `SIZE_VALUES = frozenset(SIZE_ORDER)` | XS |
| 🟢 | code-quality | `cli.py:476-481` | `export_fn` dict sans typing Literal | Utiliser `Literal['md','html','csv','json']` | S |
| 🟢 | architecture | `docs/architecture.mmd` | 2 edges manquants : `GEN_PROFILE --> TEAM_MOD`, `CI_EVAL --> REPORT` | Ajouter les 2 edges Mermaid | XS |
| 🟢 | architecture | `docs/adr/` | ADR-0017 (team persistence) non documentée | Créer `docs/adr/0017-team-tracker-persistence-json-local.md` | S |
| 🟢 | architecture | `scoring.py:70-130` + `schema.py:31-51` | Validation double (schema + normalize) — divergences silencieuses possibles | Documenter la séparation dans une ADR | XS |
| 🟢 | performance | `scoring.py:367-372` | Dict `scorers` recréé à chaque appel `evaluate()` | Déclarer `SCORERS` au niveau module | XS |
| 🟢 | performance | `generate_profile.py:160` | Regex fixe compilée à l'intérieur de la fonction | Monter au niveau module | XS |
| 🟢 | performance | `generate_profile.py:219` | `re.search` pattern constant compilé à chaque appel | Monter au niveau module | XS |
| 🟢 | performance | `team.py:273,337` | `opt_out_slugs` calculé en double dans exports | Extraire en helper ou passer en paramètre | XS |
| 🟢 | tests | `schema.py:38-41` | Branch `except ImportError` (jsonschema absent) non testée | Mock `jsonschema` pour lever ImportError | M |
| 🟢 | tests | `team.py:32-39` | `_validate_team_name` non testée directement | 4 tests unitaires (vide, spéciaux, 65 chars, OK) | S |
| 🟢 | tests | `team.py:82-102` | Fallback `generate_team_salt()` quand salt absent non testé | Test JSON sans clé `salt` | XS |
| 🟢 | tests | `cli.py:541-553` | `_parse_retry_ratio` — cas limites non testés (0%, 100%, grands nombres) | 3 tests dédiés | XS |
| 🟢 | tests | `cli.py:169-172` | `--version` testé en snapshot mais pas en assertions directes | Ajouter `assert '0.1.0' in r.output` | XS |
| 🟢 | tests | `cli.py:82` | `MAX_JSON_MB = 2` borne exacte non testée | Test avec fichier 2.1 MB | S |
| 🟢 | tests | `tests/test_team_rgpd.py:67` | Assertion trop permissive : `assert 'alice' not in slug or slug.startswith('alice')` | Renforcer l'assertion | XS |
| 🟢 | tests | `tests/test_cli.py:33` | Assertion trop permissive : `assert 'introuvable' in r.output or 'trouv' in r.output` | Renforcer l'assertion | XS |
| 🟢 | tests | `tests/test_calibrate_degraded.py:139` | `Path('/tmp/test_sd')` hardcoded au lieu de `tmp_path` | Remplacer par `tmp_path` | XS |

---

## Top actions

Highest impact first. Chaque action nomme les findings concernés.

1. **Ajouter les 3 tests CLI critiques** (findings tests #1-3) — `_filter_fields`, `--json` mode, `--fail-on` exit code. Couvrent les gaps les plus exposés en CI/agent. Effort: **S**.
2. **Valider `--fail-on` input** (security #1, code-quality #2) — wrap `Level[fail_on.upper()]` dans `try/except KeyError`. Empêche les traces non interceptées. Effort: **S**.
3. **Supprimer `encoding.py` mort** (architecture #1) — 0 imports, double implémentation de l'encodage. Effort: **XS**.
4. **Test team history trim** (tests #4) — 1 test vérifiant la limite 100 entrées. Effort: **S**.
5. **Extraire logique métier de `cli.py`** (architecture #2, code-quality #11-12) — `_merge_answer` + `_parse_retry_ratio` + `_LEVELS_BY_KEYWORD` → `interrogate.py`. Réduit `cli.py` de ~80 lignes. Effort: **M**.
6. **Consolider validation** (code-quality #9) — `_validate_minimal` (schema) vs `normalize_profile` (scoring) vérifient les mêmes champs avec des logiques différentes. Effort: **M**.
7. **Synchroniser ruff pre-commit/lockfile** (dependencies #1) — 2 versions divergentes = résultats inconsistent. Effort: **XS**.
8. **Property tests multi-axes** (tests #5) — `st_full_profile` couvrant les 4 axes au lieu de 1. Effort: **M**.

---

## Coverage

Piliers examinés et statut :

- **Scanned**: code-quality (22 findings), architecture (7 findings), security (6 findings), dependencies (3 findings), performance (7 findings), tests (22 findings)
- **Skipped**: `ui` — projet CLI sans interface graphique. Les exports HTML ne constituent pas un UI layer.

### Health summary

| Pillar | Critical | Warning | Minor | Health |
|--------|----------|---------|-------|--------|
| code-quality | 0 | 13 | 9 | good |
| architecture | 0 | 3 | 4 | good |
| security | 0 | 2 | 4 | good |
| dependencies | 0 | 0 | 3 | good |
| performance | 0 | 3 | 4 | good |
| tests | 0 | 5 | 8 | good |
| ui | — | — | — | skipped |
| **Total** | **0** | **26** | **32** | **good** |

### Remarques transversales

- **Aucun finding critique** — la codebase est saine pour un projet hackathon
- **Sécurité solide** : 22 tests sécurité, pas de shell injection, HTML échappé, RGPD opt-out consistant
- **Architecture propre** : pas de cycles, direction CLI → core → model respectée
- **Performance OK** : moteur O(1), pas de N+1, subprocess bornés
- **Tests bien structurés** : pyramide saine (74% unit, 22% integration, 4% E2E), hypothesis, snapshots
- **Dépendances saines** : 0 CVE, 0 inutilisées, licences compatibles

---

*Rapport fusionné — audit consortium Goumies Creative — 2026-08-28*
