# Codebase Audit: goumies-creative-laivel-up

Triple passe qualité : GC Framework CLI + AIDD 7 piliers + Compound Engineering 5 personas. Les fondations sont solides (sécurité mature, tests au-dessus des seuils, CI 3 OS × 3 Python), mais deux zones critiques se dégagent : la persistance team Tracker (bugs connus, non corrigés) et la taille des god-modules.

- **Date**: 2026-08-31
- **Scope**: src/laivelup/, scripts/, tests/, .github/workflows/, docs/, schemas/, pyproject.toml, requirements.lock
- **Health**: fair (findings critiques isolés, addressables)
- **GC Score**: 7.8/10 — WARN (4 P1)
- **Findings consolidés**: 2 critical, 11 warning, 12 minor (25 au total, dédoublonnés)

---

## Synthèse par passe

| Passe | Scope | Health | Critical | Warning | Minor |
|-------|-------|--------|----------|---------|-------|
| **GC Framework** | 5 axes (scoring pondéré) | WARN | 0 P0 | 4 P1 | — |
| **AIDD** | 7 piliers (findings file:line) | — | 2 | 28 | 25 |
| **CE Personas** | 5 review personas | — | 0 | 7 | 5 |

### Convergence des passes

- **Sécurité** : AIDD trouve 1 critical (symlink TOCTOU) vs CE security qui valide le SHIP (0P0/P1). Le finding AIDD est un risque réel (team.py:54-58) mais les défenses couches sont bonnes — le persona le classifie P2.
- **Architecture** : Toutes les passes convergent sur les god-modules (cli.py 985l, report.py 1051l) et build/ obsolète.
- **Performance** : AIDD conteste le chiffre GC (21 subprocess) — le vrai nombre production est ~7. CE performance confirme cold-start et CSS inline.
- **Dependencies** : AIDD trouve mutmut absent du lockfile (critical) — non confirmé par les autres passes (hors périmètre).

---

## Findings consolidés

| Sev | Source | Location | Issue | Suggested fix | Effort |
| --- | --- | --- | --- | --- | --- |
| 🔴 | AIDD-security | `src/laivelup/team.py:54-58` | Symlink TOCTOU : remplacement `.laivelup/teams/` par symlink = path traversal possible | Containment check via `resolve()` post-mkdir | M |
| 🔴 | AIDD-deps | `pyproject.toml` / `requirements.lock` | Lockfile incomplet : mutmut<3 déclaré mais absent du lockfile + 4 transitives jsonschema manquantes | Régénérer lockfile avec `pip-compile` | S |
| 🟡 | AIDD-security | `schemas/profile.schema.json:85-91` | `answers`/`meta` avec `additionalProperties: true` — clés arbitraires non contraintes | Restreindre ou valider les clés autorisées | M |
| 🟡 | AIDD-security | `src/laivelup/report.py:1013,1019` | Écriture non atomique MD/HTML — fichier corrompu si interruption | tempfile + os.replace() | S |
| 🟡 | AIDD-arch + CE-arch | `src/laivelup/cli.py` (985l), `report.py` (1051l) | God-modules au-delà du seuil 500l — responsabilités mélangées | Extraire interaction.py depuis cli.py, templates HTML depuis report.py | L |
| 🟡 | AIDD-arch + CE-arch | `docs/architecture.mmd` | Diagramme obsolète : 4 modules absents (calibrate_core, calibrate_dashboard, _completion_patch, tui/), typo CLI_YLY | Mettre à jour le diagramme | S |
| 🟡 | CE-arch + CE-maint | Multiples fichiers | Duplication ×4 : `_load_profile` (3 copies), `LEVEL_COLORS` (2), `AXIS_LABELS` (2) | Module partagé dans model.py ou utils.py | M |
| 🟡 | CE-perf + AIDD-perf | `scripts/generate_profile.py:250-257` | 4 subprocess git séquentiels non batchés | Un seul `git log --shortstat` agrégé | S |
| 🟡 | CE-perf | `src/laivelup/report.py` | render_html() reconstruit ~15KB CSS inline à chaque appel | Extraire CSS en constante module | M |
| 🟡 | CE-perf + AIDD-perf | `src/laivelup/cli.py:34-60` | Cold-start CLI : 15+ imports eager (typer, rich, team…) | Lazy imports sur les commandes non critiques | M |
| 🟡 | CE-maint | `src/laivelup/` | ~150 lignes dead code : `QUESTION_TRACE_KEYS` import mort, `apply_scenario_b/c` NotImplementedError, `_validate_minimal` fallback | Nettoyer | S |
| 🟡 | AIDD-codequality | `src/laivelup/team.py:251,293,356` | Pattern opt_out copié-collé 3 fois | Extraire helper | S |
| 🟡 | AIDD-tests | `tests/test_team.py:16-27` | Import fonction privée `_slug` au lieu de tester via exports publics | Refactorer les assertions | S |
| 🟡 | CE-testing | `tests/security/` | Tests security vérifient exit_code mais pas le contenu du message d'erreur | Assertions sur stderr | S |
| 🟢 | AIDD-codequality | `src/laivelup/report.py:84`, `calibrate_dashboard.py:18` | `LEVEL_COLORS` dupliqué entre deux modules | Centraliser | S |
| 🟢 | AIDD-codequality | Multiples | Dead code : `_nes_progress_bar`, `_glossary_tooltip`, imports inutilisés | Nettoyer | S |
| 🟢 | AIDD-ui | `src/laivelup/calibrate_dashboard.py:108` | Cartes axes sans `role="listitem"` ni `aria-label` | Ajouter ARIA | S |
| 🟢 | AIDD-ui | `src/laivelup/team.py:371` | Export HTML équipe sans `<meta>` viewport/charset | Ajouter les balises | S |
| 🟢 | AIDD-ui | `src/laivelup/team.py:341` | Thème divergent : exports équipe en light vs rapports officiels en dark | Documenter ou unifier | S |
| 🟢 | CE-security | `scripts/demo.py:47-52` | subprocess.run() sans timeout → blocage potentiel | Ajouter timeout=30 | S |
| 🟢 | CE-security | `pyproject.toml:159` | Skip Bandit B601 inutile (aucun shell=True dans le codebase) | Retirer le skip | S |
| 🟢 | AIDD-deps | `.github/workflows/ci.yml` | CI audite l'environnement installé plutôt que le lockfile | `pip-audit -r requirements.lock` | S |
| 🟢 | AIDD-perf | `tests/test_team_rgpd.py:238` | write_text() sans encoding (Windows) | Ajouter encoding='utf-8' | S |
| 🟢 | CE-testing | `tests/` | mutmut configuré sur scoring.py uniquement, sans rapport Survivant visible | Générer le rapport mutmut | S |
| 🟢 | AIDD-perf | `scripts/benchmark.py:24-40` | Benchmark dominé par cold-start interpréteur, pas la logique scoring | Micro-benchmark in-process | S |

