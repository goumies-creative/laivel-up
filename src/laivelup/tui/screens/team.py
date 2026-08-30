# Copyright 2026 Romy Alula — MIT License
"""Écran team — team tracker."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Label

from laivelup.tui.widgets.footer import Footer


class TeamScreen(Screen):
    """Team tracker — CRUD, export, RGPD."""

    CSS = """
    TeamScreen {
        layout: vertical;
        padding: 1 2;
    }
    #title {
        color: #00aaff;
        text-style: bold;
        margin-bottom: 1;
    }
    .menu-item {
        color: #e0e0e0;
        margin: 0 0;
        padding: 0 2;
    }
    .menu-item-active {
        color: #00aaff;
        text-style: bold;
    }
    #footer {
        dock: bottom;
    }
    """

    BINDINGS = [
        Binding('escape', 'back', 'Back'),
    ]

    MENU = [
        'CR\u00c9ER UNE \u00c9QUIPE',
        '\u00c9VALUER UN MEMBRE',
        'VOIR LES MEMBRES',
        'EXPORTER',
        'OPT-OUT RGPD',
        'SUPPRIMER',
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._selected = 0

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label('TEAM TRACKER', id='title')
            for i, item in enumerate(self.MENU):
                cls = 'menu-item-active' if i == self._selected else 'menu-item'
                marker = '\u25ba ' if i == self._selected else '  '
                yield Label(f'{marker}{item}', classes=cls, id=f'team-{i}')
            yield Footer('\u2191\u2193 NAVIGUER   ESC RETOUR', id='footer')

    def action_back(self) -> None:
        self.app.pop_screen()
