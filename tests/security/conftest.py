# Copyright 2026 Romy Alula — MIT License
"""Fixtures partagees pour les tests de securite."""

from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture
def giant_profile(tmp_path: Path) -> Path:
    """Profil JSON de 3 Mo (> MAX_JSON_MB=2) pour tester le depassement de taille."""
    data = {
        'name': 'giant',
        'traces': {
            'pr_sizes': ['M'] * 100000,
            'context_versioned': True,
            'retries_after_fact': 0.3,
            'parallel_projects': 2,
        },
    }
    # Gonfler jusqu'a ~3 Mo
    blob = json.dumps(data)
    while len(blob.encode('utf-8')) < 3 * 1024 * 1024:
        data['traces']['pr_sizes'].extend(['M'] * 10000)
        blob = json.dumps(data)
    path = tmp_path / 'giant.json'
    path.write_text(blob, encoding='utf-8')
    return path


@pytest.fixture
def malicious_json(tmp_path: Path) -> Path:
    """JSON avec injection de cles inattendues et types errones."""
    data = {
        'name': 'injection',
        '__proto__': {'admin': True},
        'constructor': {'prototype': {'isAdmin': True}},
        'traces': {
            'pr_sizes': ['M'],
            'retries_after_fact': 'NOT_A_NUMBER',
            'parallel_projects': -1,
            'evil_key': 'x' * 10000,
        },
        'answers': {'last_answer': '<script>alert(1)</script>'},
    }
    path = tmp_path / 'injection.json'
    path.write_text(json.dumps(data), encoding='utf-8')
    return path


@pytest.fixture
def valid_profile(tmp_path: Path) -> Path:
    """Profil minimal valide pour comparaison."""
    data = {
        'name': 'valid',
        'traces': {
            'pr_sizes': ['M', 'M'],
            'context_versioned': True,
            'retries_after_fact': 0.4,
            'retries_triangulated': True,
            'parallel_projects': 1,
        },
    }
    path = tmp_path / 'valid.json'
    path.write_text(json.dumps(data), encoding='utf-8')
    return path
