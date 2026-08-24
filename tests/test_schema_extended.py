# Copyright 2026 Romy Alula — MIT License
"""Tests schema.py : validate_profile, _validate_minimal.

Cible : 85% branch sur schema.py.
"""

from __future__ import annotations

import pytest

from laivelup.schema import _validate_minimal, validate_profile


# --- validate_profile (jsonschema) -------------------------------------


class TestValidateProfile:
    def test_valid_profile(self):
        data = {'name': 'test', 'traces': {'pr_sizes': ['S', 'M']}}
        assert validate_profile(data) == []

    def test_invalid_declared_level(self):
        data = {'name': 'test', 'declared_level': 'PLATINUM'}
        errors = validate_profile(data)
        assert len(errors) > 0

    def test_invalid_pr_sizes(self):
        data = {'name': 'test', 'traces': {'pr_sizes': ['XXL']}}
        errors = validate_profile(data)
        assert len(errors) > 0

    def test_retries_out_of_range(self):
        data = {'name': 'test', 'traces': {'retries_after_fact': 1.5}}
        errors = validate_profile(data)
        assert len(errors) > 0

    def test_parallel_negative(self):
        data = {'name': 'test', 'traces': {'parallel_projects': -1}}
        errors = validate_profile(data)
        assert len(errors) > 0

    def test_missing_name(self):
        data = {'traces': {'pr_sizes': ['S']}}
        errors = validate_profile(data)
        assert len(errors) > 0


# --- _validate_minimal (fallback) --------------------------------------


class TestValidateMinimal:
    def test_not_dict(self):
        errors = _validate_minimal([1, 2, 3])  # type: ignore[arg-type]
        assert any('objet JSON' in e for e in errors)

    def test_missing_name(self):
        errors = _validate_minimal({'traces': {}})
        assert any('name' in e for e in errors)

    def test_empty_name(self):
        errors = _validate_minimal({'name': '  '})
        assert any('name' in e for e in errors)

    def test_invalid_declared_level(self):
        errors = _validate_minimal({'name': 'x', 'declared_level': 'PLATINUM'})
        assert any('PLATINUM' in e for e in errors)

    def test_valid_declared_level(self):
        errors = _validate_minimal({'name': 'x', 'declared_level': 'BLUE'})
        assert errors == []

    def test_traces_not_dict(self):
        errors = _validate_minimal({'name': 'x', 'traces': 'bad'})
        assert any('objet' in e for e in errors)

    def test_pr_sizes_not_list(self):
        errors = _validate_minimal({'name': 'x', 'traces': {'pr_sizes': 'S'}})
        assert any('liste' in e for e in errors)

    def test_pr_sizes_invalid_value(self):
        errors = _validate_minimal({'name': 'x', 'traces': {'pr_sizes': ['XXL']}})
        assert any('XXL' in e for e in errors)

    def test_retries_not_number(self):
        errors = _validate_minimal({'name': 'x', 'traces': {'retries_after_fact': 'abc'}})
        assert any('nombre' in e for e in errors)

    def test_retries_out_of_range(self):
        errors = _validate_minimal({'name': 'x', 'traces': {'retries_after_fact': 2.0}})
        assert any('entre 0 et 1' in e for e in errors)

    def test_parallel_not_int(self):
        errors = _validate_minimal({'name': 'x', 'traces': {'parallel_projects': 'bad'}})
        assert any('entier' in e for e in errors)

    def test_parallel_negative(self):
        errors = _validate_minimal({'name': 'x', 'traces': {'parallel_projects': -1}})
        assert any('entier' in e for e in errors)

    def test_context_not_bool(self):
        errors = _validate_minimal({'name': 'x', 'traces': {'context_versioned': 'yes'}})
        assert any('booléen' in e for e in errors)

    def test_agents_autonomous_not_bool(self):
        errors = _validate_minimal({'name': 'x', 'traces': {'agents_autonomous': 1}})
        assert any('booléen' in e for e in errors)

    def test_valid_complete_profile(self):
        data = {
            'name': 'valid',
            'declared_level': 'GREEN',
            'traces': {
                'pr_sizes': ['S', 'M'],
                'retries_after_fact': 0.3,
                'parallel_projects': 3,
                'projects_completed': 2,
                'context_versioned': True,
                'agents_autonomous': False,
            },
        }
        assert _validate_minimal(data) == []
