# Copyright 2026 Romy Alula — MIT License
"""Mascotte LAIVEL-UP — Moniteur rétro-futuriste 8-bit.

Le moniteur EST le personnage. Son écran constitue son visage.
Pas de corps, bras, jambes, antenne, élément humanoid.
"""

from __future__ import annotations

from laivelup.tui.mascot.renderer_ascii import render_ascii
from laivelup.tui.mascot.renderer_rich import render_rich
from laivelup.tui.mascot.sprite import SPRITE_COMPACT, SPRITE_STANDARD
from laivelup.tui.mascot.states import MascotState

__all__ = [
    'SPRITE_COMPACT',
    'SPRITE_STANDARD',
    'MascotState',
    'render_ascii',
    'render_rich',
]
