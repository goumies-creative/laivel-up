# Copyright 2026 Romy Alula — MIT License
"""Tests de charge : 1k profils + équipe 50 membres < 5s."""

from __future__ import annotations

import os
import time

import pytest

from laivelup.model import ProfileData
from laivelup.scoring import evaluate
from laivelup.team import Team, create_team, evaluate_member
from tests.fixtures.load_generator import generate_profiles, generate_team_profiles


# Seuil configurable via env var (CI lent)
MAX_SECONDS = float(os.environ.get('LOAD_TEST_MAX_SECONDS', '5.0'))


@pytest.mark.slow
def test_load_1k_profiles():
    """Évaluer 1000 profils valides en < 5s."""
    profiles = generate_profiles(1000)

    start = time.perf_counter()
    results = [evaluate(p) for p in profiles]
    elapsed = time.perf_counter() - start

    assert len(results) == 1000
    assert all(r.decided or r.level is None for r in results)
    assert elapsed < MAX_SECONDS, f'1k profils: {elapsed:.2f}s > {MAX_SECONDS}s'

    print(f'\n[LOAD] 1000 profils évalués en {elapsed:.2f}s ({1000 / elapsed:.0f} profils/s)')


@pytest.mark.slow
def test_load_team_50():
    """Créer équipe 50 membres + évaluer chacun en < 5s."""
    profiles = generate_team_profiles(50)
    member_names = [p.name for p in profiles]
    profiles_map = {p.name: p for p in profiles}

    start = time.perf_counter()
    team = create_team('load-test-team', member_names)
    team_created = time.perf_counter() - start

    start = time.perf_counter()
    results = []
    for slug, member in team.members.items():
        profile = profiles_map[member.name]
        verdict = evaluate_member(team, slug, profile)
        results.append(verdict)
    team_evaluated = time.perf_counter() - start

    total_elapsed = team_created + team_evaluated

    assert len(team.members) == 50
    assert len(results) == 50
    assert all(r is not None for r in results)
    assert total_elapsed < MAX_SECONDS, f'Team 50: {total_elapsed:.2f}s > {MAX_SECONDS}s'

    print(
        f'\n[LOAD] Team 50 créée en {team_created:.3f}s, évaluée en {team_evaluated:.3f}s, total {total_elapsed:.2f}s'
    )
