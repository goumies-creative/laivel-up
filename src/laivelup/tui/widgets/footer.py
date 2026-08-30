# Copyright 2026 Romy Alula — MIT License
"""Barre de statut / raccourcis clavier."""

from __future__ import annotations

from rich.text import Text
from textual.widget import Widget


class Footer(Widget):
    """Barre de statut avec raccourcis clavier."""

    DEFAULT_CSS = """
    Footer {
        height: 1;
        width: 100%;
        background: #1a1a2e;
        color: #666688;
        content-align: center middle;
    }
    """

    def __init__(self, shortcuts: str = '', **kwargs) -> None:
        super().__init__(**kwargs)
        self._shortcuts = shortcuts

    def render(self) -> Text:
        return Text(self._shortcuts, style='#666688')
