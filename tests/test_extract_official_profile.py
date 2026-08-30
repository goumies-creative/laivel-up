# Copyright 2026 Romy Alula — MIT License
"""Tests de régression pour scripts/extract_official_profile.py.

Cible spécifiquement les 4 bugs silencieux documentés dans le docstring du
module (corrigés le 28/08) : chacun laissait un profil officiel réel
(bohort/leodagan/arthur/perceval) mal classé sans lever d'erreur — pas de
crash, pas de message, juste un axe mal noté ou un refus injustifié.
"""

from __future__ import annotations

import json

from scripts.extract_official_profile import (
    _extract_agent_rules_versioned,
    _extract_pr_sizes,
    _extract_prompts,
    _extract_retries_triangulated,
    extract_profile,
)


class TestPrSizesWeighting:
    """Bug historique : pr_sizes ne gardait que la présence par taille
    (["S","M","L"] quel que soit le nombre réel de PR), aplatissant la
    distribution réelle — bohort/leodagan/arthur produisaient tous les
    trois exactement la même liste. Corrigé en dupliquant chaque taille
    par son compte réel."""

    def test_weighted_by_real_count(self):
        git_activity = {'pull_requests': {'size_distribution': {'S': 3, 'M': 1, 'L': 0, 'XS': 2}}}
        sizes = _extract_pr_sizes(git_activity)
        assert sizes.count('S') == 5  # 3 S + 2 XS normalisés en S
        assert sizes.count('M') == 1
        assert 'L' not in sizes  # count=0 exclu, pas juste "présent avec poids 0"
        assert len(sizes) == 6

    def test_no_size_distribution_returns_none(self):
        assert _extract_pr_sizes({'pull_requests': {}}) is None

    def test_zero_counts_return_none(self):
        git_activity = {'pull_requests': {'size_distribution': {'S': 0, 'M': 0}}}
        assert _extract_pr_sizes(git_activity) is None


class TestPromptsSignal:
    """Bug historique : le signal `prompts` (signal plancher du harness)
    n'était jamais renseigné — un profil avec context_files entièrement à
    false (cas réel perceval) était refusé (aucun axe harness décidé) au
    lieu d'obtenir RED. Corrigé en dérivant `prompts` depuis assistant_usage."""

    def test_declared_tools_gives_prompts_true(self):
        git_activity = {'assistant_usage': {'declared_tools': ['Copilot'], 'sessions_per_week': 0}}
        assert _extract_prompts(git_activity) is True

    def test_sessions_without_declared_tools_gives_prompts_true(self):
        git_activity = {'assistant_usage': {'declared_tools': [], 'sessions_per_week': 3}}
        assert _extract_prompts(git_activity) is True

    def test_no_usage_at_all_returns_none(self):
        assert _extract_prompts({}) is None

    def test_empty_usage_returns_false_not_none(self):
        """Distinction importante : usage déclaré mais nul (0 outil, 0 session)
        est un vrai « non », pas une absence de donnée."""
        git_activity = {'assistant_usage': {'declared_tools': [], 'sessions_per_week': 0}}
        assert _extract_prompts(git_activity) is False


class TestAgentRulesVersioned:
    """Bug historique : seul rules_count était regardé. Cas réel arthur :
    rules_count=0 mais agents_count=2 (2 fichiers d'agents réels dans
    repo-context/.claude/agents/) — son harness plafonnait à BLUE au lieu
    de COPPER. Corrigé en combinant rules_count ET agents_count."""

    def test_agents_count_alone_gives_true(self):
        git_activity = {'context_files': {'rules_count': 0, 'agents_count': 2}}
        assert _extract_agent_rules_versioned(git_activity) is True

    def test_rules_count_alone_gives_true(self):
        git_activity = {'context_files': {'rules_count': 3, 'agents_count': 0}}
        assert _extract_agent_rules_versioned(git_activity) is True

    def test_both_zero_gives_false(self):
        git_activity = {'context_files': {'rules_count': 0, 'agents_count': 0}}
        assert _extract_agent_rules_versioned(git_activity) is False

    def test_both_absent_gives_none(self):
        assert _extract_agent_rules_versioned({'context_files': {}}) is None


