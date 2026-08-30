# Copyright 2026 Romy Alula — MIT License
"""Fallback ASCII pour terminaux sans Unicode."""

from __future__ import annotations

_UNICODE_TO_ASCII: dict[str, str] = {
    '\u2588': '#',  # █
    '\u2580': '#',  # ▀
    '\u2584': '#',  # ▄
    '\u2592': '#',  # ▒
    '\u2591': '-',  # ░
    '\u25c6': '*',  # ◆
    '\u25cf': 'O',  # ●
    '\u25ba': '>',  # ►
    '\u25b6': '>',  # ▶
    '\u2713': 'OK',  # ✓
    '\u2717': 'X',  # ✗
    '\u2726': '*',  # ✦
    '\u2500': '-',  # ─
    '\u2502': '|',  # │
    '\u250c': '+',  # ┌
    '\u2510': '+',  # ┐
    '\u2514': '+',  # └
    '\u2518': '+',  # ┘
    '\u251c': '+',  # ├
    '\u2524': '+',  # ┤
    '\u252c': '+',  # ┬
    '\u2534': '+',  # ┴
    '\u253c': '+',  # ┼
    '\u2550': '=',  # ═
    '\u2551': '|',  # ║
    '\u2554': '+',  # ╔
    '\u2557': '+',  # ╗
    '\u255a': '+',  # ╚
    '\u255d': '+',  # ╝
    '\u2560': '+',  # ╠
    '\u2563': '+',  # ╣
    '\u2566': '+',  # ╦
    '\u2569': '+',  # ╩
    '\u256c': '+',  # ╬
    '\u2026': '...',  # …
    '\u2014': '-',  # —
    '\u00b7': '.',  # ·
    '\u2022': '*',  # •
    '\u25cb': ' ',  # ○
}


def to_ascii(text: str) -> str:
    """Remplace les caractères Unicode par des équivalents ASCII."""
    result = text
    for char, repl in _UNICODE_TO_ASCII.items():
        result = result.replace(char, repl)
    return result


def supports_unicode() -> bool:
    """Détection rapide de support Unicode dans le terminal."""
    import os
    import sys

    if os.environ.get('PYTHONIOENCODING', '').lower().replace('-', '') == 'utf8':
        return True
    if sys.platform != 'win32':
        return True
    enc = getattr(sys.stdout, 'encoding', '') or ''
    return 'utf' in enc.lower()
