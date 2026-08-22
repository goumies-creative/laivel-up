# Copyright 2026 Romy Alula — MIT License
"""Tests snapshot pour la sortie CLI.

Vérifie que le format de sortie du CLI reste stable et cohérent.
Les snapshots capturent la sortie Rich (tables, messages) et les rapports.
Les chemins temporaires sont normalisés avant comparaison.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from typer.testing import CliRunner

from laivelup.cli import app

REPO = Path(__file__).parent.parent
runner = CliRunner()


def _normalize(output: str) -> str:
    """Normalise les chemins temporaires et codes ANSI pour des snapshots stables."""
    # Strip ANSI escape codes (Rich force_terminal=True les ajoute)
    output = re.sub(r"\x1b\[[0-9;]*m", "", output)
    output = re.sub(r"C:\\Users\\[^\\]+\\AppData\\Local\\Temp\\[^\n]+", "<TMP>", output)
    output = re.sub(r"/tmp/[^/\n]+", "<TMP>", output)
    output = re.sub(r"pytest-\d+", "pytest-N", output)
    return output


@pytest.mark.snapshot
class TestEvaluateSnapshot:
    """Snapshots de la commande evaluate."""

    def test_evaluate_profil_maison_1(self, snapshot):
        """Sortie de evaluate sur profil-maison-1."""
        r = runner.invoke(
            app,
            ["evaluate", str(REPO / "exemples" / "profil-maison-1.json"), "--no-html"],
        )
        assert r.exit_code == 0
        snapshot.assert_match(_normalize(r.output), "evaluate_profil_maison_1.txt")

    def test_evaluate_profil_maison_2(self, snapshot):
        """Sortie de evaluate sur profil-maison-2."""
        r = runner.invoke(
            app,
            ["evaluate", str(REPO / "exemples" / "profil-maison-2.json"), "--no-html"],
        )
        assert r.exit_code == 0
        snapshot.assert_match(_normalize(r.output), "evaluate_profil_maison_2.txt")

    def test_evaluate_fichier_introuvable(self, snapshot):
        """Message d'erreur quand le fichier n'existe pas."""
        r = runner.invoke(
            app,
            ["evaluate", "exemples/inexistant.json", "--no-html"],
        )
        assert r.exit_code != 0
        snapshot.assert_match(_normalize(r.output), "evaluate_fichier_introuvable.txt")

    def test_evaluate_json_invalide(self, snapshot, tmp_path):
        """Message d'erreur pour JSON invalide."""
        bad = tmp_path / "bad.json"
        bad.write_text("{invalid json}", encoding="utf-8")
        r = runner.invoke(
            app,
            ["evaluate", str(bad), "--no-html"],
        )
        assert r.exit_code == 2
        snapshot.assert_match(_normalize(r.output), "evaluate_json_invalide.txt")


@pytest.mark.snapshot
class TestInterrogateSnapshot:
    """Snapshots de la commande interrogate (mode interactif mocké)."""

    def test_interrogate_verdict_atteint(self, snapshot, monkeypatch, tmp_path):
        """Sortie quand un verdict est atteint."""
        from laivelup import cli

        answers = iter([
            "souvent des M",
            "mon niveau est bleu",
            "40%",
            "oui voici 3 PR typiques",
            "oui j'ai un contexte",
            "1 chantier",
        ])
        monkeypatch.setattr(cli.Prompt, "ask", lambda prompt, **kw: next(answers))
        r = runner.invoke(
            cli.app,
            ["interrogate", "--max-turns", "6", "--out", str(tmp_path)],
        )
        assert r.exit_code == 0
        snapshot.assert_match(_normalize(r.output), "interrogate_verdict_atteint.txt")

    def test_interrogate_sans_verdict(self, snapshot, monkeypatch, tmp_path):
        """Sortie quand aucun verdict n'est atteint."""
        from laivelup import cli

        monkeypatch.setattr(cli.Prompt, "ask", lambda prompt, **kw: "pas certain")
        r = runner.invoke(
            cli.app,
            ["interrogate", "--max-turns", "2", "--out", str(tmp_path)],
        )
        assert r.exit_code == 0
        snapshot.assert_match(_normalize(r.output), "interrogate_sans_verdict.txt")


@pytest.mark.snapshot
class TestHelpSnapshot:
    """Snapshots de l'aide CLI."""

    def test_main_help(self, snapshot):
        """Aide principale."""
        r = runner.invoke(app, ["--help"])
        assert r.exit_code == 0
        snapshot.assert_match(r.output, "help_main.txt")

    def test_evaluate_help(self, snapshot):
        """Aide de la commande evaluate."""
        r = runner.invoke(app, ["evaluate", "--help"])
        assert r.exit_code == 0
        snapshot.assert_match(r.output, "help_evaluate.txt")

    def test_interrogate_help(self, snapshot):
        """Aide de la commande interrogate."""
        r = runner.invoke(app, ["interrogate", "--help"])
        assert r.exit_code == 0
        snapshot.assert_match(r.output, "help_interrogate.txt")

    def test_team_help(self, snapshot):
        """Aide du sous-commande team."""
        r = runner.invoke(app, ["team", "--help"])
        assert r.exit_code == 0
        snapshot.assert_match(r.output, "help_team.txt")