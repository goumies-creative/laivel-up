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


# --- _load_schema / fallback ImportError (coverage-90-closing-gaps) ----


class TestLoadSchemaMissing:
    def test_schema_not_found_raises_runtime_error(self, monkeypatch, tmp_path):
        from laivelup import schema as schema_mod

        monkeypatch.setattr(schema_mod, '_SCHEMA_PATH', tmp_path / 'nope.json')
        monkeypatch.setattr(schema_mod, '_schema', None)
        with pytest.raises(RuntimeError, match='Schema introuvable'):
            schema_mod._load_schema()


class TestValidateProfileImportFallback:
    def test_jsonschema_import_error_falls_back_to_minimal(self, monkeypatch):
        import sys

        from laivelup import schema as schema_mod

        monkeypatch.setitem(sys.modules, 'jsonschema', None)
        errors = schema_mod.validate_profile({'traces': {}})
        assert any('name' in e for e in errors)


# --- Mapping jsonschema -> FR (coverage-90-closing-gaps / copy-francaise) --


class TestJsonschemaErrorTranslation:
    def test_missing_required_property_is_translated(self):
        errors = validate_profile({'traces': {'pr_sizes': ['S']}})
        assert any('propriété requise manquante' in e for e in errors)
        assert not any('required property' in e for e in errors)

    def test_wrong_type_is_translated(self):
        errors = validate_profile({'name': 123})
        assert any('doit être une chaîne' in e for e in errors)

    def test_enum_violation_is_translated(self):
        errors = validate_profile({'name': 'x', 'traces': {'pr_sizes': ['XXL']}})
        assert any('valeur invalide' in e for e in errors)

    def test_maximum_violation_is_translated(self):
        errors = validate_profile({'name': 'x', 'traces': {'retries_after_fact': 1.5}})
        assert any('doit être <=' in e for e in errors)

    def test_additional_properties_is_translated(self):
        errors = validate_profile({'name': 'x', 'traces': {'inconnu_xyz': True}})
        assert any('supplémentaire non autorisée' in e for e in errors)

    def test_path_separator_uses_space_colon_space(self):
        """Convention typographique AGENTS.md : ' : ' pas ':'."""
        errors = validate_profile({'traces': {}})
        assert any(' : ' in e for e in errors)
