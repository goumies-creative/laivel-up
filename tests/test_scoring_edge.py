# Copyright 2026 Romy Alula — MIT License
"""Tests scoring.py : cas manquants — erreurs, bornes, edge cases, red flags.

Cible : 100% branch coverage sur scoring.py.
"""

from __future__ import annotations

import pytest

from laivelup.model import Level, ProfileData
from laivelup.scoring import (
    _as_float,
    _as_int,
    _peak_info,
    _questions_for,
    detect_red_flags,
    evaluate,
    normalize_profile,
    parallel_max,
    progress_for_axis,
)


# --- _as_float / _as_int — exception paths ----------------------------


class TestAsFloatAsInt:
    def test_as_float_returns_none_on_value_error(self):
        assert _as_float("not_a_number") is None

    def test_as_float_returns_none_on_type_error(self):
        assert _as_float([1, 2, 3]) is None

    def test_as_float_converts_string_number(self):
        assert _as_float("3.14") == pytest.approx(3.14)

    def test_as_int_returns_none_on_value_error(self):
        assert _as_int("abc") is None

    def test_as_int_returns_none_on_type_error(self):
        assert _as_int({"key": "val"}) is None

    def test_as_int_converts_string_int(self):
        assert _as_int("42") == 42


# --- normalize_profile — error branches -------------------------------


class TestNormalizeProfileErrors:
    def test_traces_not_dict(self):
        p = ProfileData(name="x", traces="not a dict")
        errors = normalize_profile(p)
        assert any("must be an object" in e for e in errors)

    def test_pr_sizes_not_list(self):
        p = ProfileData(name="x", traces={"pr_sizes": "S"})
        errors = normalize_profile(p)
        assert any("pr_sizes must be a list" in e for e in errors)

    def test_pr_sizes_invalid_value(self):
        p = ProfileData(name="x", traces={"pr_sizes": ["S", "XXL"]})
        errors = normalize_profile(p)
        assert any("XXL" in e for e in errors)

    def test_retries_bool_is_error(self):
        p = ProfileData(name="x", traces={"retries_after_fact": True})
        errors = normalize_profile(p)
        assert any("retries_after_fact must be a number" in e for e in errors)

    def test_retries_out_of_range(self):
        p = ProfileData(name="x", traces={"retries_after_fact": 1.5})
        errors = normalize_profile(p)
        assert any("ratio between 0 and 1" in e for e in errors)

    def test_retries_non_numeric(self):
        p = ProfileData(name="x", traces={"retries_after_fact": "abc"})
        errors = normalize_profile(p)
        assert any("must be a number" in e for e in errors)

    def test_parallel_projects_bool(self):
        p = ProfileData(name="x", traces={"parallel_projects": True})
        errors = normalize_profile(p)
        assert any("parallel_projects" in e and "integer" in e for e in errors)

    def test_parallel_projects_negative(self):
        p = ProfileData(name="x", traces={"parallel_projects": -1})
        errors = normalize_profile(p)
        assert any("non-negative" in e for e in errors)

    def test_parallel_projects_not_int(self):
        p = ProfileData(name="x", traces={"parallel_projects": "abc"})
        errors = normalize_profile(p)
        assert any("parallel_projects" in e and "integer" in e for e in errors)

    def test_projects_completed_bool(self):
        p = ProfileData(name="x", traces={"projects_completed": False})
        errors = normalize_profile(p)
        assert any("projects_completed" in e and "integer" in e for e in errors)

    def test_declared_level_unknown(self):
        p = ProfileData(name="x", declared_level="PLATINUM")  # type: ignore[arg-type]
        errors = normalize_profile(p)
        assert any("unknown level" in e for e in errors)

    def test_adoption_signal_not_bool(self):
        p = ProfileData(name="x", traces={"context_versioned": "yes"})
        errors = normalize_profile(p)
        assert any("context_versioned must be a boolean" in e for e in errors)

    def test_agent_rules_not_bool(self):
        p = ProfileData(name="x", traces={"agent_rules_versioned": 1})
        errors = normalize_profile(p)
        assert any("agent_rules_versioned must be a boolean" in e for e in errors)

    def test_retry_loops_not_bool(self):
        p = ProfileData(name="x", traces={"retry_loops": "true"})
        errors = normalize_profile(p)
        assert any("retry_loops must be a boolean" in e for e in errors)

    def test_prompts_not_bool(self):
        p = ProfileData(name="x", traces={"prompts": []})
        errors = normalize_profile(p)
        assert any("prompts must be a boolean" in e for e in errors)

    def test_agents_autonomous_not_bool(self):
        p = ProfileData(name="x", traces={"agents_autonomous": 1})
        errors = normalize_profile(p)
        assert any("agents_autonomous must be a boolean" in e for e in errors)

    def test_retries_triangulated_not_bool(self):
        p = ProfileData(name="x", traces={"retries_triangulated": "yes"})
        errors = normalize_profile(p)
        assert any("retries_triangulated must be a boolean" in e for e in errors)

    def test_no_errors_on_valid_profile(self):
        p = ProfileData(
            name="valid",
            traces={"pr_sizes": ["S", "M"], "retries_after_fact": 0.3},
        )
        assert normalize_profile(p) == []


