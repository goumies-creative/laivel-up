"""Tests skeleton pour install clean (venv vierge)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.install
class TestInstallClean:
    """Tests for clean installation in a fresh venv."""

    @pytest.mark.slow
    def test_pip_install(self) -> None:
        """pip install . works without errors."""
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '.'],
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert result.returncode == 0, f'pip install failed: {result.stderr}'

    def test_cli_help(self) -> None:
        """laivelup --help works after install."""
        result = subprocess.run(
            ['laivelup', '--help'],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f'laivelup --help failed: {result.stderr}'

    def test_cli_version(self) -> None:
        """laivelup --version or laivelup evaluate --help works."""
        result = subprocess.run(
            ['laivelup', 'evaluate', '--help'],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f'laivelup evaluate --help failed: {result.stderr}'
