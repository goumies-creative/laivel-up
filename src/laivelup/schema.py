# Copyright 2026 Romy Alula — MIT License
"""Validation de profil via JSON Schema.

Fail fast : un profil invalide → erreur claire, pas de crash silencieux.
Le schema est aligné sur la grille officielle (4 axes, 7 niveaux).
"""

from __future__ import annotations

import json
import re
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


_TYPE_LABELS_FR: dict[str, str] = {
    'string': 'une chaîne',
    'integer': 'un entier',
    'number': 'un nombre',
    'boolean': 'un booléen',
    'array': 'une liste',
    'object': 'un objet',
    'null': 'nul',
}


def _translate_jsonschema_error(error: object) -> str:
    """Traduit les erreurs jsonschema courantes vers le style FR de
    `_validate_minimal` (type/enum/required/minLength/minimum/maximum/
    additionalProperties). Message brut jsonschema (EN) en repli si le
    validateur n'est pas mappé : un message anglais exploitable vaut mieux
    qu'un texte tronqué ou une erreur de traduction.
    """
    validator = error.validator  # type: ignore[attr-defined]

    if validator == 'type':
        expected = error.validator_value  # type: ignore[attr-defined]
        if isinstance(expected, list):
            labels = ' ou '.join(_TYPE_LABELS_FR.get(str(t), str(t)) for t in expected)
        else:
            labels = _TYPE_LABELS_FR.get(expected, str(expected))
        return f'doit être {labels}'

    if validator == 'enum':
        return f'valeur invalide : attendu parmi {error.validator_value}'  # type: ignore[attr-defined]

    if validator == 'required':
        match = re.search(r"'(\w+)' is a required property", error.message)  # type: ignore[attr-defined]
        prop = match.group(1) if match else '?'
        return f'{prop} : propriété requise manquante'

    if validator == 'minLength':
        return 'trop court'

    if validator == 'maxLength':
        return 'trop long'

    if validator == 'minimum':
        return f'doit être >= {error.validator_value}'  # type: ignore[attr-defined]

    if validator == 'maximum':
        return f'doit être <= {error.validator_value}'  # type: ignore[attr-defined]

    if validator == 'additionalProperties':
        return 'propriété supplémentaire non autorisée'

    return str(error.message)  # type: ignore[attr-defined]  # fallback brut (EN), non mappé


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
        messages.append(f'{path} : {_translate_jsonschema_error(error)}')
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
