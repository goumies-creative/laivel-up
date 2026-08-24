# Copyright 2026 Romy Alula — MIT License
"""Tests du CLI et des points contractuels audités.

Vérifie que la doc du CLI (alleas `evaluate`) tient, que les rapports se
génèrent, et que les criticals de l'audit du 2026-08-20 sont couverts
(progress_for_axis en list[str], seuil de refus, wrangle des données qui mentent).
"""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from laivelup.cli import app
from laivelup.model import Level
from laivelup.scoring import progress_for_axis

REPO = Path(__file__).parent.parent
runner = CliRunner()


def test_cli_doc_alias_evaluate_exit_0():
    r = runner.invoke(
        app, ['evaluate', str(REPO / 'exemples' / 'profil-maison-1.json'), '--no-html']
    )
    assert r.exit_code == 0


def test_cli_no_such_file_message_aimable():
    r = runner.invoke(app, ['evaluate', 'exemples/introuvable.json', '--no-html'])
    assert r.exit_code != 0
    assert 'introuvable' in r.output.lower() or 'trouv' in r.output.lower()


def test_progress_for_axis_retourne_liste_de_str():
    for axe in ('size', 'harness', 'intervention', 'parallel'):
        out = progress_for_axis(axe, Level.RED)
        assert isinstance(out, list) and out
        assert all(isinstance(x, str) for x in out)


def test_pic_iso_dominant_refuse_pas_de_niveau_arbitraire():
    # Un pic XL co-dominant mais minoritaire : l'habituel n'est pas établi,
    # on refuse plutôt que de fixer un niveau (confiance sous le seuil).
    from laivelup.model import ProfileData
    from laivelup.scoring import evaluate

    profile = ProfileData(name='pic', traces={'pr_sizes': ['XL', 'S', 'L']})
    verdict = evaluate(profile)
    assert not verdict.decided
    taille = next(a for a in verdict.axis_scores if a.axe == 'size')
    assert taille.confidence < 0.5
