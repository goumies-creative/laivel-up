# Changelog

Toutes les changements notables de LAIVEL UP sont documentés dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/),
et le projet suit [Semantic Versioning](https://semver.org/lang/fr/).

## [Unreleased]

### Added
- `utils.py` : slug HMAC-SHA256 + generate_team_salt (shared)
- `questions.py` : QUESTION_IDS dict partagé scoring/CLI
- `scripts/demo.py` : script de démo 2 min pour enregistrement asciinema
- `scripts/version_bump.py` : bump SemVer automatique + tag + commit
- `.github/workflows/release.yml` : tag v* → build → PyPI + GitHub Release
- `docs/VIDEO_PRODUCTION.md` : guide complet production vidéo (asciinema + Aegisub + FFmpeg)
- `aidd_docs/.../video-demo-prompt.md` : prompt Claude Desktop pour génération script démo
- `tests/test_demo.py` : tests structurels et d'exécution de demo.py
- `tests/conftest.py` : isolation `.laivelup/` via autouse fixture (adversarial #3)
- `tests/test_scoring.py::test_normalize_retries_inf_refuse` : float("inf") rejection (S6)
- `tests/test_scoring.py::test_normalize_retries_float_refuse` : non-integer float rejection (S6)
- `tests/test_team_rgpd.py::TestReviewFixes` : 6 tests post-CE-review (HMAC, XSS, confidence, opt-out)
- `aidd_docs/.../audit/security.md` : deep dive sécurité (score 9/10)
- `aidd_docs/.../audit/adversarial-deep-dive.md` : review adversariale (3 findings)
- `aidd_docs/.../audit/performance-deep-dive.md` : deep dive performance (score 8.5/10)
- `aidd_docs/.../audit/architecture-deep-dive.md` : deep dive architecture (score 9/10)
- `aidd_docs/.../audit/maintainability-deep-dive.md` : deep dive maintenabilité (score 9/10)
- `aidd_docs/.../2026_08_24_critique_complete_synthese.md` : synthèse session 3 (8.8/10)
- `docs/solutions/session-3-critique-audit-trail.md` : learnings session 3

### Changed
- `team.py` : HMAC-SHA256 avec sel par équipe (slug résistant dictionnaire)
- `team.py` : export_html échappe les caractères XSS (html.escape)
- `team.py` : export_html échappe team.name dans le template HTML (S1)
- `team.py` : confidence = limiting_axis (pas max)
- `team.py` : opt_out persiste dans l'historique (B1)
- `team.py` : trim automatique history (100 max, S3)
- `team.py` : validation noms d'équipe alphanum + tirets (S2)
- `team.py` : limite 50 membres par équipe (S5)
- `scoring.py` : normalize_profile rejette les floats non-entiers (B2 breaking)
- `scoring.py` : _questions_for utilise QUESTION_IDS
- `scoring.py` : import QUESTION_IDS en tête de fichier (archi #5)
- `cli.py` : _merge_answer match par chaîne exacte (plus fragile substring)
- `cli.py` : import QUESTION_IDS en tête de fichier (archi #5)
- `report.py` : verdict_to_dict() sérialisation canonique Verdict→JSON (archi #3)
- `report.py` : `<main>` tag dans le HTML (maintainability)
- `scripts/ci_evaluate.py` : schema.validate_profile avant évaluation (archi #2)
- `scripts/ci_evaluate.py` : utilise verdict_to_dict (archi #3)
- `generate_profile.py` : _detect_pr_sizes 51→1 process git (perf 3.1)
- `generate_profile.py` : _detect_retries_after_fact git log -n 100 (perf 3.2)
- `.github/workflows/aidd-eval.yml` : fix injection shell via env: (adversarial #1)
- `tests/test_install_clean.py` : result.output → result.stdout (adversarial #2)
- `docs/architecture.mmd` : +utils.py, +questions.py, +release_hackathon.sh, +run_all_examples.sh
- `docs/adr/0007-team-tracker-rgpd-slug-sha256.md` : périmètre RGPD documenté (team salé, report brut)
- `QUALITY.md` : +HMAC-SHA-256, +test counts, +session 3 audit
- `TESTING_STRATEGY.md` : +security tests, +test counts
- `TRANSPARENCE.md` : +HMAC salt, +RGPD scope
- `CONTRIBUTING.md` : ajout section "Release Process" complète

## [0.2.0] - 2026-08-22

### Added
- `scoring_defaults.py` : extraction SCORING_DEFAULTS (seuils modifiables par scripts Plan B)
- `scripts/calibrate_degraded.py` : mode dégradé diagnostic (strict/graceful, json/table/markdown)
- `scripts/apply_calibration_fix.py` : scénarios A/B/C de patch calibration
- `scripts/release_hackathon.sh` : release atomique (tag + push + GH Release + CI check)
- `tests/test_calibrate_degraded.py` : 9 tests mode dégradé
- `tests/test_apply_calibration_fix.py` : 6 tests patch calibration
- `tests/test_scoring_defaults.py` : 5 tests extraction constantes
- CI job `calibrate-degraded` dans `ci.yml`

### Changed
- `scoring.py` : import depuis `scoring_defaults.py`, aliases backward-compatible
- `scoring.py` : remplacement `_SIZE_LEVEL` par dict lookup `SCORING_DEFAULTS["SIZE_LEVEL"]`

## [0.1.0] - 2026-08-21

### Added
- CLI Typer + Rich : `evaluate`, `interrogate`, `team create/evaluate/export`
- Moteur de scoring : 4 axes (Size, Harness, Intervention, Parallel) × 7 niveaux
- Méthode La Décodeuse : refus de deviner, questions ciblées
- Validation JSON Schema Draft 2020-12
- Team Tracker RGPD : pseudo-anonymisation SHA-256
- Rapports Markdown + HTML
- CI matrix : Ubuntu/Windows/macOS × Python 3.11/3.12/3.13
- Tests : 143+ tests (unit, property, snapshot, security)
- 16 ADR (Architecture Decision Records)
- Encoding cross-platform : `sys.stdout.reconfigure` + `emoji=False` fallback
- Documentation : README, METHODE, QUALITY, CONTRIBUTING, TRANSPARENCE, TESTING_STRATEGY
- Profils d'exemple : `profil-maison-1.json`, `profil-maison-2.json`
- Grille officielle AIDD : `grille/aidd.md`
- Quick reference grille → code : `docs/GRID_QUICKREF.md`
- Quickstart juges : `docs/QUICKSTART_JUDGES.md`
