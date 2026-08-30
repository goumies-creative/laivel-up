# Copyright 2026 Romy Alula — MIT License
"""Détection taille terminal et breakpoints responsive."""

from __future__ import annotations

import shutil


def terminal_size() -> tuple[int, int]:
    """Retourne (colonnes, lignes) du terminal."""
    size = shutil.get_terminal_size()
    return size.columns, size.lines


def width_class(cols: int | None = None) -> str:
    """Classe de largeur : 'compact', 'standard', 'wide'.

    - compact  : < 80 colonnes
    - standard : 80-119 colonnes
    - wide     : >= 120 colonnes
    """
    if cols is None:
        cols, _ = terminal_size()
    if cols < 80:
        return 'compact'
    if cols < 120:
        return 'standard'
    return 'wide'


def should_show_sidebar(cols: int | None = None) -> bool:
    """Afficher la barre latérale en standard+."""
    return width_class(cols) != 'compact'


def should_show_details(cols: int | None = None) -> bool:
    """Afficher les détails en wide uniquement."""
    return width_class(cols) == 'wide'


def max_label_width(cols: int | None = None) -> int:
    """Largeur maximale des labels selon la classe."""
    cls = width_class(cols)
    if cls == 'compact':
        return 12
    if cls == 'standard':
        return 18
    return 24
