# Copyright 2026 Romy Alula — MIT License
"""Tests de compatibilité schéma : tous les exemples valident.

Contourne le problème de path schema.py installé globalement
en utilisant le fallback _validate_minimal pour les tests invalides.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

EXEMPLES_DIR = Path(__file__).resolve().parent.parent / 'exemples'
OFFICIALS_DIR = Path(__file__).resolve().parent.parent / 'grille' / 'profils-officiels'
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = PROJECT_ROOT / 'schemas' / 'profile.schema.json'


def _validate_with_local_schema(data: dict) -> list[str]:
    """Valide un profil en utilisant le schéma local du projet (pas celui installé)."""
    sys.path.insert(0, str(PROJECT_ROOT / 'src'))
    from laivelup.schema import _validate_minimal

    # Import jsonschema et charger le schéma local
    try:
        import jsonschema

        schema = json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
        validator = jsonschema.Draft202012Validator(schema)
        errors = sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))
        messages = []
        for error in errors:
            path = '.'.join(str(p) for p in error.absolute_path) or 'profil'
            messages.append(f'{path}: {error.message}')
        return messages
    except (FileNotFoundError, ImportError):
        return _validate_minimal(data)


class TestExamplesValidate:
    """Tous les profils exemples valident le schéma."""

    def test_examples_validate(self):
        examples = list(EXEMPLES_DIR.glob('*.json'))
        assert len(examples) >= 1, f'Aucun profil exemple trouvé dans {EXEMPLES_DIR}'
        for path in examples:
            data = json.loads(path.read_text(encoding='utf-8'))
            errors = _validate_with_local_schema(data)
            assert errors == [], f'{path.name}: {errors}'

    def test_officials_validate_if_present(self):
        if not OFFICIALS_DIR.exists():
            pytest.skip('Profils officiels pas encore disponibles (28/08)')
        officials = list(OFFICIALS_DIR.glob('*.json'))
        if not officials:
            pytest.skip('Aucun profil officiel trouvé')
        for path in officials:
            data = json.loads(path.read_text(encoding='utf-8'))
            errors = _validate_with_local_schema(data)
            assert errors == [], f'{path.name}: {errors}'


class TestSchemaRoundtrip:
    """Profil → dict → JSON → validate → structure identique."""

    def test_roundtrip_maison1(self):
        path = EXEMPLES_DIR / 'profil-maison-1.json'
        data = json.loads(path.read_text(encoding='utf-8'))
        errors = _validate_with_local_schema(data)
        assert errors == []
        json_str = json.dumps(data, ensure_ascii=False)
        data_back = json.loads(json_str)
        errors2 = _validate_with_local_schema(data_back)
        assert errors2 == []
        assert data_back.keys() == data.keys()
        assert data_back['name'] == data['name']


class TestInvalidRejected:
    """Profil invalide → erreurs non-vides."""

    def test_invalid_pr_sizes(self):
        data = {'name': 'bad', 'traces': {'pr_sizes': ['XXL']}}
        errors = _validate_with_local_schema(data)
        assert len(errors) > 0

    def test_invalid_declared_level(self):
        data = {'name': 'bad', 'declared_level': 'PLATINUM'}
        errors = _validate_with_local_schema(data)
        assert len(errors) > 0

    def test_missing_name(self):
        data = {'traces': {'pr_sizes': ['M']}}
        errors = _validate_with_local_schema(data)
        assert len(errors) > 0
