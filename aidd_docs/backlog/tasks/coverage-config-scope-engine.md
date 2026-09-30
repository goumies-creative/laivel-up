---
type: task
status: proposed
source: https://github.com/goumies-creative/laivel-up/issues/11
---

# Task: Coverage config: scope to engine only, fix path

## Outcome

The 100% coverage gate on the scoring engine is actually enforced, and the engine genuinely reaches it.

## Context

Issue #11 was written on a false premise. Frame verified the following against the installed toolchain (`coverage` 7.11.3) and upstream `coverage/config.py` at tags 7.4.0, 7.5.0, 7.6.0, 7.9.0, 7.10.0 and 7.11.3:

- **coverage.py has no `[overrides]` feature.** The string `overrides` appears zero times in `config.py` at every one of those versions. The `[[tool.coverage.overrides]]` block in `pyproject.toml:160-162` is parsed silently — no warning, even under strict parsing — and then discarded.
- **The 100% gate has therefore never been enforced.** `coverage debug config` reports `fail_under: 0.0` and no override machinery. The only live threshold is pytest-cov's `--cov-fail-under=85` CLI flag (`pyproject.toml:131`).
- **ADR-0009 is wrong on this point.** `docs/adr/0009-couverture-scoring-100-autres-85-branch.md:33-35` specifies the overrides block as its implementation, so the ADR describes a mechanism that does not exist. The audit at `aidd_docs/tasks/2026_08/2026_08_31_audit/ce-testing.md:26,153` marks "scoring.py = 100% (override)" as verified; that claim rests on the dead config.
- **The engine is at 99%, not 100%.** `src/laivelup/scoring.py` reports `Missing: 122, 400->409`:
  - Line 122 is `value = int(value)` — the branch taken when a float *is* integral (e.g. `3.0`). No test covers it; `tests/test_scoring.py:291` covers only the rejected `3.7` case.
  - Branch `400->409` is the false arm of `if tails:`. `AXES` is `GRID.axis_ids` (`src/laivelup/model.py:56`), loaded at import from `grille/aidd.md` and overridable via `LAIVELUP_GRID` — so it is not a fixed constant. `'size'` is nevertheless guaranteed to be present: `scoring_defaults._check_size_levels` reads `GRID.cells[level.id]['size']` at import, so a grid lacking a `size` axis raises `KeyError` while the module loads, before `evaluate()` is callable. This arm is structurally unreachable, not merely untested.

Consequence: the issue's stated cause ("override module path is wrong", "scripts dilute to ~89%") does not hold, and its proposed fix ("add a separate override") cannot work. The real defect is a gate that asserts something it does not do — the exact failure class the parent Epic (#16) exists to correct.

## Decisions

Both decisions were taken by Romy Alula on 2026-09-30.

| Decision | Choice | Rejected alternative |
|---|---|---|
| Gate mechanism | A dedicated coverage pass scoped to `src/laivelup/scoring.py` at `--cov-fail-under=100`, alongside the existing global 85% pass | Amending ADR-0009 to drop the 100% mandate |
| Gap closure | Extend scope: add the missing line-122 test, and remove the unreachable `if tails:` guard | A `# pragma: no branch`, which would relax ADR-0009's ban on pragmas over business logic |

## Scope

- Includes:
  - `pyproject.toml` — remove the dead `[[tool.coverage.overrides]]` block.
  - `.github/workflows/ci.yml` — add the engine-scoped coverage gate as its own step in the `test` job.
  - `tests/test_scoring.py` — one test covering the integer-valued float at `scoring.py:122`.
  - `src/laivelup/scoring.py` — remove the unreachable `if tails:` guard at line 400.
  - `docs/adr/0009-couverture-scoring-100-autres-85-branch.md` — correct the Implementation section to describe the mechanism that actually works.
  - A note in the ADR recording that `[overrides]` was never a coverage.py feature.
- Wiring notes, established by probing the toolchain:
  - The gate belongs in CI only. `.pre-commit-config.yaml:22-27` runs a fast subset with `--no-cov` by design; adding a full-suite coverage pass there contradicts that design and costs ~97s per commit.
  - The engine gate must run the **full** suite. Scoped to only `tests/test_scoring*.py`, it reports a third gap, `scoring.py:187` — the refusal arm `if isolated_peak and dominant == max_present:` — which other tests cover. Line 187 is the refusal-to-decide path the parent Epic names as the product's core strength, so it must stay covered, never excluded.
  - The flag is module form `--cov=laivelup.scoring`. The path form `--cov=src/laivelup/scoring.py` silently collects no data, reports 0%, and fails with a `module-not-imported` warning rather than an obvious error.
- Excludes:
  - Any change to level calculation or the level grid, per the parent Epic's boundary.
  - Raising or removing the global 85% threshold.
  - Coverage work on any other module.
  - The `socle-qualite` worktree.
- Scope was widened from the original issue, which excluded source and test changes while requiring a passing 100% gate — a contradiction, since the only ways to close those two gaps are a test and a source edit.

## Done When

- The `[[tool.coverage.overrides]]` block is gone from `pyproject.toml`.
- A CI step runs the full suite with `--cov=laivelup.scoring --cov-branch --cov-fail-under=100` and passes.
- `src/laivelup/scoring.py` reports 100% statements **and** 100% branches, with no `Missing` lines.
- The gate is proven live, not assumed: introducing a temporary untested branch in `scoring.py` makes that step fail, then is reverted.
- `scoring.py:187` (the refusal arm) remains covered, and no `pragma: no cover` is added anywhere in `scoring.py`.
- The existing global gate still passes at `--cov-fail-under=85`, with that threshold and the `[tool.coverage.run] source` list unchanged.
- `.pre-commit-config.yaml` is unchanged.
- ADR-0009's Implementation section describes a mechanism that exists and can be run.

## Completion Evidence

- `pytest -o addopts="" --cov=laivelup.scoring --cov-branch --cov-fail-under=100 --cov-report=term-missing` showing 100% and `Required test coverage of 100% reached`.
- The same command's output before the fix, showing `Missing: 122, 400->409` and a non-zero exit, recorded as the before state.
- Output of `coverage debug config` confirming no override machinery and `fail_under: 0.0` from the config file itself.
- A recorded negative check: a temporary untested branch in `scoring.py` fails the engine pass, then is reverted.
- The unchanged global run showing `Required test coverage of 85% reached`.

## Cancellation

No longer pursued if the coverage strategy is redesigned or the engine package structure changes — in particular if `scoring.py` is split into a package, which changes the scope path the pass targets.
