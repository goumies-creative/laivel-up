My confidence level of correctness now: 85%

# Correctness (100%)

- The central claim holds and is not a guess: `coverage.py` has no `[overrides]` section in any released version. Verified against the installed 7.11.3 `config.py` and upstream at tags 7.4.0, 7.5.0, 7.6.0, 7.9.0, 7.10.0, 7.11.3 — zero occurrences. `[overrides]` is parsed silently and discarded, even under `-W error`, which is why it went unnoticed for so long.
- The gate is real, not decorative. I ran it: 228 statements, 0 missing, 120 branches, 0 partial, exit 0. An independent reviewer injected a probe and observed exit 1 naming the gap, then reverted it. A gate observed failing is a gate; the previous config was never observed failing because it never ran.
- The global gate is untouched at 87.66% ≥ 85%, and `--cov-fail-under=85` plus `[tool.coverage.run] source` are byte-identical. The change removes a fiction without moving any other number.
- The `if tails:` removal is behaviour-preserving. The invariant that makes the false arm unreachable is now stated correctly: `scoring_defaults` reads `GRID.cells[level.id]['size']` at import, so a grid lacking a `size` axis raises `KeyError` before `evaluate()` is callable. Verified by probing alternate grids.
- Constraints held: `.pre-commit-config.yaml` unchanged, no `pragma` added to `scoring.py`, no level-calculation or grid change, `security`/`install` CI jobs untouched.
- Two runs are the minimum, not ceremony: one pytest run has exactly one coverage `source`, so two thresholds over two scopes cannot share a run.

# Deal breakers

- None blocking this pull request.
- Blocking for the repository, pre-existing and out of scope for #11: the `pytest-fast` pre-commit hook destroys the git index on every run. `tests/test_team_rgpd.py::test_generate_profile_strip_emails_auteurs` executes `git init` + `git add .` inside a temp directory, and pre-commit exports `GIT_INDEX_FILE` pointing at the repository's real index, so the test overwrites it with its own one-entry index. Reproduced deterministically: index 31,718 bytes → 137 bytes, commit aborted, every tracked file appearing staged-deleted. Consequences beyond the aborted commit: `git status` and `git diff` return nonsense afterwards, which is enough to make an agent "discover" phantom whole-file rewrites and go fix healthy files. Both commits here were made with `--no-verify`; ruff, ruff-format, mypy and the full suite were run manually and pass, and CI does not invoke pre-commit, so the PR is not weakened. But the repo currently cannot be committed to through its own gate, and that needs its own issue before the next change lands.

# Suggestions (enhancements only)

- "The engine" means `scoring.py` alone. `scoring_defaults.py` holds `SCORING_DEFAULTS`, `SIZE_LEVEL`, `CONFIDENCE_THRESHOLD`, `CONFIDENCE_PEAK`, `RETRIES_PER_LEVEL` — the thresholds the engine decides with — and sits at **81%** (`Missing: 48, 57, 59`, all grid-validation error paths in `_first_level_mentioning` and `_check_size_levels`). ADR-0009's own table says `scoring.py | 100%`, so this change is internally consistent and correct as written. But the parent Epic (#16) states the success criterion as "the coverage gate reaches 100% on the engine **package**", and a reader will reasonably read `scoring_defaults.py` as part of the engine. Widening the gate would fail today at 81% and needs its own scope and three more tests. That is a product decision, not an implementation detail, so it should be raised explicitly rather than absorbed here.
- The gate step can be skipped silently. `if: matrix.os == 'ubuntu-latest'` is correct today, but if the matrix `os` labels are ever renamed the step vanishes and nothing fails — a skipped gate is exactly the failure class this issue exists to end. A cheap guard would be a job-level assertion that the gate ran at least once.
- `docs/backlog.md` is still untracked and still asserts the original premise for items other than #5. Whoever stages it next will import stale, disproved claims into the repository.
