# Copyright 2026 Romy Alula — MIT License
"""Tests for scoring_defaults extraction (R1, R2)."""

from __future__ import annotations

import pytest

from laivelup.model import Level
from laivelup.scoring_defaults import SCORING_DEFAULTS


def test_scoring_defaults_exists_and_has_all_keys():
    expected_keys = {
        'CONFIDENCE_THRESHOLD',
        'CONFIDENCE_PEAK',
        'CONFIDENCE_MEDIUM',
        'CONFIDENCE_LOW',
        'CONFIDENCE_HARNESS_ONLY',
        'RETRIES_PER_LEVEL',
        'SIZE_LEVEL',
    }
    assert set(SCORING_DEFAULTS.keys()) == expected_keys


def test_confidence_threshold_value():
    assert SCORING_DEFAULTS['CONFIDENCE_THRESHOLD'] == 0.5


def test_retries_per_level_values():
    rpl = SCORING_DEFAULTS['RETRIES_PER_LEVEL']
    assert rpl['gold'] == 0.05
    assert rpl['copper_or_green'] == 0.2
    assert rpl['blue'] == 0.5


def test_size_level_maps_to_level_enum():
    sl = SCORING_DEFAULTS['SIZE_LEVEL']
    assert sl['S'] is Level.RED
    assert sl['M'] is Level.BLUE
    assert sl['L'] is Level.GOLD
    assert sl['XL'] is Level.GOLD


def test_backward_compat_aliases_match_defaults():
    from laivelup.scoring import (
        CONFIDENCE_THRESHOLD,
        CONFIDENCE_PEAK,
        CONFIDENCE_MEDIUM,
        CONFIDENCE_LOW,
        CONFIDENCE_HARNESS_ONLY,
        RETRIES_PER_LEVEL,
    )

    assert SCORING_DEFAULTS['CONFIDENCE_THRESHOLD'] == CONFIDENCE_THRESHOLD
    assert SCORING_DEFAULTS['CONFIDENCE_PEAK'] == CONFIDENCE_PEAK
    assert SCORING_DEFAULTS['CONFIDENCE_MEDIUM'] == CONFIDENCE_MEDIUM
    assert SCORING_DEFAULTS['CONFIDENCE_LOW'] == CONFIDENCE_LOW
    assert SCORING_DEFAULTS['CONFIDENCE_HARNESS_ONLY'] == CONFIDENCE_HARNESS_ONLY
    assert SCORING_DEFAULTS['RETRIES_PER_LEVEL'] == RETRIES_PER_LEVEL