---

## Top actions

1. **Corriger le symlink TOCTOU team.py** (AIDD security 🔴) — path traversal exploitable, fix en M
2. **Régénérer requirements.lock** (AIDD deps 🔴) — mutmut + transitives manquantes, fix en S
3. **Extraire interaction.py depuis cli.py** (AIDD arch + CE arch + CE maint) — réduit 3 god-modules d'un coup
4. **Centraliser LEVEL_COLORS + _load_profile + AXIS_LABELS** (CE maint + AIDD codequality) — élimine la duplication ×4
5. **Lazy imports cli.py + batch subprocess generate_profile.py** (CE perf + AIDD perf) — cold-start + perf production

---

## Passes détaillées

### GC Framework (CLI `gc analyze`)

| Axe | Score | Passé | P1 | Findings |
|-----|-------|-------|-----|----------|
| security | 8.2 | ❌ | 3 | bandit: 3 issues |
| performance | 6.5 | ❌ | 1 | 21 subprocess, io encoding, complexity |
| architecture | 6.5 | ❌ | 0 | late-import build/, large modules |
| maintainability | 7.5 | ✅ | 0 | large-func tests, dead-code scripts |
| testing | 10.0 | ✅ | 0 | — |

### AIDD (7 piliers)

| Pilier | Health | 🔴 | 🟡 | 🟢 | Top finding |
|--------|--------|-----|-----|-----|------------|
| code-quality | fair | 0 | 9 | 5 | opt_out copié-collé ×3 |
| architecture | fair | 0 | 4 | 3 | god-modules cli.py/report.py |
| security | fair | 1 | 3 | 4 | symlink TOCTOU team.py |
| dependencies | fair | 1 | 2 | 2 | lockfile incomplet |
| performance | good | 0 | 3 | 2 | subprocess séquentiels |
| tests | good | 0 | 4 | 3 | couplage _slug |
| ui | good | 0 | 3 | 5 | ARIA manquant dashboard |

### Compound Engineering (5 personas)

| Persona | Verdict | Findings | Top finding |
|---------|---------|----------|------------|
| ce-security-reviewer | SHIP | 0P0 0P1 1P2 3P3 | demo.py sans timeout |
| ce-performance-reviewer | PASS | 0P0 1P1 2P2 1P3 | cold-start CLI |
| ce-architecture-strategist | CONDITIONAL PASS | 2H 2M 2L 1I | god-modules |
| ce-maintainability-reviewer | PASS w/ reservations | 0C 4H 4M 2L | duplication ×4 |
| ce-testing-reviewer | APPROVE | 0C 0W 3M | coverage_report.txt format |

---

## Coverage

- **GC Framework**: 5 axes analysés (security, performance, architecture, maintainability, testing) — `gc analyze --json`
- **AIDD**: code-quality, architecture, security, dependencies, performance, tests, ui — scan statique + grep + lecture config
- **CE Personas**: 5 personas conditionnels dispatchés selon la matrice de routing Goumies
- **Skipped**: exécution live d'outils (pytest --cov, bandit, pip-audit) — analyse fondée sur lecture statique croisée ; CI existante (3 OS × 3 Python) comme atténuant
