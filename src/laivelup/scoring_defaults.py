# Copyright 2026 Romy Alula — MIT License
"""Constantes de scoring modifiables par les scripts Plan B.

Extraction des seuils hardcoded de scoring.py en dict structuré.
Les scripts calibrate_degraded.py et apply_calibration_fix.py
lisent/modifient SCORING_DEFAULTS pour adapter les seuils.

La partie `GRID` est dérivée de `grille/aidd.md`, la seule source de la grille :
elle n'est pas écrite ici, elle est lue au chargement. Le contrôle final refuse
un `SIZE_LEVEL` qui accorderait à une taille un niveau inférieur à celui où la
grille introduit cette taille.
"""

from __future__ import annotations

import re

from .grid_doc import GridError
from .model import GRID, Level

# Exigence de la grille, par niveau et par axe. Ordinal : plus haut = plus exigeant.
GRID_DEMAND: dict[str, dict[str, int]] = {
    level.id: {axis: GRID.demand(level.id, axis) for axis in GRID.axis_ids} for level in GRID.levels
}

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


# Première taille de PR citée par la grille, et le niveau où elle apparaît.
def _first_level_mentioning(size: str) -> Level | None:
    pattern = re.compile(rf'(?<![A-Z]){re.escape(size)}(?![A-Z])')
    for level in GRID.levels:
        if pattern.search(GRID.cells[level.id]['size']):
            return Level[level.id.upper()]
    return None


def _check_size_levels() -> None:
    size_level = SCORING_DEFAULTS['SIZE_LEVEL']
    assert isinstance(size_level, dict)
    for size, authorized in size_level.items():
        introduced_at = _first_level_mentioning(size)
        if introduced_at is None:
            raise GridError(f'{GRID.path} : la grille ne mentionne aucune taille de PR « {size} »')
        if authorized < introduced_at:
            raise GridError(
                f'{GRID.path} : SIZE_LEVEL accorde {size} le niveau {authorized.name}, '
                f'moins haut que {introduced_at.name} où la grille introduit cette taille'
            )


_check_size_levels()
