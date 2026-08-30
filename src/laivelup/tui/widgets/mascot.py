# Copyright 2026 Romy Alula — MIT License
"""Widget mascotte — moniteur rétro-futuriste LAIVEL-UP."""

from __future__ import annotations

from rich.text import Text
from textual.reactive import reactive
from textual.widget import Widget

from laivelup.tui.mascot.renderer_rich import render_rich
from laivelup.tui.mascot.states import MascotState


class Mascot(Widget):
    """Widget affichant le moniteur LAIVEL-UP dans différents états."""

    DEFAULT_CSS = """
    Mascot {
        width: auto;
        height: auto;
        content-align: center middle;
    }
    """

    state: reactive[MascotState] = reactive(MascotState.IDLE)

    def __init__(self, state: MascotState = MascotState.IDLE, **kwargs) -> None:
        super().__init__(**kwargs)
        self.state = state

    def render(self) -> Text:
        return render_rich(self.state)
