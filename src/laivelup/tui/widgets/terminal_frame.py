# Copyright 2026 Romy Alula — MIT License
"""Cadre pixel-art pour les panneaux TUI."""

from __future__ import annotations

from textual.containers import Container
from textual.widget import Widget


class TerminalFrame(Container):
    """Cadre stylé terminal pour les contenus TUI.

    Utilise les bordures CSS de Textual.
    """

    DEFAULT_CSS = """
    TerminalFrame {
        border: tall #3a3a5c;
        background: #0f0f23;
        padding: 1 2;
        margin: 0 0;
    }
    """
