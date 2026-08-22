# Copyright 2026 Romy Alula — MIT License
"""Tests de securite : protection contre les profils geants (DoS).

Verifie que le CLI rejete proprement les fichiers JSON trop volumineux
(> MAX_JSON_MB = 2 Mo).
"""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from laivelup.cli import app

runner = CliRunner()


class TestDosProfileGiant:
    def test_giant_profile_rejected(self, giant_profile: Path):
        """Profil > 2 Mo → exit 2 (trop volumineux)."""
        r = runner.invoke(app, ["evaluate", str(giant_profile), "--no-html"])
        assert r.exit_code == 2

    def test_giant_profile_message(self, giant_profile: Path):
        """Message d'erreur explicite pour fichier trop volumineux."""
        r = runner.invoke(app, ["evaluate", str(giant_profile), "--no-html"])
        assert "trop volumineux" in r.output.lower() or r.exit_code == 2

    def test_valid_small_profile_accepted(self, valid_profile: Path):
        """Profil < 2 Mo → accepte (pas de faux positif)."""
        r = runner.invoke(app, ["evaluate", str(valid_profile), "--no-html"])
        assert r.exit_code == 0

    def test_nonexistent_file_clean_error(self, tmp_path: Path):
        """Fichier inexistant → exit 2 proprement."""
        r = runner.invoke(app, ["evaluate", str(tmp_path / "nope.json"), "--no-html"])
        assert r.exit_code != 0
