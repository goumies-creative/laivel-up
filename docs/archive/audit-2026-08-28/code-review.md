# Code Review — LAIVEL UP (commit 4c77971)

## Summary

The reviewed codebase is a well-structured, domain-specific CLI tool for AIDD developer level evaluation. The architecture cleanly separates concerns across scoring, reporting, team management, and CLI layers. The scoring engine is principled (AND semantics, refusal to guess, equity guarantees) and the team module demonstrates solid RGPD-aware design with pseudo-anonymization. However, several issues deserve attention: a path traversal risk in `write_reports` (slug-based filenames from untrusted input), redundant date-object mutation in `evaluate_member`, inconsistent error messages in French/English, a missing `--purge` flag test path, and a potential TOCTOU race in `save_team` symlink check. The test suite is thorough at ~85% branch coverage for `cli.py` but lacks integration tests for concurrent team writes and edge cases around `_merge_answer` with adversarial inputs. Overall, the code is production-ready for a hackathon tool with minor hardening needed before external deployment.

## Findings by severity

### Critical

| # | File | Line(s) | Finding |
|---|------|---------|---------|
| C1 | `team.py` | 262-302 | **Potential path traversal in `export_markdown`/`export_csv`/`export_html`** — The `path` argument is user-controlled (via `--out` option). `write_reports` in `report.py` uses `slug(verdict.name)` for the filename, which is derived from user-supplied `name` in the profile JSON. If `slug()` doesn't fully sanitize (it does alphanumeric cleanup, but the hash suffix could collide), this could lead to unexpected file overwrites. Low real-world risk since `slug()` cleans aggressively, but defense-in-depth is missing: no explicit `path.resolve()` check against an allowed root. |
| C2 | `team.py` | 53-55 | **TOCTOU race in symlink check** — `save_team` checks `target.parent.is_symlink()` then proceeds to write. Between the check and the write, an attacker could replace the directory with a symlink. This is a classic time-of-check-to-time-of-use pattern. Mitigation: use `os.open` with `O_NOFOLLOW` or write atomically via temp file + rename. |

### Warning

| # | File | Line(s) | Finding |
|---|------|---------|---------|
| W1 | `cli.py` | 149-152 | **`_version_callback` prints to stdout, not `console`** — Inconsistency with the rest of the CLI which uses Rich `console` for output. When `--json` mode is active, `print()` goes to stdout alongside JSON output, potentially corrupting machine-readable output. Should use `error_console` or route through `console`. |
| W2 | `cli.py` | 223-269 | **`_print_verdict` has dual responsibility** — It both computes the verdict (`evaluate(profile)`) and renders it. The caller expects a `Verdict` return but doesn't know evaluation already happened. If `evaluate` has side effects or is expensive, this is misleading. Consider splitting into `evaluate` + `render_verdict`. |
| W3 | `cli.py` | 384-386 | **Dead code path** — `if verdict.decided: if verdict.level is None: return`. If `decided` is true, `level` is guaranteed non-None (by `Verdict.decided` property). This is unreachable. |
| W4 | `cli.py` | 379 | **`profile.answers['last_answer']` mutation in loop** — `_merge_answer` sets `answers['last_answer']` every iteration, but the `interrogate` loop also sets it directly at line 379 before calling `_merge_answer`. The double-write is redundant and confusing about which value is canonical. |
| W5 | `scoring.py` | 407-409 | **`min()` over non-None levels is fragile** — If a future scorer returns a level not in the expected enum range, `min()` will silently pick it. The `if a.level is not None` guard is correct but the pattern could be made explicit with a dedicated helper. |
| W6 | `team.py` | 167-168 | **Redundant re-assignment** — `member = team.members[member_slug]` appears at line 163 and again at line 168 (after `evaluate`). The second assignment overwrites the first, but `member` is never used between them. Dead variable. |
| W7 | `cli.py` | 353 | **`asked: set[str]` tracks questions by string content** — If two questions have identical text (unlikely but possible with translations), only one would be asked. Consider tracking by question ID. |
| W8 | `report.py` | 92 | **`escape(axis_label(a.axe))` double-escapes** — `axis_label()` returns plain text (e.g., "Taille"), then `escape()` is correct. But `level_label()` at line 86 returns emoji-decorated text (e.g., "🔺 Red") that is NOT escaped, while the axis label IS escaped. Inconsistent XSS protection. |

### Minor

