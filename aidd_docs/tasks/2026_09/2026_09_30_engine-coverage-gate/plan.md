---
objective: "The scoring engine's 100% coverage gate runs in CI, fails when it should, and the engine reports 100% statements and branches."
status: pending
---

# Plan: Make the engine coverage gate real

## Overview

| Field      | Value                                                                    |
| ---------- | ------------------------------------------------------------------------ |
| **Goal**   | Replace a coverage gate that never ran with one that enforces 100% on the scoring engine. |
| **Source** | [#11](https://github.com/goumies-creative/laivel-up/issues/11) · [`coverage-config-scope-engine.md`](../../../backlog/tasks/coverage-config-scope-engine.md) |

The repository claims its scoring engine is held at 100% coverage. It is not held at anything: the `[[tool.coverage.overrides]]` block that is supposed to do it is a feature coverage.py has never had, so it is parsed, ignored without a warning, and the engine has been sitting at 99% behind a global 85% gate. This plan makes the claim true or removes it, and corrects the ADR that documents the fiction.

## Phases

| #   | Phase                                     | File                                    |
| --- | ----------------------------------------- | --------------------------------------- |
| 1   | Close the engine's real coverage gaps      | [`phase-1.md`](./phase-1.md)            |
| 2   | Remove the dead override, wire the gate    | [`phase-2.md`](./phase-2.md)            |
| 3   | Correct ADR-0009                           | [`phase-3.md`](./phase-3.md)            |

## Resources

| Source                                                                                                                       | Verified                                                                                                                                                                                                                                                                                            |
| ---------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `coverage` 7.11.3 `config.py` (installed)                                                                                     | No `[overrides]` feature exists. `grep -c overrides` returns 0; the parsed config object exposes no override attribute. Confirmed the `[overrides]` section is silently discarded, with no warning even when a warning is requested.                                                                                                        |
| upstream `coverage/config.py` at tags 7.4.0, 7.5.0, 7.6.0, 7.9.0, 7.10.0, 7.11.3                                            | `overrides` occurs zero times at every tag, so the block was never valid at any version this project could have pinned.                                                                                                                                                                                                                                        |
| `python -m coverage debug config` (in this repo)                                                                              | `fail_under: 0.0`, no override machinery. The live threshold comes solely from pytest-cov's `--cov-fail-under=85` on the command line, never from the config file.                                                                                                                                                                                             |
| `pytest -o addopts="" --cov=laivelup.scoring --cov-branch --cov-fail-under=100` (full suite, probed)                     | Exits 1 with `Missing: 122, 400->409`, proving the module-form scoped gate works and fails as intended.                                                                                                                                                                                                                                                              |
| same command scoped to `tests/test_scoring*.py` only                                                                          | Additionally reports `187`, the refusal arm, which the wider suite covers. Confirms the gate must run the full suite.                                                                                                                                                                                                                                                   |
| `pytest ... --cov=src/laivelup/scoring.py` (path form)                                                                        | Collects nothing, reports `0.00%`, and exits non-zero with `module-not-imported` rather than an obvious usage error. Confirms module form is mandatory.                                                                                                                                                                                                                   |
| `coverage` documentation, messages index 7.11.3                                                                                | Resolved the two warnings observed during probing (`module-not-imported`, `no-data-collected`) to a bad `--cov` value rather than a broken test suite.                                                                                                                                                                                                                    |

## Decisions

| Decision                                                                       | Why                                                                                                                                                                   |
| ------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Enforce the engine gate as a separate CI step rather than a second `--cov` flag in the shared pytest `addopts` | A single pytest run has one coverage `source`. Two thresholds against two different scopes need two runs. `-o addopts=""` on the gate step is the same escape hatch the mutmut runner already uses at `pyproject.toml:184`. |
| Leave the gate out of `.pre-commit-config.yaml`                                  | That hook is a deliberate fast subset running `--no-cov` (`.pre-commit-config.yaml:22-27`). A full-suite coverage pass costs ~97s per commit and would work against its design. CI is where the global 85% gate already runs. |
| Remove the unreachable `if tails:` guard instead of excluding the branch        | `AXES` is grid-derived (`GRID.axis_ids`, `src/laivelup/model.py:56`), not a fixed constant, but `'size'` cannot be absent at runtime: `scoring_defaults._check_size_levels` reads `GRID.cells[level.id]['size']` at import, so a grid without a `size` axis raises `KeyError` before `evaluate()` is callable. ADR-0009 bans `pragma` over business logic, and the honest fix for unreachable code is to delete it. |
| Test `scoring.py:122` through the public `evaluate` entry point                  | The existing sibling case at `tests/test_scoring.py:291` already asserts the rejected `3.7` float that reaches this code, so the fixture and assertion style already exist.      |
| Leave `[tool.coverage.run] source` and the global 85% threshold untouched        | ADR-0009 scopes the 85% floor to `src/`; changing the source list would silently move the global baseline, which is a decision beyond this ticket.                                          |
