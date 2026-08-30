# Copyright 2026 Romy Alula — MIT License
"""Barre de titre pour les écrans TUI."""

from __future__ import annotations

from rich.text import Text
from textual.widget import Widget


class Header(Widget):
    """Barre de titre avec nom de l'écran."""

    DEFAULT_CSS = """
    Header {
        height: 1;
        width: 100%;
        background: #1a1a2e;
        color: #e0e0e0;
        content-align: center middle;
        text-style: bold;
    }
    """

    def __init__(self, title: str = '', **kwargs) -> None:
        super().__init__(**kwargs)
        self._title = title

    def render(self) -> Text:
        return Text(self._title, style='bold #e0e0e0')
