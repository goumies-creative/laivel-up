---
status: pending
---

# Instruction: Close the engine's real coverage gaps

## Architecture projection

> Tree of the final files. ✅ create · ✏️ modify · ❌ delete

```txt
.
├── src/laivelup/scoring.py        ✏️ remove the unreachable `if tails:` guard at line 400
└── tests/test_scoring.py           ✏️ one test for the integer-valued float at scoring.py:122
```

Nothing is created or deleted in this phase. It changes two files so that `src/laivelup/scoring.py` reports 100% statements and 100% branches under the gate that phase 2 wires into CI.

## Test Scope

```mermaid
---
title: Test scope
---
journey
  %% Every task has exactly one actor: browser, api, cli, or system.
  section Setup
    {checkout the branch with a clean tree} => {scoring.py reachable as laivelup.scoring}: 1: cli
  section Happy path
    {run the full suite through the engine gate} => {scoring.py reports 100% statements and 100% branches, gate exits 0}: 5: cli
  section Edge case - integral float is accepted
    {evaluate a profile whose parallel_projects is the float 3.0} => {scoring.py:122 executes and no error is raised for that trace}: 5: cli
  section Edge case - non-integral float is still rejected
    {evaluate a profile whose parallel_projects is the float 3.7} => {the existing rejection still fires and the run still passes}: 5: cli
  section Teardown
    {revert nothing; confirm the working tree holds only the two intended edits} => {baseline restored to committed state}: 1: cli
```

## Tasks to do

### `1)` Add the missing test for an integral float

> `scoring.py:122` is `value = int(value)`, the arm taken when a float is already integral. It is uncovered today, and it is the only statement gap in the engine.

1. Open `tests/test_scoring.py` and find the existing B2 float case at lines 289-292, which passes `3.7` and expects rejection. Reuse its fixture and assertion style rather than inventing a new shape.
2. Add one sibling test that passes an integral float, `3.0`, through `evaluate` for the same trace key, and assert that no error is raised for that key — the value is coerced to `int`, not rejected.
3. Keep the existing `3.7` rejection test untouched. Both arms of the `is_integer()` branch must stay covered.
4. Do not add `pragma: no cover` anywhere, and do not widen the assertion into unrelated behaviour.

### `2)` Remove the unreachable `if tails:` guard

> `AXES` is `GRID.axis_ids` (`src/laivelup/model.py:56`) — grid-derived from `grille/aidd.md` and overridable via `LAIVELUP_GRID`, so not a fixed constant. `'size'` is still guaranteed present, because `scoring_defaults._check_size_levels` reads `GRID.cells[level.id]['size']` at import and a grid without a `size` axis raises `KeyError` before `evaluate()` is callable. So `axes` always holds a `size` entry and `tails` is never `None`. The false arm at line 400 is reported as the partial branch `400->409` and cannot execute.

1. Open `src/laivelup/scoring.py` at lines 399-407 and read the `tails = next(...)` / `if tails:` block that annotates variance from an isolated `pr_sizes` peak.
2. Replace the `if tails:` wrapper with its body dedented one level, so the variance annotation runs directly against the `size` axis score.
3. Keep the annotation's behaviour byte-for-byte identical for every profile that exercises it. This is a dead-branch removal, not a behaviour change.
4. Leave `scoring.py:187` alone. It is the refusal arm `if isolated_peak and dominant == max_present:` — reachable, product-critical, and covered by the wider suite. It must stay covered.

### `3)` Prove the engine is at 100% before any gate is wired

> The gate does not exist yet, so verify with the command phase 2 will encode.

1. Run `pytest -o addopts="" --cov=laivelup.scoring --cov-branch --cov-fail-under=100 --cov-report=term-missing`.
2. Read the report: `src/laivelup/scoring.py` must show 100% on both statements and branches, with an empty `Missing` column, and the run must exit 0 with `Required test coverage of 100% reached`.
3. If `Missing` still names anything, that line is a further real gap. Report it instead of suppressing it.

## Test acceptance criteria

| Task | Acceptance criteria                                                                                                                                                              |
| ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1    | Evaluating a profile carrying `3.0` for an integer trace key produces no validation error for that key, and `scoring.py:122` no longer appears in the report's `Missing` column.              |
| 1    | The pre-existing `3.7` rejection test still passes unchanged.                                                                                                                       |
| 2    | `400->409` no longer appears in the report's `Missing` column, because the branch no longer exists.                                                                              |
| 2    | Variance annotation for an isolated `pr_sizes` peak is still applied — an existing test covering that annotation still passes.                                                     |
| 3    | The engine gate command reports 100% statements and 100% branches for `src/laivelup/scoring.py` with no `Missing` entry, and exits 0.                                              |
| 3    | No `pragma: no cover` was added anywhere in `src/laivelup/scoring.py`.                                                                                                             |
