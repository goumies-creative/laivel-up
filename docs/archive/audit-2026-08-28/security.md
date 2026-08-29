---
name: audit
description: Security pillar audit for LAIVEL UP
argument-hint: N/A
---

# Codebase Audit: LAIVEL UP — Security Pillar

Audit sécurité du CLI d'évaluation AIDD, focusing OWASP risks, injection, input validation, secrets, and RGPD handling.

- **Date**: 2026_08_28
- **Scope**: `src/laivelup/` (CLI + scoring + team tracker + exports)
- **Health**: good
- **Findings**: 0 critical, 2 warning, 4 minor

## Findings

| Sev | Category | Location | Issue | Suggested fix | Effort |
| --- | --- | --- | --- | --- | --- |
| 🟡 | security | `cli.py:339` | `--fail-on` input not validated before `Level[fail_on.upper()]` — uncaught `KeyError` leaks internal enum names and produces an unhandled traceback instead of a clean error message | Wrap in `try/except KeyError` with a user-friendly message listing valid levels (mirrors `declared_level` validation at `cli.py:226-233`) | S |
| 🟡 | security | `cli.py:543-553` | `_parse_retry_ratio` regex patterns use unbounded `\d+` alternatives and nested optional groups (`(?:[.,]\d+)?` inside `(?:%|pourcent)`) — low ReDoS risk with adversarial input but untested | Add a unit test with crafted long inputs to confirm linear-time matching; optionally simplify to a single pass with `float()` after stripping non-numeric chars | S |
| 🟢 | security | `report.py:162-169` | `write_reports` uses `mkdir(parents=True, exist_ok=True)` on user-supplied `out_dir` — no validation that the resolved path is within an expected directory (acceptable for local CLI, but a constrained `--out` would harden against misuse in automation) | Optionally resolve `out_dir` and reject paths outside CWD or a configurable root when `LAIVELUP_SANDBOX=1` env var is set | M |
| 🟢 | security | `team.py:82` | `load_team` reads arbitrary JSON from disk without size check — a crafted `.laivelup/teams/<name>.json` could be large and consume memory | Add a file-size guard (e.g., 1 MB) before `json.loads()`, mirroring the `MAX_JSON_MB` pattern in `cli.py:199-204` | S |
| 🟢 | security | `team.py:53` | `save_team` creates parent directories with `mkdir(parents=True)` — no symlink check on the path before writing | Resolve the path with `.resolve()` and verify the parent is not a symlink before writing; low risk for local CLI but good hygiene | S |
| 🟢 | security | `cli.py:231` | `declared_level` error message exposes the full `Level` enum to the user (`", ".join(l.name for l in Level)`) — minor information disclosure of internal model | Use a curated list of valid level names instead of iterating the enum, or accept the current behavior as intentional UX | S |

## Top actions

1. **Wrap `--fail-on` in try/except** (`cli.py:339`) — prevents unhandled `KeyError` traceback and matches the validation pattern already used for `declared_level` at line 226. Effort: S.
2. **Add a file-size guard to `load_team`** (`team.py:82`) — mirrors the `MAX_JSON_MB` pattern in `_load_profile` and prevents memory exhaustion from crafted team files. Effort: S.
3. **Simplify or test `_parse_retry_ratio` regex** (`cli.py:543-553`) — ensure the regex is linear-time under adversarial input; a focused property-based test would close this gap. Effort: S.

## Coverage

- **Scanned**: security
- **Skipped**: none (security pillar only, as requested)

### Pillar notes

- **No hardcoded secrets** found across all source files. API keys, tokens, and credentials are absent.
- **No shell injection** risk: the codebase uses no `subprocess`, `os.system`, or `eval`.
- **HTML exports are properly escaped**: `report.py` and `team.py` use `html.escape()` on all user-supplied values before embedding in HTML.
- **RGPD opt-out is consistently enforced**: all export functions (`export_json`, `export_markdown`, `export_csv`, `export_html`) filter out opt-out members before writing.
- **Team name validation is solid** (`team.py:36`): `re.fullmatch(r'[a-zA-Z0-9_-]{1,64}', name)` prevents path traversal in team filenames.
- **JSON schema validation** (`schema.py`) validates profiles against `Draft202012Validator` with a fallback minimal validator when `jsonschema` is unavailable.
- **Bandit config** (`pyproject.toml:152-155`): `B101` (assert) and `B601` (shell) are skipped — acceptable for a pure-Python CLI with no shell commands.
