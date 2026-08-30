# Copyright 2026 Romy Alula — MIT License
"""Sprite data pour le moniteur LAIVEL-UP.

Deux résolutions : compact (16x11) et standard (24x16).
La silhouette est un moniteur plein, légèrement asymétrique.
L'écran est une zone négative découpée dans la masse.
"""

from __future__ import annotations

# ─── Sprite compact 16x11 ─────────────────────────────────────
# Le moniteur est un bloc plein avec une zone écran négative.
# Les yeux et symboles sont rendus dans la zone écran par les renderers.

SPRITE_COMPACT = [
    '   ▄██████▄   ',
    '  ██████████  ',
    ' ████████████ ',
    '████        ██',
    '███   ..   ███',
    '███   ..   ███',
    '███        ███',
    '████        ██',
    ' ████████████ ',
    '  ██████████  ',
    '   ▀██████▀   ',
]

# ─── Sprite standard 24x16 ────────────────────────────────────
SPRITE_STANDARD = [
    '      ▄██████████▄      ',
    '    ▄███████████████▄    ',
    '   ███████████████████   ',
    '  █████████████████████  ',
    ' ██████          ██████ ',
    '██████            ██████',
    '██████   ..  ..   ██████',
    '██████            ██████',
    '██████            ██████',
    ' ██████          ██████ ',
    '  █████████████████████  ',
    '   ███████████████████   ',
    '    ▀███████████████▀    ',
    '      ▀██████████▀      ',
]

# Coordonnées de la zone écran dans le sprite compact
SCREEN_REGION_COMPACT = {
    'row_start': 3,
    'row_end': 7,
    'col_start': 4,
    'col_end': 12,
}

# Coordonnées de la zone écran dans le sprite standard
SCREEN_REGION_STANDARD = {
    'row_start': 5,
    'row_end': 9,
    'col_start': 6,
    'col_end': 18,
}
