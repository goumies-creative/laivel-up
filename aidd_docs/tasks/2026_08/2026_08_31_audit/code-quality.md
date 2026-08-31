# Codebase Audit: goumies-creative-laivel-up — code-quality

Audit read-only du pilier code-quality : clean code (naming, SOLID, DRY, readability, smells) et tech debt (dead code, complexity, taille, error handling).

- **Date**: 2026-08-31
- **Scope**: `src/laivelup/` (15 modules, 4 029 LOC)
- **Health**: fair
- **Findings**: 0 critical, 9 warning, 5 minor

## Findings

| Sev | Category | Location | Issue | Suggested fix | Effort |
| --- | --- | --- | --- | --- | --- |
| 🟡 | code-quality | `src/laivelup/report.py:84` | `LEVEL_COLORS` dict dupliqué à l'identique dans `calibrate_dashboard.py:18` | Extraire dans un module partagé (ex: `model.py` ou `theme.py`) | S |
| 🟡 | code-quality | `src/laivelup/cli.py:294` | `_nes_progress_bar` définie mais jamais appelée (dead code) | Supprimer la fonction | S |
| 🟡 | code-quality | `src/laivelup/report.py:95` | `_glossary_tooltip` définie mais jamais appelée (dead code) | Supprimer la fonction | S |
| 🟡 | code-quality | `src/laivelup/cli.py:44` | `QUESTION_TRACE_KEYS` importé mais jamais utilisé dans ce module | Retirer de l'import | S |
| 🟡 | code-quality | `src/laivelup/cli.py:42` | `ensure_utf8_env` importé mais jamais appelé (le commentaire ligne 67 affirme un appel « lazy » qui n'existe pas) | Appeler `ensure_utf8_env()` dans `main()` ou retirer l'import | S |
| 🟡 | code-quality | `src/laivelup/team.py:251,293,356` | Pattern de filtrage opt_out dupliqué 3 fois (`opt_out_slugs` + `history_filtered`) | Extraire une fonction `_filter_opt_out(team) -> tuple[set, list]` | S |
| 🟡 | code-quality | `src/laivelup/encoding.py:32` | `except Exception:` avec `pass` silencieux — masque toute erreur non prévue (Windows VTV) | Logger l'exception ou restreindre le type à `OSError` | S |
| 🟡 | code-quality | `src/laivelup/team.py:88` | `except Exception:` dans le nettoyage du temp file — catch trop large | Restreindre à `OSError` | S |
| 🟡 | code-quality | `src/laivelup/cli.py:186` | Mutation de variables globales `console` / `error_console` via `global` — smell anti-SOLID | Injecter la console via un conteneur ou un paramètre | M |
| 🟢 | code-quality | `src/laivelup/report.py:1` | Fichier de 1051 lignes — dépasse le seuil típique 500 LOC | Découper la génération HTML dans un sous-module | M |
| 🟢 | code-quality | `src/laivelup/cli.py:1` | Fichier de 985 lignes — dépasse le seuil típique 500 LOC | Découper les commandes team dans un sous-module | M |
| 🟢 | code-quality | `src/laivelup/team.py:302` | Magic number `[-20:]` pour tronquer l'historique (répété ligne 362) | Extraire une constante `_HISTORY_DISPLAY_LIMIT = 20` | S |
| 🟢 | code-quality | `src/laivelup/team.py:306` | Magic number `[:16]` pour tronquer le slug (répété ligne 366) | Extraire une constante `_SLUG_DISPLAY_LEN = 16` | S |
| 🟢 | code-quality | `src/laivelup/team.py:79` | `import tempfile` à l'intérieur du corps de `save_team` — import tardif injustifié | Remonter en haut du fichier avec les autres imports | S |
| 🟢 | code-quality | `src/laivelup/team.py:151-153` | `_slug()` wrapper triviale autour de `utils.slug()` — couche d'indirection inutile | Appeler `slug()` directement dans `create_team` | S |

## Top actions

1. **Extraire `LEVEL_COLORS`** dans un module partagé pour éliminer la duplication `report.py:84` ↔ `calibrate_dashboard.py:18` (1 finding, Effort S)
2. **Supprimer le dead code** : `_nes_progress_bar` (`cli.py:294`), `_glossary_tooltip` (`report.py:95`), import `QUESTION_TRACE_KEYS` (`cli.py:44`), import `ensure_utf8_env` (`cli.py:42`) — 4 findings, Effort S
3. **DRY sur le filtrage opt_out** dans `team.py` : le pattern `opt_out_slugs` + `history_filtered` est copié-collé 3 fois (251/293/356) — extraire une helper (1 finding, Effort S)
4. **Élargir les `except Exception:` silencieux** (`encoding.py:32`, `team.py:88`) pour ne catcher que les types attendus — réduit le risque de debugging en production (2 findings, Effort S)
5. **Découper report.py et cli.py** au-delà de 500 LOC chacun — améliore la maintenabilité à long terme (2 findings, Effort M)

## Coverage

- **Scanned**: code-quality (clean code + tech debt)
- **Skipped**: architecture, security, dependencies, performance, tests, ui — hors périmètre de cet audit ciblé

## Message final

**Counts** : 0🔴 9🟡 5🟢 — 14 findings total. Health : **fair** (pas de critical, mais dead code et DRY violations isolés et adressables).

**Top 3 findings** :

1. `src/laivelup/report.py:84` — `LEVEL_COLORS` dupliqué à l'identique dans `calibrate_dashboard.py:18`
2. `src/laivelup/cli.py:294` — `_nes_progress_bar` dead code (jamais appelée)
3. `src/laivelup/team.py:251,293,356` — filtrage opt_out copié-collé 3 fois
