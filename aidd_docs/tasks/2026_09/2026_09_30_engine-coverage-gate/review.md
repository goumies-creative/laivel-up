# Review: Make the engine coverage gate real (issue #11, `a7973a4`)

- **Verdict**: approve
- **Diff**: `a7973a4` (base `3994fb6`) — 13 files, +575/-18
- **Axes run**: code, fit, conform, rot, functional
- **Date**: 2026-09-30
- **Findings**: 7 (0 blocker, 0 critical, 0 major, 4 minor, 3 suggestion)

## Phases

**Phase 1 — Close the engine's real coverage gaps** (`phase-1.md`)

- [x] `3.0` on an integer trace key raises no validation error and `scoring.py:122` leaves `Missing` — `tests/test_scoring.py:303`; single-test run reports `Missing: 55, 58-63, 82, 86-91, 97-105, 111, 117, 124, ...` and 122 is absent.
- [x] Pre-existing `3.7` rejection test still passes unchanged — `tests/test_scoring.py:290`.
- [x] `400->409` no longer appears because the branch no longer exists — `src/laivelup/scoring.py:401`; gate reports empty `Missing`.
- [x] Variance annotation for an isolated `pr_sizes` peak still applied — `tests/test_scoring_edge.py:335` (`test_variance_signal`, 1 passed).
- [x] Engine gate reports 100% statements **and** branches, empty `Missing`, exit 0 — `src/laivelup/scoring.py` at 228 stmts / 0 miss, 120 branch / 0 partial.
- [x] No `pragma: no cover` added in `scoring.py` — `src/laivelup/scoring.py` (grep: none).

**Phase 2 — Remove the dead override, wire the gate** (`phase-2.md`)

- [x] `pyproject.toml` contains no `tool.coverage.overrides` — `pyproject.toml:143` (only `[[tool.mypy.overrides]]` at `:118`, `:122` remain).
- [x] `pytest -q` still reaches 85% and `[tool.coverage.run] source` still lists both paths — `pyproject.toml:131` and `pyproject.toml:143`; run ends `Required test coverage of 85% reached. Total coverage: 87.66%`, exit 0.
- [x] `test` job carries the gate step with `-o addopts=""`, `--cov=laivelup.scoring`, `--cov-branch`, `--cov-fail-under=100` — `.github/workflows/ci.yml:48`.
- [x] That step's command, run locally, exits 0 at 100% — `.github/workflows/ci.yml:49`.
- [x] `.pre-commit-config.yaml` byte-identical — `git diff 3994fb6 a7973a4 -- .pre-commit-config.yaml` is empty.
- [x] With a temporary untested branch the gate exits non-zero and names it — probe appended `_REVIEW_PROBE = False / if _REVIEW_PROBE:`; output `Missing: 461`, `Coverage failure: total of 99 is less than fail-under=100`, exit 1.
- [x] After reverting, the gate exits 0 again — file restored via `git checkout --`, sha256 `215128ed…` matches the pre-probe hash, re-run `Required test coverage of 100% reached`, exit 0.
- [x] `coverage debug config` reports `fail_under: 0.0` and no override machinery — `pyproject.toml:143` (post-removal).

**Phase 3 — Correct ADR-0009** (`phase-3.md`)

- [x] Implémentation section carries no `[tool.coverage.overrides]` snippet presented as working — `docs/adr/0009-couverture-scoring-100-autres-85-branch.md:26`.
- [x] Every command named there runs, both gates named with exact flags — `docs/adr/0009-couverture-scoring-100-autres-85-branch.md:31` (global) and `:47` (engine), with their reproduced console output at `:44` and `:57`; both reproduced verbatim by me.
- [x] ADR states plainly there is no `[overrides]` section and names the versions checked — `docs/adr/0009-couverture-scoring-100-autres-85-branch.md:76`.
- [x] Décision table, Status, Date, Décideurs identical — `docs/adr/0009-couverture-scoring-100-autres-85-branch.md:3`.
- [x] `ce-testing.md` carries a dated correction, original rows intact — `aidd_docs/tasks/2026_08/2026_08_31_audit/ce-testing.md:218`; diff is a pure append, `:26` and `:153` byte-identical.

## Findings

