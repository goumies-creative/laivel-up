# Copyright 2026 Romy Alula — MIT License
"""Écran next steps — recommandations du moteur."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Label

from laivelup.tui.widgets.footer import Footer


class NextStepsScreen(Screen):
    """Affichage des prochaines actions / questions."""

    CSS = """
    NextStepsScreen {
        layout: vertical;
        padding: 1 2;
    }
    #title {
        color: #00aaff;
        text-style: bold;
        margin-bottom: 1;
    }
    .step {
        color: #00aaff;
        margin: 0 0;
    }
    #footer {
        dock: bottom;
    }
    """

    BINDINGS = [
        Binding('escape', 'back', 'Back'),
    ]

    def __init__(self, next_steps: list[str], **kwargs) -> None:
        super().__init__(**kwargs)
        self._steps = next_steps

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label('COMMENT PROGRESSER', id='title')
            for step in self._steps:
                yield Label(f'  \u2192 {step}', classes='step')
            yield Footer('ESC RETOUR', id='footer')

    def action_back(self) -> None:
        self.app.pop_screen()
