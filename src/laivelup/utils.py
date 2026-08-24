# Copyright 2026 Romy Alula — MIT License
"""Fonctions utilitaires partagées (slug RGPD, etc.)."""
from __future__ import annotations

import hashlib
import hmac
import os


def generate_team_salt() -> str:
    """Génère un sel aléatoire pour une équipe (16 bytes hex = 32 chars)."""
    return os.urandom(16).hex()


def slug(name: str, salt: str | None = None) -> str:
    """Pseudo-anonyme RGPD pour le partage de rapports.

    Si un sel est fourni, utilise HMAC-SHA256 (résistant dictionnaire).
    Sinon, SHA-256 simple (rétro-compatibilité, déprécié).
    """
    if salt is not None:
        digest = hmac.new(
            salt.encode("utf-8"),
            name.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()[:8]
    else:
        digest = hashlib.sha256(name.encode("utf-8")).hexdigest()[:8]
    cleaned = "".join(c if c.isalnum() else "-" for c in name.lower()).strip("-") or "membre"
    return f"{cleaned[:32]}-{digest}"
