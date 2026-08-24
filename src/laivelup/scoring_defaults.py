# Copyright 2026 Romy Alula — MIT License
"""Constantes de scoring modifiables par les scripts Plan B.

Extraction des seuils hardcoded de scoring.py en dict structuré.
Les scripts calibrate_degraded.py et apply_calibration_fix.py
lisent/modifient SCORING_DEFAULTS pour adapter les seuils.
"""

from __future__ import annotations

from .model import Level

SCORING_DEFAULTS: dict[str, object] = {
    'CONFIDENCE_THRESHOLD': 0.5,
    'CONFIDENCE_PEAK': 0.9,
    'CONFIDENCE_MEDIUM': 0.8,
    'CONFIDENCE_LOW': 0.4,
    'CONFIDENCE_HARNESS_ONLY': 0.7,
    'RETRIES_PER_LEVEL': {'gold': 0.05, 'copper_or_green': 0.2, 'blue': 0.5},
    'SIZE_LEVEL': {
        'S': Level.RED,
        'M': Level.BLUE,
        'L': Level.GOLD,
        'XL': Level.GOLD,
    },
}