# --- _peak_info edge case ---------------------------------------------


class TestPeakInfo:
    def test_empty_list(self):
        assert _peak_info([]) == (None, 0.0)


# --- progress_for_axis with None level --------------------------------


class TestProgressForAxis:
    def test_none_level(self):
        result = progress_for_axis("size", None)
        assert len(result) == 1
        assert "données insuffisantes" in result[0]

    def test_known_axis_known_level(self):
        result = progress_for_axis("size", Level.RED)
        assert len(result) == 1
        assert "S" in result[0] or "M" in result[0]

    def test_unknown_axis(self):
        result = progress_for_axis("unknown", Level.RED)
        assert result == ["Maintenir le niveau actuel."]


# --- parallel_max edge cases ------------------------------------------


class TestParallelMaxEdgeCases:
    def test_completed_none_and_n_ge_3(self):
        p = ProfileData(name="x", traces={"parallel_projects": 5})
        level, conf, ev = parallel_max(p.traces)
        assert level == Level.GREEN
        assert conf < 0.5
        assert any("completion to confirm" in e for e in ev)

    def test_completed_less_than_n(self):
        p = ProfileData(name="x", traces={"parallel_projects": 5, "projects_completed": 2})
        level, conf, ev = parallel_max(p.traces)
        assert level == Level.GREEN
        assert conf < 0.5
        assert any("completed" in e for e in ev)

    def test_completed_ge_3(self):
        p = ProfileData(name="x", traces={"parallel_projects": 5, "projects_completed": 3})
        level, conf, _ = parallel_max(p.traces)
        assert level == Level.GOLD

    def test_n_is_none(self):
        level, conf, ev = parallel_max({})
        assert level is None
        assert conf == 0.0


# --- detect_red_flags edge cases ---------------------------------------


class TestDetectRedFlags:
    def test_retries_high_declared_blue(self):
        p = ProfileData(
            name="x",
            declared_level=Level.BLUE,
            traces={"retries_after_fact": 0.7},
        )
        flags = detect_red_flags(p)
        assert any("reprise" in f.titre.lower() for f in flags)

    def test_no_context_declared_blue(self):
        p = ProfileData(
            name="x",
            declared_level=Level.BLUE,
            traces={},
        )
        flags = detect_red_flags(p)
        assert any("contexte" in f.titre.lower() for f in flags)

    def test_no_flags_when_no_declared(self):
        p = ProfileData(name="x", traces={})
        assert detect_red_flags(p) == []

    def test_no_flags_when_low_level(self):
        p = ProfileData(
            name="x",
            declared_level=Level.RED,
            traces={"retries_after_fact": 0.8},
        )
        flags = detect_red_flags(p)
        assert not any("reprise" in f.titre.lower() for f in flags)

    def test_retries_low_no_flag(self):
        p = ProfileData(
            name="x",
            declared_level=Level.GOLD,
            traces={"retries_after_fact": 0.01},
        )
        flags = detect_red_flags(p)
        assert not any("reprise" in f.titre.lower() for f in flags)

    def test_context_present_no_blue_flag(self):
        p = ProfileData(
            name="x",
            declared_level=Level.BLUE,
            traces={"context_versioned": True},
        )
        flags = detect_red_flags(p)
        assert not any("contexte" in f.titre.lower() for f in flags)


