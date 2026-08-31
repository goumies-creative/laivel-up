# Copyright 2026 Romy Alula — MIT License
"""Tests pour le rapport HTML (design system console LAIVEL-UP)."""

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


class TestVerdictHero:
    def test_hero_section_in_html(self):
        v = _make_verdict()
        html = render_html(v)
        assert 'verdict-hero' in html
        assert 'LAIVEL-UP / VERDICT' in html

    def test_level_name_in_hero(self):
        v = _make_verdict(level=Level.GREEN)
        html = render_html(v)
        assert 'Green' in html

    def test_limiting_axis_displayed(self):
        v = _make_verdict(limiting_axis='size')
        html = render_html(v)
        assert 'AXE PLANCHER' in html
        assert 'Taille' in html

    def test_no_limiting_axis(self):
        v = _make_verdict(limiting_axis=None)
        html = render_html(v)
        assert 'class="hero-limiting"' not in html


class TestConfidence:
    def test_confidence_bar_in_html(self):
        v = _make_verdict()
        html = render_html(v)
        assert 'confidence' in html
        assert 'CONFIANCE' in html

    def test_confidence_percentage(self):
        v = _make_verdict(level=Level.GREEN)
        html = render_html(v)
        assert '60%' in html  # min(0.8, 0.9, 0.7, 0.6) = 0.6

    def test_undecided_confidence(self):
        v = Verdict(name='t', level=None, axis_scores=[], limiting_axis=None)
        html = render_html(v)
        assert '—' in html


class TestAxisDetail:
    def test_axis_cards_in_html(self):
        v = _make_verdict()
        html = render_html(v)
        assert 'axis-grid' in html
        assert 'Axes' in html

    def test_axis_card_content(self):
        v = _make_verdict()
        html = render_html(v)
        assert 'Taille' in html
        assert 'CONFIANCE' in html
        assert 'OBSERVATIONS' in html

    def test_limiting_axis_highlighted(self):
        v = _make_verdict(limiting_axis='size')
        html = render_html(v)
        assert 'axis-card-limiting' in html
        assert 'AXE PLANCHER' in html

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
        assert 'Aucune trace' in html


class TestNextStepsHtml:
    def test_next_steps_section(self):
        v = _make_verdict(next_steps=['Étape 1', 'Étape 2'])
        html = render_html(v)
        assert 'Étape 1' in html
        assert 'Étape 2' in html
        assert 'Next Steps' in html

    def test_no_next_steps(self):
        v = _make_verdict(next_steps=[])
        html = render_html(v)
        assert 'class="section next-steps-section"' not in html


class TestFlagsHtml:
    def test_flags_section(self):
        v = _make_verdict(
            red_flags=[RedFlag(severite=2, titre='Flag', constat='x', source='y', question='Q?')]
        )
        html = render_html(v)
        assert 'Flag' in html
        assert 'Q?' in html
        assert 'Red Flags' in html

    def test_no_flags(self):
        v = _make_verdict(red_flags=[])
        html = render_html(v)
        assert 'AUCUNE ALERTE' in html


class TestPedagogySection:
    def test_glossary_in_html(self):
        v = _make_verdict()
        html = render_html(v)
        assert 'Glossaire' in html
        for term in GLOSSARY:
            assert term in html

    def test_glossary_reprise_definition(self):
        v = _make_verdict()
        html = render_html(v)
        assert 'Reprise (proportion de)' in html
        assert 'commits correctifs' in html
        assert 'cellule Red' in html
        assert 'traces du profil' in html

    def test_references_in_html(self):
        v = _make_verdict()
        html = render_html(v)
        assert 'RÉFÉRENCES CURATÉES' in html
        for ref in REFERENCES:
            assert ref['title'] in html

    def test_progression_guide(self):
        v = _make_verdict(limiting_axis='harness', level=Level.RED)
        html = render_html(v)
        assert 'Comment monter' in html
        assert 'Harness' in html


class TestTransparency:
    def test_transparency_section(self):
        v = _make_verdict()
        html = render_html(v)
        assert 'Transparence' in html
        assert 'neurotype' in html


class TestFooter:
    def test_footer_in_html(self):
        v = _make_verdict()
        html = render_html(v)
        assert 'system-footer' in html
        assert 'LAIVEL-UP' in html


class TestRefusal:
    def test_refusal_screen(self):
        v = Verdict(name='t', level=None, axis_scores=[], limiting_axis=None)
        html = render_html(v)
        assert 'refusal-screen' in html
        assert 'REFUS' in html

    def test_refusal_with_errors(self):
        v = Verdict(name='t', level=None, axis_scores=[], limiting_axis=None, data_errors=['err'])
        html = render_html(v)
        assert 'refusal-errors' in html
        assert 'err' in html


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
