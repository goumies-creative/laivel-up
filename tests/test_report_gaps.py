# Copyright 2026 Romy Alula — MIT License
"""Tests item 7 : ecarts types pratique (✗ U+2717) vs preuve (?).

Moteur (scoring) + rendu (Markdown/HTML) + serialisation (verdict_to_dict).
"""

from __future__ import annotations

from laivelup.model import AxisScore, Gap, Level, ProfileData, Verdict
from laivelup.report import (
    GAP_PRACTICE_MARK,
    GAP_PROOF_MARK,
    _gap_mark,
    render_html,
    render_markdown,
    verdict_to_dict,
)
from laivelup.scoring import evaluate


def _decided_profile() -> ProfileData:
    return ProfileData(
        name='decide',
        traces={
            'pr_sizes': ['M', 'M'],
            'context_versioned': True,
            'retries_after_fact': 0.4,
            'retries_triangulated': True,
            'parallel_projects': 1,
        },
    )


def _refused_profile() -> ProfileData:
    return ProfileData(name='vide', traces={})


class TestGapSymbols:
    def test_practice_mark_is_ballot_x(self):
        assert GAP_PRACTICE_MARK == '✗'
        assert ord(GAP_PRACTICE_MARK) == 0x2717

    def test_proof_mark_is_question(self):
        assert GAP_PROOF_MARK == '?'

    def test_gap_mark_practice(self):
        assert _gap_mark('practice') == '✗'

    def test_gap_mark_proof(self):
        assert _gap_mark('proof') == '?'

    def test_gap_mark_unknown_defaults_to_proof(self):
        assert _gap_mark('nimporte-quoi') == '?'


class TestScoringGaps:
    def test_refusal_gaps_are_all_proof(self):
        verdict = evaluate(_refused_profile())
        assert verdict.level is None
        assert verdict.gaps, 'un refus doit typer ses ecarts'
        assert [g.text for g in verdict.gaps] == verdict.next_steps
        assert all(g.kind == 'proof' for g in verdict.gaps)

    def test_decided_gaps_are_practice(self):
        verdict = evaluate(_decided_profile())
        assert verdict.decided
        assert verdict.gaps, 'un verdict decide doit typer ses ecarts'
        assert [g.text for g in verdict.gaps] == verdict.next_steps
        assert all(g.kind == 'practice' for g in verdict.gaps)

    def test_silver_without_autonomy_adds_proof_gap(self):
        profile = ProfileData(
            name='silver',
            traces={
                'pr_sizes': ['XL', 'XL', 'XL', 'L'],
                'context_versioned': True,
                'agent_rules_versioned': True,
                'retry_loops': True,
                'retries_after_fact': 0.0,
                'retries_triangulated': True,
                'parallel_projects': 3,
                'projects_completed': 3,
            },
        )
        verdict = evaluate(profile)
        assert verdict.level == Level.SILVER
        kinds = [g.kind for g in verdict.gaps]
        assert kinds[0] == 'practice'
        assert kinds[-1] == 'proof'
        assert 'autonomie' in verdict.gaps[-1].text

    def test_data_errors_gaps_are_proof(self):
        profile = ProfileData(name='menteur', traces={'pr_sizes': 'PAS-UNE-LISTE'})  # type: ignore[dict-item]
        verdict = evaluate(profile)
        assert verdict.data_errors
        assert verdict.gaps
        assert all(g.kind == 'proof' for g in verdict.gaps)


class TestMarkdownGaps:
    def _verdict(self) -> Verdict:
        return Verdict(
            name='t',
            level=None,
            axis_scores=[],
            limiting_axis='size',
            next_steps=['Passer de S à M', 'Quelle part est reprise ?'],
            gaps=[
                Gap(text='Passer de S à M', kind='practice'),
                Gap(text='Quelle part est reprise ?', kind='proof'),
            ],
        )

    def test_markdown_shows_both_marks(self):
        md = render_markdown(self._verdict())
        assert '- ✗ Passer de S à M' in md
        assert '- ? Quelle part est reprise ?' in md

    def test_markdown_legend(self):
        md = render_markdown(self._verdict())
        assert 'Légende' in md
        assert 'écart de pratique' in md
        assert 'écart de preuve' in md
        assert 'refus de deviner' in md

    def test_markdown_legacy_without_gaps(self):
        v = Verdict(
            name='t', level=Level.BLUE, axis_scores=[], limiting_axis='size', next_steps=['Step 1']
        )
        md = render_markdown(v)
        assert '- Step 1' in md
        assert 'Légende' not in md


class TestHtmlGaps:
    def _verdict(self) -> Verdict:
        return Verdict(
            name='t',
            level=Level.BLUE,
            axis_scores=[
                AxisScore(axe='size', level=Level.BLUE, confidence=0.8, evidence=['2 PR M']),
            ],
            limiting_axis='size',
            next_steps=['Passer de S à M', 'Quelle part est reprise ?'],
            gaps=[
                Gap(text='Passer de S à M', kind='practice'),
                Gap(text='Quelle part est reprise ?', kind='proof'),
            ],
        )

    def test_html_shows_both_marks(self):
        html = render_html(self._verdict())
        assert '✗' in html
        assert 'gap-practice' in html
        assert 'gap-proof' in html
        assert 'Passer de S à M' in html

    def test_html_legend(self):
        html = render_html(self._verdict())
        assert 'gaps-legend' in html
        assert 'écart de pratique' in html
        assert 'écart de preuve' in html

    def test_html_legacy_without_gaps(self):
        v = Verdict(
            name='t',
            level=Level.BLUE,
            axis_scores=[
                AxisScore(axe='size', level=Level.BLUE, confidence=0.8, evidence=['2 PR M']),
            ],
            limiting_axis='size',
            next_steps=['Step 1'],
        )
        html = render_html(v)
        assert 'Step 1' in html
        assert 'gaps-legend' not in html

    def test_html_refusal_shows_proof_gaps(self):
        v = Verdict(
            name='t',
            level=None,
            axis_scores=[],
            limiting_axis='size',
            next_steps=['Quelle part est reprise ?'],
            gaps=[Gap(text='Quelle part est reprise ?', kind='proof')],
        )
        html = render_html(v)
        assert 'refusal-screen' in html
        assert '?' in html
        assert 'gap-proof' in html
        assert 'gaps-legend' in html


class TestVerdictToDictGaps:
    def test_gaps_serialized_with_type(self):
        v = Verdict(
            name='t',
            level=Level.BLUE,
            axis_scores=[],
            limiting_axis='size',
            next_steps=['a', 'b'],
            gaps=[Gap(text='a', kind='practice'), Gap(text='b', kind='proof')],
        )
        data = verdict_to_dict(v)
        assert data['gaps'] == [
            {'text': 'a', 'type': 'practice'},
            {'text': 'b', 'type': 'proof'},
        ]
        # next_steps reste une liste de str (compat CLI/interrogate).
        assert data['next_steps'] == ['a', 'b']

    def test_empty_gaps_serialized(self):
        v = Verdict(name='t', level=None, axis_scores=[], limiting_axis=None)
        assert verdict_to_dict(v)['gaps'] == []

    def test_evaluate_roundtrip_jsonable(self):
        import json

        data = verdict_to_dict(evaluate(_decided_profile()))
        json.dumps(data, ensure_ascii=False)
        assert all('type' in g for g in data['gaps'])
