# Copyright 2026 Romy Alula — MIT License
"""Écran red flags — liste des alertes."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Label

from laivelup.model import RedFlag
from laivelup.tui.widgets.footer import Footer


class RedFlagsScreen(Screen):
    """Affichage des red flags avec sévérité visuelle."""

    CSS = """
    RedFlagsScreen {
        layout: vertical;
        padding: 1 2;
    }
    #title {
        color: #cc3333;
        text-style: bold;
        margin-bottom: 1;
    }
    .flag {
        border: tall #cc3333;
        padding: 1;
        margin: 0 0 1 0;
    }
    .flag-title {
        color: #cc3333;
        text-style: bold;
    }
    .flag-constat {
        color: #e0e0e0;
    }
    .flag-source {
        color: #666688;
    }
    .flag-question {
        color: #00aaff;
    }
    #footer {
        dock: bottom;
    }
    """

    BINDINGS = [
        Binding('escape', 'back', 'Back'),
    ]

    def __init__(self, red_flags: list[RedFlag], **kwargs) -> None:
        super().__init__(**kwargs)
        self._flags = red_flags

    def compose(self) -> ComposeResult:
        with Vertical():
            severity_labels = {1: '\u26a0', 2: '\u26a0\u26a0', 3: '\u26a0\u26a0\u26a0'}
            yield Label(f'RED FLAGS ({len(self._flags)})', id='title')

            for _i, flag in enumerate(self._flags):
                sev = severity_labels.get(flag.severite, '\u26a0')
                with Vertical(classes='flag'):
                    yield Label(f'[{sev}] {flag.titre}', classes='flag-title')
                    yield Label(f'Constat : {flag.constat}', classes='flag-constat')
                    yield Label(f'Source : {flag.source}', classes='flag-source')
                    if flag.question:
                        yield Label(f'\u2192 {flag.question}', classes='flag-question')

            yield Footer('ESC RETOUR', id='footer')

    def action_back(self) -> None:
        self.app.pop_screen()
