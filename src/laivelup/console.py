# Copyright 2026 Romy Alula — MIT License
"""Console Rich partagée (cli.py, team_cli.py, etc.)."""

from __future__ import annotations

import os
import sys

from rich.console import Console

NO_COLOR = os.environ.get('NO_COLOR') is not None
TTY = sys.stdout.isatty()


def make_console(no_color: bool | None = None) -> Console:
    """Crée une console Rich avec détection TTY et encoding cross-platform."""
    from .encoding import ensure_utf8_env

    ensure_utf8_env()
    return Console(
        no_color=no_color if no_color is not None else NO_COLOR,
        force_terminal=TTY,
    )


console = make_console()
error_console = Console(stderr=True, no_color=NO_COLOR)
