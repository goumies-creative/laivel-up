# Copyright 2026 Romy Alula — MIT License
"""Tests basés sur les propriétés (hypothesis) pour le moteur d'évaluation AIDD.

Vérifie les invariantes fondamentales :
- Le verdict est toujours cohérent (jamais de niveau sans données suffisantes)
- La confiance est toujours entre 0 et 1
- Les red flags portent toujours une question
- Les next_steps sont toujours des strings non vides
"""

from __future__ import annotations

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

from laivelup.model import Level, ProfileData, AXES
from laivelup.scoring import evaluate, normalize_profile, SIZE_VALUES


# Stratégies pour générer des profils valides

st_level = st.sampled_from(list(Level))
st_pr_size = st.sampled_from(list(SIZE_VALUES))
st_pr_sizes = st.lists(st_pr_size, min_size=0, max_size=50)
st_ratio = st.floats(min_value=0.0, max_value=1.0)
st_int = st.integers(min_value=0, max_value=20)
st_bool = st.booleans()


def make_profile(
    pr_sizes=None,
    context_versioned=False,
    agent_rules_versioned=False,
    retry_loops=False,
    retries_after_fact=None,
    retries_triangulated=True,
    parallel_projects=None,
    projects_completed=None,
    agents_autonomous=False,
    declared_level=None,
):
    """Helper pour construire un profil de test."""
    traces = {}
    if pr_sizes is not None:
        traces['pr_sizes'] = pr_sizes
    if context_versioned:
        traces['context_versioned'] = True
    if agent_rules_versioned:
        traces['agent_rules_versioned'] = True
    if retry_loops:
        traces['retry_loops'] = True
    if retries_after_fact is not None:
        traces['retries_after_fact'] = retries_after_fact
    if retries_triangulated:
        traces['retries_triangulated'] = True
    if parallel_projects is not None:
        traces['parallel_projects'] = parallel_projects
    if projects_completed is not None:
        traces['projects_completed'] = projects_completed
    if agents_autonomous:
        traces['agents_autonomous'] = True
    return ProfileData(
        name='test',
        declared_level=declared_level,
        traces=traces,
    )


class TestInvariants:
    """Invariantes fondamentales du moteur d'évaluation."""

    @given(st_pr_sizes)
    @settings(max_examples=100)
    def test_verdict_toujours_coherent(self, pr_sizes):
        """Le verdict est toujours cohérent : si decided, le niveau est dans l'enum."""
        profile = make_profile(pr_sizes=pr_sizes)
        verdict = evaluate(profile)

        if verdict.decided:
            assert verdict.level is not None
            assert isinstance(verdict.level, Level)
            assert verdict.level in Level

    @given(st_pr_sizes)
    @settings(max_examples=100)
    def test_confiance_toujours_entre_0_et_1(self, pr_sizes):
        """La confiance est toujours entre 0 et 1."""
        profile = make_profile(pr_sizes=pr_sizes)
        verdict = evaluate(profile)

        for axis in verdict.axis_scores:
            assert 0.0 <= axis.confidence <= 1.0, (
                f"Confiance hors limites : {axis.confidence} pour l'axe {axis.axe}"
            )

    @given(st_pr_sizes)
    @settings(max_examples=100)
    def test_red_flags_portent_une_question(self, pr_sizes):
        """Les red flags portent toujours une question ou une explication."""
        profile = make_profile(
            pr_sizes=pr_sizes,
            declared_level=Level.BLUE,
        )
        verdict = evaluate(profile)

        for flag in verdict.red_flags:
            assert flag.titre
            assert flag.constat
            assert flag.source
            if flag.question:
                assert len(flag.question) > 10

    @given(st_pr_sizes)
    @settings(max_examples=100)
    def test_next_steps_sont_des_strings_non_vides(self, pr_sizes):
        """Les next_steps sont toujours des strings non vides."""
        profile = make_profile(pr_sizes=pr_sizes)
        verdict = evaluate(profile)

        for step in verdict.next_steps:
            assert isinstance(step, str)
            assert len(step) > 0

    @given(st_pr_sizes)
    @settings(max_examples=100)
    def test_limiting_axis_est_valide(self, pr_sizes):
        """L'axe limitant est toujours un axe valide de la grille."""
        profile = make_profile(pr_sizes=pr_sizes)
        verdict = evaluate(profile)

        if verdict.limiting_axis is not None:
            assert verdict.limiting_axis in AXES

    @given(st_pr_sizes)
    @settings(max_examples=100)
    def test_axis_scores_couvre_tous_les_axes(self, pr_sizes):
        """Le verdict couvre toujours les 4 axes."""
        profile = make_profile(pr_sizes=pr_sizes)
        verdict = evaluate(profile)

        assert len(verdict.axis_scores) == 4
        axe_names = {a.axe for a in verdict.axis_scores}
        assert axe_names == set(AXES)


class TestEquite:
    """Tests d'équité structurelle : l'outil ne juge jamais plus bas que les données."""

    @given(st_pr_sizes)
    @settings(max_examples=100)
    def test_sans_donnees_refuse(self, pr_sizes):
        """Un profil sans traces ne donne jamais de verdict."""
        profile = make_profile()
        verdict = evaluate(profile)
        assert not verdict.decided

    @given(st_ratio)
    @settings(max_examples=100)
    def test_ratio_non_triangule_refuse(self, ratio):
        """Un ratio non triangulé ne donne jamais de verdict (équité)."""
        assume(ratio is not None)
        profile = make_profile(
            pr_sizes=['M', 'M'],
            retries_after_fact=ratio,
            retries_triangulated=False,
        )
        verdict = evaluate(profile)
        itv = next((a for a in verdict.axis_scores if a.axe == 'intervention'), None)
        if itv and itv.level is not None:
            assert itv.confidence < 0.5

    @given(st.integers(min_value=-10, max_value=-1))
    @settings(max_examples=50)
    def test_taille_negatif_refuse(self, n):
        """Un nombre négatif de chantiers est invalide."""
        profile = make_profile(
            parallel_projects=n,
        )
        verdict = evaluate(profile)
        assert not verdict.decided
        assert verdict.data_errors

    @given(st_pr_size, st_pr_size)
    @settings(max_examples=100)
    def test_egyalite_tailles_refuse(self, s1, s2):
        """Une égalité parfaite entre tailles refuse (pas de level arbitraire)."""
        assume(s1 != s2)
        profile = make_profile(
            pr_sizes=[s1, s1, s2, s2],
        )
        verdict = evaluate(profile)
        taille = next((a for a in verdict.axis_scores if a.axe == 'size'), None)
        if taille:
            assert taille.confidence < 0.5


class TestNormalize:
    """Tests de normalisation des profils."""

    @given(st_pr_sizes)
    @settings(max_examples=100)
    def test_normalize_retourne_liste(self, pr_sizes):
        """normalize_profile retourne toujours une liste."""
        profile = make_profile(pr_sizes=pr_sizes)
        errors = normalize_profile(profile)
        assert isinstance(errors, list)

    def test_bool_est_invalide(self):
        """Un booléen à la place d'un ratio est invalide."""
        profile = make_profile(retries_after_fact=False)
        errors = normalize_profile(profile)
        assert any('retries_after_fact' in e for e in errors)

    def test_string_est_invalide(self):
        """Une chaîne à la place d'un entier est invalide."""
        profile = make_profile(parallel_projects='trois')
        errors = normalize_profile(profile)
        assert any('parallel_projects' in e for e in errors)
