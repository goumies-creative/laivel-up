# Copyright 2026 Romy Alula — MIT License
"""Renderer ASCII fallback pour la mascotte."""

from __future__ import annotations

from laivelup.tui.mascot.states import EXPRESSIONS, MascotState

# Sprite ASCII compact (moniteur simplifié)
ASCII_SPRITE = [
    '  +---------+  ',
    ' /###########\\ ',
    '|#############|',
    '|##         ##|',
    '|##  O   O  ##|',
    '|##    .    ##|',
    '|##         ##|',
    '|#############|',
    ' \\###########/ ',
    '  +---------+  ',
]

# Coordonnées de la zone écran dans le sprite ASCII
ASCII_SCREEN_REGION = {
    'row_start': 3,
    'row_end': 7,
    'col_start': 2,
    'col_end': 12,
}


def render_ascii(state: MascotState) -> str:
    """Render le moniteur en ASCII simple.

    Args:
        state: état de la mascotte

    Returns:
        Sprite ASCII multi-ligne
    """
    eye_left, eye_right, symbol = EXPRESSIONS[state]

    # Mapping des yeux pour ASCII
    ascii_eyes = {
        '\u25a0': 'O',  # ■ → O
        '\u2500': '-',  # — → -
        '\u25d6': 'o',  # ◖ → o
        '\u25d7': 'o',  # ◗ → o
        '\u2726': '*',  # ✦ → *
        '\u2713': 'V',  # ✓ → V
        '\u2717': 'X',  # ✗ → X
        '!': '!',
        '?': '?',
    }

    e_l = ascii_eyes.get(eye_left, 'O')
    e_r = ascii_eyes.get(eye_right, 'O')
    sym = ascii_eyes.get(symbol, '.')

    result = []
    for row in ASCII_SPRITE:
        result.append(row)

    # Injecter les yeux et symbole
    rows = list(result)
    screen = ASCII_SCREEN_REGION
    mid = (screen['row_end'] - screen['row_start']) // 2

    if len(rows) > screen['row_start'] + mid - 1:
        eye_row = list(rows[screen['row_start'] + mid - 1])
        eye_col_l = screen['col_start'] + 3
        eye_col_r = screen['col_start'] + 7
        if eye_col_l < len(eye_row):
            eye_row[eye_col_l] = e_l
        if eye_col_r < len(eye_row):
            eye_row[eye_col_r] = e_r
        rows[screen['row_start'] + mid - 1] = ''.join(eye_row)

    if len(rows) > screen['row_start'] + mid + 1:
        sym_row = list(rows[screen['row_start'] + mid + 1])
        sym_col = screen['col_start'] + 5
        if sym_col < len(sym_row):
            sym_row[sym_col] = sym
        rows[screen['row_start'] + mid + 1] = ''.join(sym_row)

    return '\n'.join(rows)
