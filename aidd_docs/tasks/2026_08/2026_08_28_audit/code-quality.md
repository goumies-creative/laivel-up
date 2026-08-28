# Code-Quality Audit — LAIVEL UP

**Date:** 2026-08-28
**Scope:** `src/laivelup/` (11 files, ~1 843 LOC)
**Lenses:** clean code, tech debt

## Findings

| Sev | Category | Location | Issue | Suggested fix | Effort |
|-----|----------|----------|-------|---------------|--------|
| 🟡 | tech-debt | `cli.py:267` | Dead code — unreachable `if verdict.level is None: return` after `verdict.decided` (which means `level is not None`). The branch can never execute. | Remove the dead `if`/`return` block (lines 267-268). | S |
| 🟡 | tech-debt | `cli.py:157-165` | `_LEVEL_ORDER` dict duplicates `Level` IntEnum values (`Level.WHITE.value == 0`, etc.). | Replace with `Level[fail_on.upper()].value` and remove `_LEVEL_ORDER`. | S |
| 🟡 | tech-debt | `team.py:130-132` + `report.py:173-175` | Two private `_slug()` wrappers are one-liners that just call `slug()` from utils. Dead indirection layers. | Delete both `_slug` functions; call `slug()` directly from the callers. | S |
| 🟡 | tech-debt | `scoring.py:347-349` | `if not questions: questions.append(QUESTION_IDS['DEFAULT'])` — `_questions_for` always returns ≥1 item. The `evaluate` caller never reads this default (it's appended to `next_steps`, not used as a fallback guard). Dead branch. | Remove the `if not questions:` guard and the `DEFAULT` key in `QUESTION_IDS`, or document its intended consumer. | S |
| 🟡 | clean-code | `scoring.py:183` | Magic number `0.5 + 0.1 * n` in confidence formula. The base and step are unnamed. | Extract `CONFIDENCE_BASE = 0.5` and `CONFIDENCE_STEP = 0.1` into `scoring_defaults.py`. | S |
| 🟡 | tech-debt | `scoring.py:50-67` | `_as_float` and `_as_int` are near-identical converters (same structure, differ only by `float` vs `int`). Violates DRY. | Extract a generic `_as_numeric(value, cast)` or keep both but acknowledge the duplication with a comment. | S |
| 🟡 | clean-code | `scoring.py:70-130` | `normalize_profile` is 60 lines with deeply nested `if/else` blocks (4 levels). Mixes validation and error message generation. | Extract helpers: `_validate_pr_sizes(traces, errors)`, `_validate_retries(traces, errors)`, etc. | M |
| 🟡 | tech-debt | `schema.py:54-111` + `scoring.py:70-130` | `_validate_minimal` (fallback) and `normalize_profile` validate the same fields with separate logic. Maintenance burden: a rule change requires updating both. | Consolidate validation into one canonical path (schema + normalize_profile as post-schema business rules). | M |
| 🟡 | tech-debt | `schema.py:14,19` | Global `_schema` with lazy init is not thread-safe (TOCTOU race on `_schema is None`). Acceptable for CLI but blocks future async use. | Add `threading.Lock` or use `functools.lru_cache`. | S |
| 🟡 | tech-debt | `report.py:120-156` + `team.py:352-389` | Inline CSS duplicated across `render_html` and `export_html`. Near-identical badge/table/flag styles. | Extract shared CSS into a constant or template partial. | M |
| 🟡 | clean-code | `scoring_defaults.py:13` | `SCORING_DEFAULTS: dict[str, object]` — `object` value type defeats type safety. Consumers need `# type: ignore` casts. | Use `TypedDict` with precise types, or split into typed constants per key. | M |
| 🟡 | clean-code | `cli.py:541-553` | `_parse_retry_ratio` chains 3 regex patterns with nested `min/max` clamping. Hard to follow and test edge cases. | Break into `_from_percent`, `_from_fraction`, `_from_bare_number` helpers. | M |
| 🟡 | clean-code | `cli.py:300-345` | `evaluate_profile` command function mixes I/O, profile loading, verdict printing, JSON output, report writing, and fail-on logic in one 45-line body. | Extract `_handle_json_output(...)`, `_handle_file_output(...)`, and `_check_fail_on(...)` helpers. | M |
| 🟡 | tech-debt | `cli.py:572-619` | `_merge_answer` has 6 `elif` branches with nested regex — high cyclomatic complexity (~12). Each branch is an independent parser. | Split into `_merge_pr_sizes`, `_merge_retries`, `_merge_level`, etc. | M |
| 🟢 | clean-code | `model.py:93` | `severite: int` — French field name in an otherwise English-named dataclass (`RedFlag`). Inconsistent naming convention. | Rename to `severity` (breaking change for serialized data; add migration). | S |
| 🟢 | clean-code | `team.py:34` | `import re` inside `_validate_team_name` — lazy import in a hot path; `re` is already a stdlib module. | Move `import re` to module top-level. | S |
| 🟢 | clean-code | `report.py:173-175` | `_slug` is a one-liner private wrapper with a misleading name (looks like an override but is just delegation). | Inline `slug(name)` at call site. | S |
| 🟢 | clean-code | `scoring.py:136-142` + `168-170` | `_dominant` and the tie-breaking logic in `size_max` both compute `best = max(counts[s] ...)` and `tied = [s ...]` — duplicated within the same function. | Compute once and pass through, or merge `_dominant` into `size_max`. | S |
| 🟢 | clean-code | `cli.py:55-57` | Module-level `NO_COLOR` and `TTY` computed at import time. Side-effectful import; hard to test with env override. | Wrap in a function or use `functools.lru_cache` for lazy evaluation. | S |
| 🟢 | clean-code | `encoding.py:32` | Bare `except Exception: pass` in `_enable_virtual_terminal_windows` silently swallows all errors (including `KeyboardInterrupt` on some Python builds). | Catch `(OSError, ValueError, AttributeError)` specifically. | S |
| 🟢 | tech-debt | `cli.py:476-481` | `export_fn` dict maps format strings to functions. No fallback typing; `.get(format)` returns `Optional` but the error path is separate. | Use `Literal['md', 'html', 'csv', 'json']` for the format param with Typer's `Enum` or `typer.Argument` hints. | S |
| 🟢 | clean-code | `scoring.py:32-39` | `SIZE_VALUES`, `SIZE_ORDER`, `ADOPTION_SIGNALS` are module-level constants but `SIZE_VALUES` duplicates the set comprehension `{s for s in SIZE_ORDER}`. | Derive `SIZE_VALUES` from `SIZE_ORDER`: `SIZE_VALUES = frozenset(SIZE_ORDER)`. | S |

## Top actions

1. **Remove dead code in `cli.py:267-268`** — unreachable `if verdict.level is None: return` after `verdict.decided` check. Quick win, zero risk.
2. **Eliminate `_LEVEL_ORDER` in `cli.py`** — use `Level[...].value` directly. Removes 9 lines of duplication.
3. **Delete `_slug` wrappers in `team.py:130` and `report.py:173`** — call `slug()` directly. Removes dead indirection.
4. **Extract `normalize_profile` helpers in `scoring.py`** — split the 60-line function into `_validate_pr_sizes`, `_validate_retries`, `_validate_integers`, `_validate_booleans` for readability and testability.
5. **Consolidate validation** between `schema.py::_validate_minimal` and `scoring.py::normalize_profile` to eliminate the maintenance burden of two independent validation paths.
6. **Extract shared CSS** from `report.py::render_html` and `team.py::export_html` into a constant or template.

## Coverage

- Scanned: code-quality (clean code + tech debt)
- Skipped: none
