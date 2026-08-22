# Copyright 2026 Romy Alula — MIT License
"""Tests de securite : anonymisation SHA-256.

Verifie que le Team Tracker utilise bien SHA-256 (pas SHA-1/MD5)
pour le pseudo-anonymisation des membres d'equipe.
"""

from __future__ import annotations

import hashlib
import inspect

from laivelup.team import _slug


class TestSha256Anonymization:
    def test_slug_uses_sha256(self):
        """_slug utilise hashlib.sha256, pas sha1 ni md5."""
        source = inspect.getsource(_slug)
        assert "sha256" in source.lower(), "sha256 doit etre utilise"
        assert "md5" not in source.lower(), "md5 ne doit pas etre utilise"
        assert "sha1" not in source.lower(), "sha1 ne doit pas etre utilise"

    def test_slug_is_deterministic(self):
        """Meme entree → meme slug."""
        slug1 = _slug("alice")
        slug2 = _slug("alice")
        assert slug1 == slug2

    def test_slug_different_for_different_names(self):
        """Noms differents → slugs differents."""
        slug1 = _slug("alice")
        slug2 = _slug("bob")
        assert slug1 != slug2

    def test_slug_contains_hex_digest(self):
        """Le slug contient un digest hexadecimale SHA-256."""
        slug = _slug("test")
        digest = slug.split("-")[-1]
        assert len(digest) == 8
        assert all(c in "0123456789abcdef" for c in digest)

    def test_slug_format_is_name_hash(self):
        """Format du slug : {name_clean}-{hash8}."""
        slug = _slug("alice")
        parts = slug.rsplit("-", 1)
        assert len(parts) == 2
        assert parts[0] == "alice"
        assert len(parts[1]) == 8