# --- _questions_for edge cases -----------------------------------------


class TestQuestionsFor:
    def test_all_data_provided(self):
        p = ProfileData(
            name="x",
            declared_level=Level.GREEN,
            traces={
                "pr_sizes": ["S", "M"],
                "retries_after_fact": 0.1,
                "retries_triangulated": True,
                "context_versioned": True,
                "parallel_projects": 2,
                "projects_completed": 2,
            },
        )
        qs = _questions_for(p)
        assert len(qs) == 1
        assert "complètes" in qs[0] or "dimension" in qs[0]

    def test_parallel_ge3_no_completed(self):
        p = ProfileData(
            name="x",
            declared_level=Level.GREEN,
            traces={
                "pr_sizes": ["S"],
                "retries_after_fact": 0.1,
                "retries_triangulated": True,
                "context_versioned": True,
                "parallel_projects": 5,
            },
        )
        qs = _questions_for(p)
        assert any("bout" in q for q in qs)

    def test_retries_without_triangulation(self):
        p = ProfileData(
            name="x",
            declared_level=Level.GREEN,
            traces={
                "pr_sizes": ["S"],
                "retries_after_fact": 0.1,
                "retries_triangulated": False,
                "context_versioned": True,
                "parallel_projects": 1,
            },
        )
        qs = _questions_for(p)
        assert any("corroborer" in q for q in qs)

    def test_no_adoption_signals(self):
        p = ProfileData(
            name="x",
            declared_level=Level.GREEN,
            traces={
                "pr_sizes": ["S"],
                "retries_after_fact": 0.1,
                "retries_triangulated": True,
                "parallel_projects": 1,
            },
        )
        qs = _questions_for(p)
        assert any("mémoire" in q or "règles" in q for q in qs)


# --- evaluate edge cases ----------------------------------------------


class TestEvaluateEdgeCases:
    def test_variance_signal(self):
        p = ProfileData(
            name="x",
            traces={
                "pr_sizes": ["S", "S", "S", "XL"],
                "retries_after_fact": 0.01,
                "retries_triangulated": True,
                "context_versioned": True,
                "parallel_projects": 1,
            },
        )
        v = evaluate(p)
        size_axis = next(a for a in v.axis_scores if a.axe == "size")
        assert size_axis.variance is not None

    def test_undecided_axis_refuses(self):
        p = ProfileData(
            name="x",
            traces={
                "retries_after_fact": 0.01,
                "retries_triangulated": True,
                "context_versioned": True,
                "parallel_projects": 1,
            },
        )
        v = evaluate(p)
        assert v.level is None
        assert v.limiting_axis == "size"

    def test_low_confidence_refuses(self):
        p = ProfileData(
            name="x",
            traces={
                "pr_sizes": ["S", "M"],
                "retries_after_fact": 0.01,
                "retries_triangulated": True,
                "context_versioned": True,
                "parallel_projects": 1,
            },
        )
        v = evaluate(p)
        assert v.level is None

    def test_silver_without_agents_autonomous(self):
        p = ProfileData(
            name="x",
            traces={
                "pr_sizes": ["L", "L", "L"],
                "retries_after_fact": 0.01,
                "retries_triangulated": True,
                "context_versioned": True,
                "agent_rules_versioned": True,
                "retry_loops": True,
                "parallel_projects": 3,
                "projects_completed": 3,
                "agents_autonomous": False,
            },
        )
        v = evaluate(p)
        assert v.next_steps
        assert any("Silver" in s or "agents" in s.lower() for s in v.next_steps)

    def test_data_errors_returns_early(self):
        p = ProfileData(name="x", traces={"pr_sizes": "S"})
        v = evaluate(p)
        assert v.level is None
        assert len(v.data_errors) > 0
        assert v.axis_scores == []

    def test_gold_level_fully_decided(self):
        p = ProfileData(
            name="x",
            traces={
                "pr_sizes": ["L", "XL", "L", "XL", "L"],
                "retries_after_fact": 0.01,
                "retries_triangulated": True,
                "context_versioned": True,
                "agent_rules_versioned": True,
                "retry_loops": True,
                "parallel_projects": 3,
                "projects_completed": 3,
                "agents_autonomous": True,
            },
        )
        v = evaluate(p)
        assert v.level == Level.GOLD
        assert v.decided
