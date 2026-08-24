# Copyright 2026 Romy Alula — MIT License
"""Validation de profil via JSON Schema.

Fail fast : un profil invalide → erreur claire, pas de crash silencieux.
Le schema est aligné sur la grille officielle (4 axes, 7 niveaux).
"""

from __future__ import annotations

import json
from pathlib import Path

_SCHEMA_PATH = Path(__file__).parent / 'schemas' / 'profile.schema.json'
_schema: dict | None = None


def _load_schema() -> dict:
    """Charge le schema JSON (lazy, une seule fois)."""
    global _schema
    if _schema is None:
        try:
            _schema = json.loads(_SCHEMA_PATH.read_text(encoding='utf-8'))
        except FileNotFoundError:
            raise RuntimeError(
                f'Schema introuvable : {_SCHEMA_PATH}\n'
                "Installez le package en mode dev : pip install -e '.[dev]'"
            )
    return _schema


def validate_profile(data: dict) -> list[str]:
    """Valide un dict profil contre le JSON Schema.

    Retourne la liste des erreurs (vide = valide).
    Erreurs formatées en FR pour l'utilisateur final.
    """
    try:
        import jsonschema
    except ImportError:
        # Fallback : validation minimale sans jsonschema
        return _validate_minimal(data)

    schema = _load_schema()
    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))

    messages: list[str] = []
    for error in errors:
        path = '.'.join(str(p) for p in error.absolute_path) or 'profil'
        messages.append(f'{path}: {error.message}')
    return messages


def _validate_minimal(data: dict) -> list[str]:
    """Validation minimale sans dépendance jsonschema."""
    errors: list[str] = []

    if not isinstance(data, dict):
        return ['Le profil doit être un objet JSON.']

    if 'name' not in data or not isinstance(data['name'], str) or not data['name'].strip():
        errors.append('name : requis, chaîne non vide.')

    declared = data.get('declared_level')
    if declared is not None:
        valid_levels = {'WHITE', 'RED', 'BLUE', 'GREEN', 'COPPER', 'SILVER', 'GOLD'}
        if declared not in valid_levels:
            errors.append(f"declared_level '{declared}' inconnu : valeurs = {sorted(valid_levels)}")

    traces = data.get('traces')
    if traces is not None:
        if not isinstance(traces, dict):
            errors.append('traces : doit être un objet.')
        else:
            valid_sizes = {'S', 'M', 'L', 'XL'}
            pr_sizes = traces.get('pr_sizes')
            if pr_sizes is not None:
                if not isinstance(pr_sizes, list):
                    errors.append('traces.pr_sizes : doit être une liste.')
                else:
                    for s in pr_sizes:
                        if s not in valid_sizes:
                            errors.append(
                                f"traces.pr_sizes contient '{s}' : valeurs = {sorted(valid_sizes)}"
                            )

            retries = traces.get('retries_after_fact')
            if retries is not None:
                if not isinstance(retries, (int, float)):
                    errors.append('traces.retries_after_fact : doit être un nombre (0-1).')
                elif not 0.0 <= retries <= 1.0:
                    errors.append('traces.retries_after_fact : doit être entre 0 et 1.')

            for key in ('parallel_projects', 'projects_completed'):
                val = traces.get(key)
                if val is not None and (not isinstance(val, int) or val < 0):
                    errors.append(f'traces.{key} : entier >= 0 requis.')

            for key in (
                'context_versioned',
                'agent_rules_versioned',
                'retry_loops',
                'retries_triangulated',
                'agents_autonomous',
                'prompts',
            ):
                val = traces.get(key)
                if val is not None and not isinstance(val, bool):
                    errors.append(f'traces.{key} : booléen requis.')

    return errors