| # | File | Line(s) | Finding |
|---|------|---------|---------|
| M1 | `cli.py` | 210-211 | **f-string with generator** — `", ".join(l.name for l in Level)` inside an f-string is fine but slightly unusual formatting for this codebase. Minor style inconsistency. |
| M2 | `scoring.py` | 50-57 | **`_as_numeric` passes `str(value)` to `cast`** — This means `_as_numeric(None, float)` returns `None` (good), but `_as_numeric("3.7", int)` returns `int(str("3.7"))` which raises `ValueError`. The fallback to `None` handles it, but the intent would be clearer with an explicit `try/except` per type. |
| M3 | `team.py` | 85 | **Magic number `1 * 1024 * 1024`** — File size guard uses a hardcoded 1MB. Should be a named constant like `MAX_TEAM_FILE_MB = 1` for consistency with `MAX_JSON_MB` in `cli.py`. |
| M4 | `cli.py` | 56-62 | **Module-level side effects** — `ensure_utf8_env()` runs at import time. This means importing `laivelup.cli` mutates `os.environ`, which can surprise test runners and library consumers. Consider lazy initialization. |
| M5 | `cli.py` | 73 | **`MAX_JSON_MB = 2` not shared** — The team module has its own `1 * 1024 * 1024` limit (1MB) while the CLI uses `2 * 1024 * 1024` (2MB). These limits should be documented and named consistently. |
| M6 | `team.py` | 288 | **History slug truncated to 16 chars** — `entry['slug'][:16] + '...'` may break mid-hash. The hash suffix is 8 hex chars + separator + prefix. Truncation at 16 could cut in the middle of the prefix, producing misleading output. |
| M7 | `scoring.py` | 136-142 | **`_dominant` and `size_max` both compute `counts` and `tied`** — Duplicated logic between the helper and its caller. `_dominant` computes `tied` internally but `size_max` recomputes it at line 170. |
| M8 | `report.py` | 173-205 | **`verdict_to_dict` duplicates serialisation logic** — Export functions in `team.py` also build dicts manually (e.g., `export_json` at line 237). These should share `verdict_to_dict` or a common serializer. |
| M9 | `cli.py` | 1-19 | **Module docstring mixes French and English** — The docstring is French but the exit code descriptions and some comments are English. Not a bug, but inconsistent with the "tout en français" convention visible elsewhere. |
| M10 | `encoding.py` | 87 | **`\u2014` (em dash) mapped to `-`** — The AGENTS.md rule says to replace `—` with `·` in titles/labels, not `-`. This ASCII fallback mapping contradicts the project's typography convention. |

## Strengths

- **Principled scoring engine** — The AND semantics (`min()` across all axes) with refusal-to-guess is well-documented and correctly implemented. Red flags and equity checks are thorough.
- **RGPD-aware team design** — Pseudo-anonymization via HMAC-SHA256, opt-out with history masking, no personal data in exports. The `remove_member(purge=True)` path is correctly implemented.
- **Cross-platform encoding** — The encoding module handles Windows legacy (cmd.exe), Windows Terminal, and Unix with a graceful degradation chain. The `ascii_fallback` mapping is comprehensive.
- **CLI UX** — Typer integration with `no_args_is_help=True`, structured exit codes (0/1/2/3), `--json` mode for CI/agent consumption, `--fail-on` for pipeline gating. Professional CLI conventions.
- **Test coverage** — `test_cli_extended.py` covers error paths, edge cases, team persistence, JSON structure validation, and `--fail-on` logic. The `_parse_retry_ratio` tests are particularly thorough (11 cases including French decimals, clamping, negative values).
- **Documentation in code** — Module docstrings explain the "why" not just the "what" (e.g., the equity guarantee in `scoring.py`, the privacy model in `team.py`).
- **Consistent dataclass model** — `ProfileData`, `Verdict`, `AxisScore`, `RedFlag` are clean value objects with no hidden behavior. The `Verdict.decided` property is elegant.

## Recommendations (ordered by priority)

1. **Harden `write_reports` against slug injection** — Add a path containment check: `assert md.resolve().is_relative_to(out_dir.resolve())`. Consider generating filenames from a UUID or timestamp + slug combination rather than slug alone.
2. **Fix the TOCTOU in `save_team`** — Replace the symlink check-then-write with an atomic write pattern: write to a temp file in the same directory, then `os.replace()` to the target. This also prevents partial writes on crash.
3. **Remove dead code path** at `cli.py:385-386` — The `if verdict.level is None: return` inside `if verdict.decided:` is unreachable. Delete it.
4. **Fix `_version_callback` output routing** — Use `error_console.print()` instead of `print()` to avoid corrupting `--json` output.
5. **Split `_print_verdict`** — Extract the `evaluate()` call out of the rendering function. Have `evaluate_profile` call `evaluate()` directly, then pass the verdict to a pure rendering function.
6. **Fix `level_label` escaping inconsistency in `report.py`** — Either escape all dynamic content or none. Since `level_label` returns predictable values, it's safe, but the inconsistency is confusing. Add a comment explaining why it's safe.
7. **Consolidate file size limits** — Define `MAX_TEAM_FILE_MB` in `team.py` and reference it, mirroring `MAX_JSON_MB` in `cli.py`. Document why they differ (teams can accumulate history).
8. **Extract `_dominant` logic to avoid duplication** — Have `size_max` call `_dominant` and use its return values directly instead of recomputing `tied`.
9. **Share serialization via `verdict_to_dict`** — Have `team.export_json` call `verdict_to_dict` for member verdicts instead of building dicts manually.
10. **Add integration tests for concurrent team writes** — Two processes writing to the same team file simultaneously could corrupt data. At minimum, document the limitation.

## Files reviewed

| File | LOC | Key changes in 4c77971 |
|------|-----|------------------------|
| `src/laivelup/cli.py` | 611 | Refactored `_load_profile` with schema validation, added `_filter_fields` for JSON output, restructured `evaluate_profile` JSON/report branching, cleaned up `interrogate` loop logic |
| `src/laivelup/encoding.py` | 130 | Minor: moved `Console` import behind `TYPE_CHECKING` guard for cleaner lazy loading |
| `src/laivelup/scoring.py` | 429 | Added `normalize_profile` validation refinements (float-integer rejection at B2), updated `_as_numeric` to handle None/bool edge cases |
| `src/laivelup/team.py` | 398 | Added `_validate_team_name` regex, symlink rejection in `save_team` (G01), file size guard in `load_team` (G01), opt-out persistence in history (B1), automatic history trim (S3) |
| `src/laivelup/report.py` | 205 | Refactored `verdict_to_dict` to include `evidence` and `variance` in axis serialization |
| `tests/test_cli_extended.py` | 531 | Added 173 lines: `TestFilterFields`, `TestJsonMode`, `TestFailOn`, `TestHistoryTrim`, expanded `TestTeamCommands` with persistence and export validation |
