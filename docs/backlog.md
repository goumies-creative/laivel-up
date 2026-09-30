# Backlog — laivelup-rebuild/bugs-jury

Scope: worktree `laivelup-rebuild/bugs-jury` (issue #<numéro>)
Authority: this worker owns these files for this run.
Constraint: do not touch `socle-qualite` worktree; do not change level calculations — only detection, display, and robustness.

---

## 1. Next-step text per axis with own threshold + sub-grid floor

**Artifact:** User Story  
**Operation:** create  
**Owner:** scoring / report rendering  
**Before:** `progress_for_axis()` in `scoring.py` returns only the blocking axis step; `_render_pedagogical_section()` in `report.py` shows "Comment monter d'un cran" only for limiting axis; Level.WHITE has no "lower" step text.  
**After:** Each of the 4 axes gets its own "next step" text keyed to its current level; add a step below WHITE so beginners never see "Maintenir le niveau actuel".  
**Evidence:** User request item 1; `scoring.py:306-340`, `report.py:824-968`.  
**Acceptance:** Two profiles at same level/axis receive different text for at least one of the 4 axes.

---

## 2. Explicit "no alert" banner label

**Artifact:** User Story  
**Operation:** create  
**Owner:** report rendering (red flags section)  
**Before:** `_render_red_flags()` in `report.py:545-565` shows "AUCUNE ALERTE" with no explanation.  
**After:** Banner reads "Aucune contradiction entre déclaré et observé" (the two rules triggering it require ≥ Blue, which no official profile carries).  
**Evidence:** User request item 2; `scoring.py:272-303` (red flag rules).  
**Acceptance:** "Aucune alerte" banner has explicit on-screen label explaining the two rules.

---

## 3. Whole-word declared-level detection, scoped to level question only

**Artifact:** Defect  
**Operation:** update  
**Owner:** CLI interrogate merge (`cli_interrogate.py:133-137`)  
**Before:** `_LEVELS_BY_KEYWORD` matched via `\bword\b` but could fire on substrings in free text (e.g., "redonner" → Red, "ouvert" → Green via "vert").  
**After:** Match whole word only, and only when the current question is `DECLARED_LEVEL` (already gated); ensure regex handles French accents correctly.  
**Evidence:** User request item 3; `cli_interrogate.py:54-67, 133-137`.  
**Acceptance:** "redonner" in declarative answer no longer triggers Red; "ouvert" no longer triggers Green.

---

## 4. Parallel axis: count only completed projects

**Artifact:** Defect  
**Operation:** update  
**Owner:** scoring (`parallel_max` in `scoring.py:243-266`)  
**Before:** `parallel_max` uses `parallel_projects` (active branches) for gate at n≥3; `projects_completed` only refines confidence, not the level gate.  
**After:** Level ≥ Copper requires `projects_completed ≥ 3` (not just `parallel_projects ≥ 3`). Profile with 4 finished / 2 open no longer passes incorrectly.  
**Evidence:** User request item 4; `scoring.py:243-266`.  
**Acceptance:** Profile with 3 repos touched but 0 completed does not pass parallel gate.

---

## 5. Coverage config: scope to engine only, fix path

**Artifact:** Task  
**Operation:** update  
**Owner:** pyproject.toml coverage overrides  
**Before:** ~~Override module path to the exact engine package; remove scripts from coverage source or add separate override.~~ **This framing was wrong.** coverage.py has no `[overrides]` section in any released version, so the block was read, never warned about, and silently discarded — the 100% gate never ran. The engine sat at 99% (`Missing: 122, 400->409`) behind the only live threshold, the global `--cov-fail-under=85`.  
**After:** The dead block is deleted and a real engine-scoped pass is added as its own CI step — `--cov=laivelup.scoring --cov-branch --cov-fail-under=100` over the full suite. The two real gaps are closed: a test for the integral float at `scoring.py:122`, and removal of the `if tails:` guard, whose false arm is unreachable because `AXES` always contains `size`.  
**Evidence:** User request item 5; `pyproject.toml:143-162`; verified against `coverage` 7.11.3 and upstream tags 7.4.0–7.11.3. ADR-0009 corrected.  
**Acceptance:** Coverage gate measures engine precisely and hits 100%.

---

## 6. calibrate_degraded.py exit on blocking + aidd-eval.yml always comment

**Artifact:** Defect (calibrate) + Task (workflow)  
**Operation:** update  
**Owner:** `scripts/calibrate_degraded.py::main()`, `.github/workflows/aidd-eval.yml`  
**Before:** `calibrate_degraded.py` computes `diag.summary["blocking"]` but never reads it → always exits 0. `aidd-eval.yml` Comment PR step runs only on `pull_request` event, skipping on `workflow_dispatch` and some verdicts.  
**After:** `main()` reads `diag.summary["blocking"]` and `sys.exit(1)` if true. Workflow step "Comment PR" gets `if: always()` like Upload artifacts.  
**Evidence:** User request item 6; `scripts/calibrate_degraded.py:200-244`, `.github/workflows/aidd-eval.yml:94-149`.  
**Acceptance:** Simulated error in calibrate_degraded fails CI job; PR comment appears even on UNDECIDED verdict.

---

## 7. Fix double HTML escaping + make 10 tests portable

**Artifact:** Defect (escaping) + Task (test portability)  
**Operation:** update  
**Owner:** `report.py` (HTML rendering), test files with env deps  
**Before:** Apostrophes rendered as `'` on screen (double escape via `html.escape` + template). 10 tests depend on Windows: 2 call `python` directly, 8 rely on Windows snapshot captures.  
**After:** Single escape only; replace `python` with `sys.executable` in 2 tests; isolate or rebuild 8 Windows-dependent snapshots for Linux CI.  
**Evidence:** User request item 7; `report.py:27` (import), HTML templates; test suite.  
**Acceptance:** No double-escaped apostrophes in HTML; all 10 tests pass on Linux CI.

---

## 8. Harmonize ci_evaluate.py exit codes (0/1/2 discipline)

**Artifact:** Defect  
**Operation:** update  
**Owner:** `scripts/ci_evaluate.py`  
**Before:** Returns 2 (cli.py: "validation error") for UNDECIDED verdict — not an error, causes jury-6 silence.  
**After:** Follow winner's discipline: 0 = report produced even without proven level, 1 = tool broken, 2 = bad caller usage. UNDECIDED → 0 with report.  
**Evidence:** User request item 8; `scripts/ci_evaluate.py:90`, `cli.py:18-22`.  
**Acceptance:** `ci_evaluate.py` never returns 2 for legitimate UNDECIDED; exit codes match cli.py semantics.