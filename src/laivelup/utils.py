# Copyright 2026 Romy Alula — MIT License
"""Fonctions utilitaires partagées (slug RGPD, etc.)."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .model import ProfileData


def generate_team_salt() -> str:
    """Génère un sel aléatoire pour une équipe (16 bytes hex = 32 chars)."""
    return os.urandom(16).hex()


MAX_PROFILE_MB = 2


def load_profile_data(path: Path) -> ProfileData:
    """Charge un profil JSON minimal (sans validation schema).

    Garde de taille + type check inclus. Pour la CLI utilisateur avec
    validation complète, préférer cli.py:_load_profile().
    """
    from .model import Level, ProfileData

    size = path.stat().st_size
    if size > MAX_PROFILE_MB * 1024 * 1024:
        raise ValueError(f'Profil trop volumineux (> {MAX_PROFILE_MB} Mo) : {path}')
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise ValueError(f'Le profil doit être un objet JSON (obtenu : {type(data).__name__})')
    declared = data.get('declared_level')
    declared = Level[declared.upper()] if isinstance(declared, str) and declared else None
    return ProfileData(
        name=data.get('name', path.stem),
        declared_level=declared,
        traces=data.get('traces', {}),
        answers=data.get('answers', {}),
        meta=data.get('meta', {}),
    )


def slug(name: str, salt: str | None = None) -> str:
    """Pseudo-anonyme RGPD pour le partage de rapports.

    Si un sel est fourni, utilise HMAC-SHA256 (résistant dictionnaire).
    Sinon, SHA-256 simple (rétro-compatibilité, déprécié).
    """
    if salt is not None:
        digest = hmac.new(
            salt.encode('utf-8'),
            name.encode('utf-8'),
            hashlib.sha256,
        ).hexdigest()[:8]
    else:
        digest = hashlib.sha256(name.encode('utf-8')).hexdigest()[:8]
    cleaned = ''.join(c if c.isalnum() else '-' for c in name.lower()).strip('-') or 'membre'
    return f'{cleaned[:32]}-{digest}'
