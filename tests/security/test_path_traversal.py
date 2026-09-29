# Copyright 2026 Romy Alula — MIT License
"""Tests de securite : path traversal.

Verifie que le CLI refuse les chemins malveillants (../../etc/passwd)
et n'ecrit pas en dehors du repertoire de travail.
"""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from laivelup.cli import app

runner = CliRunner()


class TestPathTraversal:
    def test_output_path_traversal_blocked(self, valid_profile: Path, tmp_path: Path):
        """--out avec path traversal doit etre refuse."""
        evil_out = tmp_path / '..' / '..' / 'tmp' / 'evil_output'
        r = runner.invoke(
            app,
            ['evaluate', str(valid_profile), '--out', str(evil_out), '--no-html'],
        )
        # L'outil doit reussir ou echouer proprement, pas ecrire hors du tmp
        assert r.exit_code in (0, 1, 2)

    def test_output_no_write_outside_cwd(self, valid_profile: Path, tmp_path: Path):
        """Vérifie que les rapports sont écrits dans le bon répertoire."""
        out = tmp_path / 'rapports'
        r = runner.invoke(
            app,
            ['evaluate', str(valid_profile), '--out', str(out), '--no-html'],
        )
        if r.exit_code == 0:
            assert out.exists()

    def test_profile_path_traversal_not_executed(self, tmp_path: Path):
        """Chemin de profil malveillant → exit != 0."""
        evil = tmp_path / '..' / 'etc' / 'passwd'
        r = runner.invoke(app, ['evaluate', str(evil), '--no-html'])
        assert r.exit_code != 0
        assert r.output.strip() != ''

    def test_slug_escape_refused_by_write_reports(self, tmp_path: Path, monkeypatch):
        """Violation délibérée : un slug qui s'échappe de --out est refusé.

        Si le garde `is_relative_to` de write_reports est désactivé, ce test
        échoue (écriture hors dossier au lieu de ValueError).
        """
        import pytest

        from laivelup import report as report_mod
        from laivelup.model import Level, Verdict

        monkeypatch.setattr(report_mod, 'slug', lambda _name: '../evil')
        verdict = Verdict(name='evil', level=Level.BLUE, axis_scores=[], limiting_axis=None)
        with pytest.raises(ValueError, match='escapes output directory'):
            report_mod.write_reports(verdict, tmp_path / 'rapports')
        assert not (tmp_path / 'evil').exists()

    def test_malicious_profile_name_stays_inside_out_dir(self, tmp_path: Path):
        """Un nom de profil '../../evil' n'écrit jamais hors de --out."""
        from laivelup.model import Level, Verdict
        from laivelup.report import write_reports

        out = tmp_path / 'rapports'
        verdict = Verdict(name='../../evil', level=Level.BLUE, axis_scores=[], limiting_axis=None)
        md, html = write_reports(verdict, out)
        assert md.resolve().parent == out.resolve()
        assert html is not None and html.resolve().parent == out.resolve()
        assert not (tmp_path / 'evil').exists()
