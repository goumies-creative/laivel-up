# Copyright 2026 Romy Alula — MIT License
"""Renderer Rich (Unicode blocs + couleurs 24-bit) pour la mascotte."""

from __future__ import annotations

from rich.text import Text

from laivelup.tui.mascot.sprite import SCREEN_REGION_COMPACT, SPRITE_COMPACT
from laivelup.tui.mascot.states import EXPRESSIONS, MascotState
from laivelup.tui.theme import (
    MONITOR_BODY,
    MONITOR_SCREEN_OFF,
    SCREEN_STATE_COLORS,
)


def render_rich(state: MascotState) -> Text:
    """Render le moniteur en Unicode avec couleurs Rich.

    Args:
        state: état de la mascotte (IDLE, ANALYZING, etc.)

    Returns:
        Text Rich rendu avec couleurs 24-bit
    """
    sprite = SPRITE_COMPACT  # TODO: standard when needed
    region = SCREEN_REGION_COMPACT
    screen_color = SCREEN_STATE_COLORS.get(state.value, MONITOR_SCREEN_OFF)
    eye_left, eye_right, symbol = EXPRESSIONS[state]

    result = Text()

    for row_idx, row in enumerate(sprite):
        if row_idx > 0:
            result.append('\n')

        in_screen = region['row_start'] <= row_idx < region['row_end']

        if in_screen:
            screen_row = row_idx - region['row_start']
            # Injecter les yeux et symbole dans la zone écran
            rendered_row = _inject_expression(row, screen_row, eye_left, eye_right, symbol, region)
            for ch in rendered_row:
                if ch == ' ':
                    result.append(ch, style=f'on {screen_color}')
                elif ch in (eye_left, eye_right, symbol) and ch:
                    result.append(ch, style=f'bold white on {screen_color}')
                else:
                    result.append(ch, style=f'on {MONITOR_BODY}')
        else:
            for ch in row:
                if ch == ' ':
                    result.append(' ')
                else:
                    result.append(ch, style=f'on {MONITOR_BODY}')

    return result


def _inject_expression(
    row: str,
    screen_row: int,
    eye_left: str,
    eye_right: str,
    symbol: str,
    region: dict,
) -> str:
    """Injecte les yeux et symbole dans la ligne de la zone écran."""
    cols = list(row)
    screen_width = region['col_end'] - region['col_start']

    # Ligne des yeux (milieu de la zone écran)
    mid_row = (region['row_end'] - region['row_start']) // 2
    if screen_row == mid_row - 1:
        # Placer les yeux
        eye_col_l = region['col_start'] + screen_width // 3
        eye_col_r = region['col_start'] + (2 * screen_width) // 3
        if 0 <= eye_col_l < len(cols):
            cols[eye_col_l] = eye_left
        if 0 <= eye_col_r < len(cols):
            cols[eye_col_r] = eye_right
    elif screen_row == mid_row + 1 and symbol:
        # Placer le symbole central
        sym_col = region['col_start'] + screen_width // 2
        if 0 <= sym_col < len(cols):
            cols[sym_col] = symbol

    return ''.join(cols)
