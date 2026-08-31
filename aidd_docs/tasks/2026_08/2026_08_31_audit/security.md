---
name: audit
description: Security pillar audit report
argument-hint: N/A
---

# Codebase Audit: goumies-creative-laivel-up — Security

Audit read-only du pilier security (OWASP, injection, secrets, validation inputs, deserialization unsafe). CLI Python Typer, pas de serveur HTTP.

- **Date**: 2026_08_31
- **Scope**: src/laivelup/, scripts/, tests/security/, .github/workflows/
- **Health**: fair
- **Findings**: 1 critical, 3 warning, 4 minor

## Findings

| Sev | Category | Location | Issue | Suggested fix | Effort |
|-----|----------|----------|-------|---------------|--------|
| 🔴 | security | `src/laivelup/team.py:54-58` | Symlink check on parent only — attacker could replace `.laivelup/teams/` with symlink to sensitive dir before `save_team()` runs, then `mkdir(parents=True)` traverses into target | Check `target.parent.resolve()` is under CWD *after* mkdir, or use `os.symlink` guard on each component | M |
| 🟡 | security | `src/laivelup/schemas/profile.schema.json:85-91` | `answers` and `meta` have `additionalProperties: true` — arbitrary keys accepted, no schema contract. Prototype pollution payload (`{"__proto__":{"admin":true}}`) passes validation silently | Restrict to known keys or add `maxProperties` bound; keep `additionalProperties: false` like root and `traces` | S |
| 🟡 | security | `src/laivelup/report.py:1013,1019` | Report files written non-atomically — interrupted write leaves partial HTML/MD on disk. Adjacent tools reading the file may consume corrupted output | Use `tempfile.NamedTemporaryFile` + `os.replace()` pattern (same as `team.py:78-91`) | S |
| 🟡 | security | `src/laivelup/calibrate_core.py:44-54` | `_load_profile()` skips JSON Schema validation (no `validate_profile()` call). Calibration profiles are repo-internal, but a corrupted `expected.json` or modified profile file could inject malformed data silently | Add `validate_profile()` call or document the trust boundary explicitly | S |
| 🟢 | security | `pyproject.toml:159` | Bandit skips B601 (subprocess shell) but no `shell=True` is used anywhere — the skip is unnecessary and may mask future regressions | Remove B601 from `skips` list | S |
| 🟢 | security | `.github/workflows/aidd-eval.yml:103-106` | PR comment escaping handles `\` `` ` `` `$` but not `${...}` with nested backticks or Unicode escape sequences. `verdict.md` is repo-generated (low risk), but defense-in-depth could be tighter | Use `github.rest.issues.createComment` with a pre-sanitized payload, or apply JSON.stringify-style escaping | S |
| 🟢 | security | `src/laivelup/team.py:54-58` | Symlink check uses `is_symlink()` before `mkdir` — TOCTOU gap between check and write. Mitigated by atomic write pattern but not eliminated | Replace with `resolve()`-based containment check after write | S |
| 🟢 | security | `src/laivelup/report.py` | No Content-Security-Policy or X-Frame-Options headers in generated HTML. Acceptable for local CLI output but limits safe embedding if reports are served | Add `<meta http-equiv="Content-Security-Policy">` to static HTML | S |

## Top actions

1. **Replace symlink check with resolve-based containment** (`team.py:54-58` + `team.py:78-91`). After `mkdir` and before `tmp_path.replace(target)`, assert `target.resolve().is_relative_to(cwd.resolve())`. This closes the TOCTOU + symlink vector. Effort: S. Skill: refactor.

2. **Restrict `answers`/`meta` in profile schema** (`profile.schema.json:85-91`). Either set `additionalProperties: false` or add `maxProperties`. Prevents unbounded key injection. Effort: S. Skill: refactor.

3. **Atomicize report writes** (`report.py:1013,1019`). Copy the `tempfile.NamedTemporaryFile` + `os.replace()` pattern from `team.py`. Prevents partial-file consumption. Effort: S. Skill: refactor.

## Coverage

- **Scanned**: security
- **Skipped**: none (single-pillar audit)
