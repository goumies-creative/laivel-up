# Copyright 2026 Romy Alula — MIT License
"""Fixtures partagées pour les tests."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _isolate_team_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Isole le répertoire .laivelup/teams/ dans tmp_path pour chaque test."""
    from laivelup import team
    monkeypatch.setattr(team, "_DEFAULT_TEAM_DIR", tmp_path / ".laivelup" / "teams")
