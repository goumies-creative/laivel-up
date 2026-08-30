# Copyright 2026 Romy Alula — MIT License
"""Application Textual principale LAIVEL-UP TUI."""

from __future__ import annotations

from pathlib import Path

from textual.app import App

from laivelup.tui.screens.home import HomeScreen


class LaivelUpApp(App):
    """Application TUI 8-bit rétro terminal pour LAIVEL-UP."""

    TITLE = 'LAIVEL-UP'
    SUB_TITLE = 'AIDD Level Diagnostic Terminal'

    CSS = """
    Screen {
        background: #0f0f23;
    }
    """

    def __init__(self, profil: str | Path | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self._profil = str(profil) if profil else None

    def on_mount(self) -> None:
        self.push_screen(HomeScreen(profil_path=self._profil))
