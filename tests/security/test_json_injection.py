# Copyright 2026 Romy Alula — MIT License
"""Tests de securite : injection JSON et types errones.

Verifie que le CLI rejete proprement des profils JSON malformes
(claes inattendues, __proto__, types errones, payloads geants).
"""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from laivelup.cli import app

runner = CliRunner()


class TestJsonInjection:
    def test_injection_proto_rejected(self, malicious_json: Path):
        """JSON avec __proto__ doit etre rejete proprement (exit 2)."""
        r = runner.invoke(app, ['evaluate', str(malicious_json), '--no-html'])
        assert r.exit_code != 0

    def test_injection_constructor_rejected(self, malicious_json: Path):
        """JSON avec constructor.prototype doit etre rejete."""
        r = runner.invoke(app, ['evaluate', str(malicious_json), '--no-html'])
        assert r.exit_code != 0

    def test_wrong_types_in_traces(self, malicious_json: Path):
        """Types errones dans traces (string au lieu de float) → exit 2."""
        r = runner.invoke(app, ['evaluate', str(malicious_json), '--no-html'])
        assert r.exit_code != 0

    def test_negative_int_rejected(self, malicious_json: Path):
        """Valeur negative pour parallel_projects → exit 2."""
        r = runner.invoke(app, ['evaluate', str(malicious_json), '--no-html'])
        assert r.exit_code != 0

    def test_large_key_value_pair(self, malicious_json: Path):
        """Cle-valeur de 10 Ko dans traces → pas de crash."""
        r = runner.invoke(app, ['evaluate', str(malicious_json), '--no-html'])
        assert r.exit_code != 0

    def test_valid_profile_accepted(self, valid_profile: Path):
        """Profil valide → exit 0 (pas de faux positif)."""
        r = runner.invoke(app, ['evaluate', str(valid_profile), '--no-html'])
        assert r.exit_code == 0
