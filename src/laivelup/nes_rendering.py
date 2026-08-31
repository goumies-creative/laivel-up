# Copyright 2026 Romy Alula — MIT License
"""Rendu NES 8-bit : boîtes ASCII, barres de progression et de niveau."""

from __future__ import annotations

from .console import console
from .model import Level

BOX_TL = '+'
BOX_TR = '+'
BOX_BL = '+'
BOX_BR = '+'
BOX_H = '-'
BOX_V = '|'
PIXEL_H = '\u2580'  # ▀ upper half block
PIXEL_F = '\u2588'  # █ full block
PIXEL_D = '\u2591'  # ░ light shade

LEVEL_RICH_COLORS: dict[Level, str] = {
    Level.WHITE: 'dim',
    Level.RED: 'red',
    Level.BLUE: 'blue',
    Level.GREEN: 'green',
    Level.COPPER: 'yellow',
    Level.SILVER: 'bright_white',
    Level.GOLD: 'bright_yellow',
}


def _nes_box(lines: list[str], color: str = 'cyan', width: int = 40) -> None:
    """Affiche un cadre NES-style en ASCII art."""
    border = BOX_H * (width - 2)
    open_tag = f'[bold {color}]'
    close_tag = '[/' + f'bold {color}]'
    console.print(open_tag + BOX_TL + border + BOX_TR + close_tag)
    for line in lines:
        padded = line.ljust(width - 4)
        console.print(
            open_tag + BOX_V + close_tag + ' ' + padded + ' ' + open_tag + BOX_V + close_tag
        )
    console.print(open_tag + BOX_BL + border + BOX_BR + close_tag)


def _nes_progress_bar(current: int, total: int, width: int = 20, color: str = 'green') -> str:
    """Barre de progression NES en blocs pixel."""
    filled = int((current / total) * width) if total > 0 else 0
    empty = width - filled
    return f'[{color}]{PIXEL_F * filled}[/{color}][dim]{PIXEL_D * empty}[/dim]'


def _nes_level_bar(level: Level | None, max_level: Level = Level.GOLD) -> str:
    """Barre de niveau pixel pour un axe."""
    if level is None:
        return f'[dim]{PIXEL_D * 7}[/dim]'
    filled = level.value + 1
    empty = max_level.value + 1 - filled
    c = LEVEL_RICH_COLORS.get(level, 'dim')
    return f'[{c}]{PIXEL_F * filled}[/{c}][dim]{PIXEL_D * empty}[/dim]'
