# Copyright 2026 Romy Alula — MIT License
"""États de la mascotte moniteur."""

from __future__ import annotations

from enum import Enum


class MascotState(Enum):
    """6 états du moniteur LAIVEL-UP.

    L'état est communiqué par :
    1. expression des yeux
    2. symbole central éventuel
    3. couleur de l'écran
    """

    IDLE = 'IDLE'
    ANALYZING = 'ANALYZING'
    QUESTIONING = 'QUESTIONING'
    SUCCESS = 'SUCCESS'
    WARNING = 'WARNING'
    ERROR = 'ERROR'


# Mapping état → (yeux_gauche, yeux_droit, symbole_central)
EXPRESSIONS: dict[MascotState, tuple[str, str, str]] = {
    MascotState.IDLE: ('\u25a0', '\u25a0', ''),  # ■ ■
    MascotState.ANALYZING: ('\u2500', '\u2500', '\u00b7'),  # — — ·
    MascotState.QUESTIONING: ('\u25d6', '\u25d7', '?'),  # ◖ ◗ ?
    MascotState.SUCCESS: ('\u2726', '\u2726', '\u2713'),  # ✦ ✦ ✓
    MascotState.WARNING: ('!', '!', '!'),  # ! ! !
    MascotState.ERROR: ('\u2717', '\u2717', '\u2717'),  # ✗ ✗ ✗
}