class TestRetriesTriangulated:
    """Bug historique : basé sur reverted > 0 — refusait leodagan (0 revert)
    alors que son retries_after_fact vient de métriques git objectives
    (git-activity.json), pas d'un déclaratif. declaratif.md est par
    définition une donnée suggestive, jamais une mesure. Corrigé : triangulé
    dès que le total de PR est mesurable depuis git-activity.json."""

    def test_measurable_total_with_zero_reverts_is_triangulated(self):
        git_activity = {'pull_requests': {'total': 12, 'reverted': 0}}
        assert _extract_retries_triangulated(git_activity) is True

    def test_no_total_is_not_triangulated(self):
        assert _extract_retries_triangulated({'pull_requests': {'total': 0}}) is None
        assert _extract_retries_triangulated({}) is None


class TestExtractProfileIntegration:
    """Bout-en-bout sur un dossier de profil, cas perceval-like : context_files
    entièrement absent mais assistant_usage présent → prompts=True, pas un
    refus faute de signal ; et le déclaratif ne fuit jamais dans les traces."""

    def test_perceval_like_profile_gets_prompts_signal(self, tmp_path):
        profile_dir = tmp_path / 'perceval'
        profile_dir.mkdir()
        (profile_dir / 'profile.json').write_text(
            json.dumps({'profile_id': 'perceval'}), encoding='utf-8'
        )
        (profile_dir / 'git-activity.json').write_text(
            json.dumps(
                {
                    'pull_requests': {'size_distribution': {'S': 2}, 'total': 2},
                    'context_files': {},
                    'assistant_usage': {'declared_tools': ['ChatGPT'], 'sessions_per_week': 1},
                }
            ),
            encoding='utf-8',
        )
        profile = extract_profile(profile_dir)
        assert profile.traces['prompts'] is True
        assert profile.traces.get('context_versioned') is None

    def test_declaratif_never_leaks_into_traces(self, tmp_path):
        """Invariant documenté dans METHODE.md : le déclaratif n'est jamais
        deviné ni injecté dans les traces, seulement dans declared_level."""
        profile_dir = tmp_path / 'x'
        profile_dir.mkdir()
        (profile_dir / 'profile.json').write_text(json.dumps({'profile_id': 'x'}), encoding='utf-8')
        (profile_dir / 'declaratif.md').write_text('Je pense être GOLD.', encoding='utf-8')
        profile = extract_profile(profile_dir)
        assert profile.declared_level is not None
        assert 'declared_level' not in profile.traces
        assert 'declaratif' not in profile.traces


class TestSessionMdAgentsAutonomous:
    """session.md, quand present, alimente traces['agents_autonomous']."""

    def test_session_md_with_autonomous_keyword_sets_true(self, tmp_path):
        profile_dir = tmp_path / 'autonomous-profile'
        profile_dir.mkdir()
        (profile_dir / 'profile.json').write_text(
            json.dumps({'profile_id': 'autonomous-profile'}), encoding='utf-8'
        )
        (profile_dir / 'session.md').write_text(
            'Le pipeline CI/CD tourne de manière autonome.', encoding='utf-8'
        )
        profile = extract_profile(profile_dir)
        assert profile.traces['agents_autonomous'] is True

    def test_no_session_md_leaves_key_absent(self, tmp_path):
        profile_dir = tmp_path / 'no-session'
        profile_dir.mkdir()
        (profile_dir / 'profile.json').write_text(
            json.dumps({'profile_id': 'no-session'}), encoding='utf-8'
        )
        profile = extract_profile(profile_dir)
        assert 'agents_autonomous' not in profile.traces
