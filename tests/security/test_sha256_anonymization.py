# Copyright 2026 Romy Alula — MIT License
"""Tests de securite : anonymisation SHA-256.

Verifie que le Team Tracker utilise bien HMAC-SHA-256 (pas SHA-1/MD5)
pour le pseudo-anonymisation des membres d'equipe.
"""

from __future__ import annotations

import hashlib
import inspect

from laivelup.utils import generate_team_salt, slug


class TestSha256Anonymization:
    def test_slug_uses_hmac_sha256(self):
        """slug utilise hmac.new + hashlib.sha256, pas sha1 ni md5."""
        source = inspect.getsource(slug)
        assert 'hmac' in source.lower(), 'hmac doit etre utilise'
        assert 'sha256' in source.lower(), 'sha256 doit etre utilise'
        assert 'md5' not in source.lower(), 'md5 ne doit pas etre utilise'
        assert 'sha1' not in source.lower(), 'sha1 ne doit pas etre utilise'

    def test_slug_is_deterministic(self):
        """Meme entree + meme sel → meme slug."""
        salt = generate_team_salt()
        slug1 = slug('alice', salt)
        slug2 = slug('alice', salt)
        assert slug1 == slug2

    def test_slug_different_for_different_names(self):
        """Noms differents → slugs differents."""
        salt = generate_team_salt()
        slug1 = slug('alice', salt)
        slug2 = slug('bob', salt)
        assert slug1 != slug2

    def test_slug_different_with_different_salts(self):
        """Meme nom, sels differents → slugs differents (preuve de sel)."""
        slug1 = slug('alice', generate_team_salt())
        slug2 = slug('alice', generate_team_salt())
        assert slug1 != slug2

    def test_slug_contains_hex_digest(self):
        """Le slug contient un digest hexadecimale HMAC-SHA-256."""
        salt = generate_team_salt()
        s = slug('test', salt)
        digest = s.split('-')[-1]
        assert len(digest) == 8
        assert all(c in '0123456789abcdef' for c in digest)

    def test_slug_format_is_name_hash(self):
        """Format du slug : {name_clean}-{hash8}."""
        salt = generate_team_salt()
        s = slug('alice', salt)
        parts = s.rsplit('-', 1)
        assert len(parts) == 2
        assert parts[0] == 'alice'
        assert len(parts[1]) == 8