| Sev | Kind | Phase | Location | Issue | Fix |
|---|---|---|---|---|---|
| minor | rot | 1 | `src/laivelup/scoring.py:399`, `aidd_docs/backlog/tasks/coverage-config-scope-engine.md:22`, `plan.md:43` | "AXES is a fixed 4-tuple that always contains 'size'" is wrong as stated: `AXES = GRID.axis_ids` (`model.py:56`) is loaded at import from `grille/aidd.md`, overridable via `LAIVELUP_GRID` (`grid_doc.py:26`). The conclusion holds — I probed it — but the code comment's reason ("sinon `scorers[axe]` a déjà levé au-dessus") only proves `AXES ⊆ scorers.keys()`, not `'size' ∈ AXES`. | Cite the two invariants that actually hold: any grid with ≠4 axes fails at load (`GridError`, display/machine divergence), and any grid whose 4 ids are not exactly `{size, harness, intervention, parallel}` dies at import with `KeyError: 'size'` (`scoring_defaults.py:46`). |
| minor | rot | 2 | `aidd_docs/tasks/.../coverage-config-scope-engine.md:45`, `plan.md:42`, `ci.yml` comment, `docs/adr/0009-…:104` | One measurement, four figures: `~97s`, `~90s` (commit message), `~100 s` (ADR), measured `69.56s` / `75.83s` / `79.09s` locally. | Quote one measured number and say on which runner/OS. |
| minor | rot | 2 | `aidd_docs/tasks/2026_09/2026_09_30_engine-coverage-gate/plan.md:41` | Cites the mutmut `-o addopts=` escape hatch at `pyproject.toml:184`; it is at `pyproject.toml:180` (file is 180 lines). | Fix the line reference. |
| minor | rot | — | `docs/backlog.md:3`, `docs/backlog.md:61` | Header ships the literal placeholder `issue #<numéro>`, and item 5 still names `pyproject.toml coverage overrides` as `**Owner**` although that block is deleted by this same commit. | Fill in `11`; re-own the item to the CI gate step. |
| suggestion | code | 1 | `tests/test_scoring.py:304` | `assert not verdict.decided` is vacuous. Verified: `evaluate` returns `decided=False` for `{}`, `{'parallel_projects': 0}` and `{'parallel_projects': 3.0}` alike — any single-trace profile refuses. It is copied from the rejection test at `:293` and carries no signal about float handling. | Delete it, or replace it with an assertion on the parallel axis (`axis_scores`) that distinguishes acceptance from refusal. |
| suggestion | code | 1 | `tests/test_scoring.py:298` | Docstring claims "3.0 doit être accepté et **ramené à int**", but the coerced value is a local in `normalize_profile` (`:122`) and never surfaces. Mutation check: replacing `value = int(value)` with `value = value` leaves the test green. | Reword to the assertion actually made ("aucune erreur de validation pour cette clé"), or expose the normalised value if the coercion is meant to be observable. |
| suggestion | fit | 2 | `.github/workflows/ci.yml:48` | The gate duplicates a full suite run on all 9 matrix cells (3 OS × 3 Python), doubling the `test` job's wall time on every PR. The cost is disclosed in the ADR (`:104`), so it is honest, not hidden — but per-OS repetition buys nothing for a line/branch threshold. | Add `if: matrix.os == 'ubuntu-latest'` (or one cell) to the gate step; keep all three Python versions, where branch coverage can genuinely differ. |

## Verification

