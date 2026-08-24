# Copyright 2026 Romy Alula — MIT License
"""Générateur de profils valides pour tests de charge et compatibilité.

Utilisé par test_load.py (1k profils) et test_schema_compat.py.
Évite hypothesis pour la génération en masse (lent) ; préfère random.
"""

from __future__ import annotations

import random

from laivelup.model import ProfileData


_SIZES = ['S', 'M', 'L', 'XL']


def make_valid_profile(index: int = 0) -> ProfileData:
    """Génère un profil valide aléatoire (reproductible via seed externe)."""
    rng = random.Random(index)
    n_prs = rng.randint(1, 5)
    pr_sizes = rng.choices(_SIZES, k=n_prs)
    traces: dict = {
        'pr_sizes': pr_sizes,
        'context_versioned': rng.choice([True, False]),
        'agent_rules_versioned': rng.choice([True, False]),
        'retry_loops': rng.choice([True, False]),
        'retries_after_fact': round(rng.random(), 2),
        'retries_triangulated': rng.choice([True, False]),
        'parallel_projects': rng.randint(0, 5),
        'projects_completed': rng.randint(0, 5),
        'agents_autonomous': rng.choice([True, False]),
        'prompts': rng.choice([True, False]),
    }
    return ProfileData(
        name=f'load-profile-{index:04d}',
        declared_level=None,
        traces=traces,
        answers={},
        meta={'generated': True, 'seed': index},
    )


def generate_profiles(count: int = 1000) -> list[ProfileData]:
    """Génère N profils valides (déterministes par seed = index)."""
    return [make_valid_profile(i) for i in range(count)]


def generate_team_profiles(count: int = 50) -> list[ProfileData]:
    """Génère des profils pour tester Team (slugs uniques RGPD)."""
    return [make_valid_profile(1000 + i) for i in range(count)]
