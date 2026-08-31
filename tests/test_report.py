# Copyright 2026 Romy Alula — MIT License
"""Tests report.py : render_markdown, render_html, write_reports.

Cible : 85% branch sur report.py.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from laivelup.model import AxisScore, Level, ProfileData, RedFlag, Verdict
from laivelup.report import render_html, render_markdown, write_reports


def _make_verdict(**kwargs) -> Verdict:
    defaults = dict(
        name='test-profile',
        level=Level.BLUE,
        axis_scores=[],
        limiting_axis='size',
    )
    defaults.update(kwargs)
    return Verdict(**defaults)


# --- render_markdown ---------------------------------------------------


class TestRenderMarkdown:
    def test_decided_level(self):
        v = _make_verdict(level=Level.GOLD)
        md = render_markdown(v)
        assert 'Gold' in md
        assert 'Niveau' in md

    def test_undecided(self):
        v = _make_verdict(level=None, limiting_axis=None)
        md = render_markdown(v)
        assert 'non déterminable' in md

    def test_data_errors(self):
        v = _make_verdict(level=None, data_errors=['traces must be a dict'])
        md = render_markdown(v)
        assert 'Données invalides' in md
        assert 'traces must be a dict' in md

    def test_axis_scores(self):
        v = _make_verdict(
            axis_scores=[
                AxisScore(axe='size', level=Level.BLUE, confidence=0.8, evidence=['3 PR S']),
            ]
        )
        md = render_markdown(v)
        assert 'Taille' in md
        assert '80%' in md

    def test_axis_with_variance(self):
        v = _make_verdict(
            axis_scores=[
                AxisScore(
                    axe='size',
                    level=Level.BLUE,
                    confidence=0.8,
                    evidence=['3 PR S'],
                    variance='pic XL isolé',
                ),
            ]
        )
        md = render_markdown(v)
        assert 'variance' in md
        assert 'pic XL' in md

    def test_red_flags_with_question(self):
        v = _make_verdict(
            red_flags=[
                RedFlag(
                    severite=2,
                    titre='Test flag',
                    constat='constat test',
                    source='source test',
                    question='Question test ?',
                )
            ]
        )
        md = render_markdown(v)
        assert 'Test flag' in md
        assert 'Question test' in md

    def test_red_flags_without_question(self):
        v = _make_verdict(red_flags=[RedFlag(severite=1, titre='Flag', constat='x', source='y')])
        md = render_markdown(v)
        assert 'Flag' in md

    def test_next_steps(self):
        v = _make_verdict(next_steps=['Passer à L', 'Maintenir le niveau'])
        md = render_markdown(v)
        assert 'Passer à L' in md
        assert 'Maintenir le niveau' in md

    def test_transparency_section(self):
        v = _make_verdict()
        md = render_markdown(v)
        assert 'Transparence' in md
        assert 'neurotype' in md

    def test_limiting_axis(self):
        v = _make_verdict(limiting_axis='harness')
        md = render_markdown(v)
        assert '**Axe plancher / faible :** Harness' in md


# --- render_html -------------------------------------------------------


class TestRenderHtml:
    def test_decided_ok(self):
        v = _make_verdict(level=Level.GREEN)
        html = render_html(v)
        assert 'ok' in html
        assert 'Green' in html

    def test_undecided_ko(self):
        v = _make_verdict(level=None, limiting_axis=None)
        html = render_html(v)
        assert 'ko' in html
        assert 'insuffisantes' in html

    def test_data_errors_ko(self):
        v = _make_verdict(level=None, data_errors=['erreur test'])
        html = render_html(v)
        assert 'ko' in html
        assert 'Données invalides' in html

    def test_axis_table(self):
        v = _make_verdict(
            axis_scores=[
                AxisScore(axe='size', level=Level.RED, confidence=0.4, evidence=['1 PR S']),
            ]
        )
        html = render_html(v)
        assert 'Taille' in html
        assert '40%' in html

    def test_axis_with_variance(self):
        v = _make_verdict(
            axis_scores=[
                AxisScore(
                    axe='size',
                    level=Level.BLUE,
                    confidence=0.8,
                    evidence=['3 PR S'],
                    variance='pic XL',
                ),
            ]
        )
        html = render_html(v)
        assert 'variance' in html

    def test_red_flags_html(self):
        v = _make_verdict(
            red_flags=[
                RedFlag(severite=2, titre='Flag', constat='x', source='y', question='Question ?')
            ]
        )
        html = render_html(v)
        assert 'Flag' in html
        assert 'Question' in html

    def test_red_flags_no_question(self):
        v = _make_verdict(red_flags=[RedFlag(severite=1, titre='F', constat='x', source='y')])
        html = render_html(v)
        assert 'F' in html

    def test_next_steps_html(self):
        v = _make_verdict(next_steps=['Étape 1'])
        html = render_html(v)
        assert 'Étape 1' in html

    def test_transparency_html(self):
        v = _make_verdict()
        html = render_html(v)
        assert 'Transparence' in html

    def test_no_limiting_axis(self):
        v = _make_verdict(limiting_axis=None)
        html = render_html(v)
        assert 'Axe plancher' not in html


# --- write_reports -----------------------------------------------------


class TestWriteReports:
    def test_write_md_and_html(self, tmp_path):
        v = _make_verdict()
        md, html = write_reports(v, tmp_path)
        assert md.exists()
        assert html is not None
        assert html.exists()
        assert 'Verdict' in md.read_text(encoding='utf-8')

    def test_write_md_only(self, tmp_path):
        v = _make_verdict()
        md, html = write_reports(v, tmp_path, with_html=False)
        assert md.exists()
        assert html is None

    def test_slug_in_filename(self, tmp_path):
        v = _make_verdict(name='Mon Profil')
        md, _ = write_reports(v, tmp_path)
        assert 'mon-profil' in md.name.lower()

    def test_timestamped_filename(self, tmp_path):
        """Les rapports de verdict sont horodatés : jamais écrasés."""
        v = _make_verdict()
        md1, html1 = write_reports(v, tmp_path, stamp='20260831-060000')
        md2, html2 = write_reports(v, tmp_path, stamp='20260831-060100')
        assert md1.name.endswith('-20260831-060000.md')
        assert md2.name.endswith('-20260831-060100.md')
        assert md1.name != md2.name
        assert html1 is not None and html2 is not None
        assert md1.exists() and md2.exists()

    def test_default_stamp_format(self, tmp_path):
        """Sans stamp injecté : suffixe horodaté YYYYMMDD-HHMMSS (slug + sel hex)."""
        import re

        v = _make_verdict()
        md, _ = write_reports(v, tmp_path)
        assert re.fullmatch(r'test-profile-[0-9a-f]{8}-\d{8}-\d{6}\.md', md.name), md.name

    def test_slug_escape_raises_value_error(self, tmp_path, monkeypatch):
        """Sécurité : un slug malicieux qui s'échappe du dossier de sortie est refusé."""
        from laivelup import report as report_mod

        monkeypatch.setattr(report_mod, 'slug', lambda _name: '../evil')
        v = _make_verdict()
        with pytest.raises(ValueError, match='escapes output directory'):
            report_mod.write_reports(v, tmp_path)


# --- _glossary_tooltip --------------------------------------------------


class TestGlossaryTooltip:
    def test_known_term_returns_tooltip_span(self):
        from laivelup.report import _glossary_tooltip

        html = _glossary_tooltip('Harness')
        assert 'glossary-term' in html
        assert 'data-tooltip' in html
        assert 'Harness' in html

    def test_unknown_term_returns_escaped_text_only(self):
        from laivelup.report import _glossary_tooltip

        html = _glossary_tooltip('Terme Inconnu XYZ')
        assert 'glossary-term' not in html
        assert 'Terme Inconnu XYZ' in html