| Verified | Files checked | Unchecked | Unplanned |
|---|---|---|---|
| **1. PASS** — coverage 7.11.3 `config.py`: `overrides` occurs **0** times; the only case-insensitive hits are 4 mypy `type: ignore[override]` comments. `coverage debug config` shows `fail_under: 0.0` and no override machinery. At base `3994fb6` (block present) `debug config` also shows `fail_under: 0.0` and emits no warning, even under `-W error` — silently discarded, as claimed. | `pyproject.toml`, `src/laivelup/scoring.py`, `tests/test_scoring.py` | The 6 upstream tags (7.4.0→7.11.3) were not fetched; only the installed 7.11.3 was checked. Consistent with my knowledge of coverage.py, but not independently confirmed. | none |
| **2. PASS** — `572 passed, 1 skipped`; `scoring.py 228 stmts 0 Miss, 120 branch 0 BrPart, 100%`, `Missing` empty, `Required test coverage of 100% reached`, exit 0. | `src/laivelup/scoring.py` | — | — |
| **3. PASS** — `Required test coverage of 85% reached. Total coverage: 87.66%`, `scoring.py` at 100% inside the global run too, exit 0. | `pyproject.toml` | — | — |
| **4. PASS** — probe (`_REVIEW_PROBE = False` + `if _REVIEW_PROBE:`) → `scoring.py 231 stmts 1 Miss 99% Missing: 461`, `FAIL Required test coverage of 100% not reached`, **exit 1**. Reverted with `git checkout --`; sha256 back to `215128ed…`, `git diff` and `git status` clean. | `src/laivelup/scoring.py` | — | — |
| **5. PASS** — `StopIteration` is unreachable in practice. Probed three grids: base loads (`AXES=('size','harness','intervention','parallel')`); a 3-axis grid dies at load with `GridError` (display/machine divergence pins the count to 4); a grid with `size` renamed dies at import with `KeyError: 'size'` (`scoring_defaults.py:46`). Verdict output is unchanged: the dedented body is still gated by `isinstance(pr_sizes, list) and pr_sizes`, and `test_variance_signal` (`tests/test_scoring_edge.py:335`) still passes. | `src/laivelup/scoring.py`, `src/laivelup/model.py`, `src/laivelup/grid_doc.py`, `src/laivelup/scoring_defaults.py`, `tests/test_scoring_edge.py` | — | — |
| **6. PASS with reservations** — the test genuinely executes `scoring.py:122` (122 absent from `Missing` in a single-test run). Its `data_errors` assertion is load-bearing: inverting `if not value.is_integer()` makes it fail. But the `decided` assertion is vacuous and the coercion itself is unobservable (see Findings). | `tests/test_scoring.py:288-307`, `src/laivelup/scoring.py:107-127` | — | Mutation testing of the new test (2 mutants, in a scratch copy under `%TEMP%`, repo untouched). |
| **7. PASS** — `.pre-commit-config.yaml` unchanged; no `pragma` in `scoring.py`; `[tool.coverage.run] source = ["src/laivelup", "scripts"]` unchanged; `addopts … --cov-fail-under=85` unchanged; diff touches only the `test` job; no level-calculation or level-grid file in the diff (`grille/aidd.md`, `model.py` untouched). | `pyproject.toml`, `.pre-commit-config.yaml`, `.github/workflows/ci.yml`, `src/laivelup/scoring.py` | — | — |
| **8. PASS** — YAML parses; the step is the 5th step of the `test` job, after `Test`, before the `security` job. Command works as written. The cost is acknowledged in the ADR (`~100 s`, "sur 3 OS × 3 Python", `:104`) and reasoned in the commit message. Caveats: it drops `--strict-markers`/`--strict-config` with the rest of `addopts` (immaterial — the preceding `Test` step still enforces them), and it re-runs the whole suite per matrix cell (see Findings). | `.github/workflows/ci.yml`, `docs/adr/0009-couverture-scoring-100-autres-85-branch.md:102-104` | Actual GitHub Actions wall time (measured on Windows locally, not on runners). | — |
| **9. PASS** — `ruff check src/ tests/` → `All checks passed!`; `ruff format --check` → `62 files already formatted`; `mypy src/` → `Success: no issues found in 22 source files`. | `src/`, `tests/` | — | — |
| **10. PASS** — ADR-0009 now describes only commands I ran and reproduced, and its `Status`/`Date`/`Décideurs`/`Décision` are untouched; its updated figures (`~573 tests`, `~88%`) match what I measured. The audit correction is append-only (`:218` onward); original rows `:26` and `:153` intact. `docs/backlog.md:62-63` strikes the wrong framing through and states the correction, so the disproved premise survives only as history. Side claims also verified: the path form yields `module-not-imported` + `0.00%` + exit 1, and a `tests/test_scoring*.py`-only run reports `Missing: 187`. | `docs/adr/0009-couverture-scoring-100-autres-85-branch.md`, `aidd_docs/tasks/2026_08/2026_08_31_audit/ce-testing.md`, `docs/backlog.md`, `aidd_docs/backlog/tasks/coverage-config-scope-engine.md` | — | — |
