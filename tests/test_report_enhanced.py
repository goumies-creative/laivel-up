# Copyright 2026 Romy Alula — MIT License
"""Tests pour le rapport HTML amélioré (Patapon world map, progress bar, pédagogie)."""

from __future__ import annotations

from laivelup.model import AxisScore, Level, RedFlag, Verdict
from laivelup.report import (
    GLOSSARY,
    REFERENCES,
    render_html,
    render_markdown,
    write_reports,
)


def _make_verdict(**kwargs) -> Verdict:
    defaults = {
        'name': 'Test',
        'level': Level.BLUE,
        'axis_scores': [
            AxisScore(axe='size', level=Level.BLUE, confidence=0.8, evidence=['2 PR M']),
            AxisScore(
                axe='harness', level=Level.BLUE, confidence=0.9, evidence=['context present']
            ),
            AxisScore(
                axe='intervention', level=Level.BLUE, confidence=0.7, evidence=['retry partiel']
            ),
            AxisScore(axe='parallel', level=Level.GREEN, confidence=0.6, evidence=['2 projets']),
        ],
        'limiting_axis': 'size',
        'data_errors': [],
        'red_flags': [],
        'next_steps': [],
    }
    defaults.update(kwargs)
    return Verdict(**defaults)


class TestWorldMap:
    def test_world_map_in_html(self):
        v = _make_verdict()
        html = render_html(v)
        assert 'patapon-world' in html
        assert 'Carte de progression AIDD' in html

    def test_world_nodes_present(self):
        v = _make_verdict()
        html = render_html(v)
        for level in ('WHITE', 'RED', 'BLUE', 'GREEN', 'COPPER', 'SILVER', 'GOLD'):
            assert f'data-level="{level}"' in html

    def test_current_level_highlighted(self):
        v = _make_verdict(level=Level.GREEN)
        html = render_html(v)
        assert 'world-node current' in html
        assert 'NIVEAU DÉBLOQUÉ' in html

    def test_locked_node_for_future_level(self):
        v = _make_verdict(level=Level.RED)
        html = render_html(v)
        assert 'data-level="GOLD"' in html
        assert 'world-node locked' in html


class TestProgressBar:
    def test_progress_bar_in_html(self):
        v = _make_verdict()
        html = render_html(v)
        assert 'progress-bar-container' in html
        assert 'Progression' in html

    def test_progress_fill_width(self):
        v = _make_verdict(level=Level.GREEN)
        html = render_html(v)
        assert 'width:50%' in html  # GREEN = 3/6 = 50%

    def test_undecided_progress(self):
        v = Verdict(name='t', level=None, axis_scores=[], limiting_axis=None)
        html = render_html(v)
        assert 'width:0%' in html
        assert 'Undécis' in html


class TestAxisDetail:
    def test_axis_cards_in_html(self):
        v = _make_verdict()
        html = render_html(v)
        assert 'axis-details' in html
        assert 'Détail par axe' in html

    def test_axis_why_explanation(self):
        v = _make_verdict()
        html = render_html(v)
        assert 'Pourquoi ce niveau ?' in html

    def test_variance_in_html(self):
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
        assert 'pic XL' in html

    def test_empty_axis(self):
        v = _make_verdict(
            axis_scores=[
                AxisScore(axe='size', level=None, confidence=0.0, evidence=[]),
            ]
        )
        html = render_html(v)
        assert 'Données insuffisantes' in html


class TestNextStepsHtml:
    def test_next_steps_section(self):
        v = _make_verdict(next_steps=['Étape 1', 'Étape 2'])
        html = render_html(v)
        assert 'Étape 1' in html
        assert 'Étape 2' in html
        assert "Monter d'un cran" in html

    def test_no_next_steps(self):
        v = _make_verdict(next_steps=[])
        html = render_html(v)
        assert "Monter d'un cran" not in html


class TestFlagsHtml:
    def test_flags_section(self):
        v = _make_verdict(
            red_flags=[RedFlag(severite=2, titre='Flag', constat='x', source='y', question='Q?')]
        )
        html = render_html(v)
        assert 'Flag' in html
        assert 'Q?' in html
        assert 'Alertes' in html

    def test_no_flags(self):
        v = _make_verdict(red_flags=[])
        html = render_html(v)
        assert 'Red flags' not in html


class TestPedagogySection:
    def test_glossary_in_html(self):
        v = _make_verdict()
        html = render_html(v)
        assert 'Glossaire AIDD' in html
        for term in GLOSSARY:
            assert term in html

    def test_references_in_html(self):
        v = _make_verdict()
        html = render_html(v)
        assert 'Références curatées' in html
        for ref in REFERENCES:
            assert ref['title'] in html

    def test_progression_guide(self):
        v = _make_verdict(limiting_axis='harness', level=Level.RED)
        html = render_html(v)
        assert 'Comment progresser vers le niveau suivant' in html
        assert 'Harness' in html


class TestTransparency:
    def test_transparency_section(self):
        v = _make_verdict()
        html = render_html(v)
        assert 'Transparence' in html
        assert 'neurotype' in html

    def test_no_limiting_axis(self):
        v = _make_verdict(limiting_axis=None)
        html = render_html(v)
        assert 'Axe plancher' not in html


class TestFooter:
    def test_footer_in_html(self):
        v = _make_verdict()
        html = render_html(v)
        assert 'report-footer' in html
        assert 'LAIVEL UP' in html


class TestMarkdown:
    def test_basic_md(self):
        v = _make_verdict()
        md = render_markdown(v)
        assert '# Verdict AIDD' in md
        assert 'Taille' in md

    def test_md_next_steps(self):
        v = _make_verdict(next_steps=['Step 1'])
        md = render_markdown(v)
        assert 'Step 1' in md


class TestWriteReports:
    def test_md_and_html(self, tmp_path):
        v = _make_verdict()
        md, html = write_reports(v, tmp_path)
        assert md.exists()
        assert html is not None and html.exists()

    def test_md_only(self, tmp_path):
        v = _make_verdict()
        md, html = write_reports(v, tmp_path, with_html=False)
        assert md.exists()
        assert html is None

    def test_slug_in_filename(self, tmp_path):
        v = _make_verdict(name='Mon Profil')
        md, _ = write_reports(v, tmp_path)
        assert 'mon-profil' in md.name.lower()
