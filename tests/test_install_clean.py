"""Tests skeleton pour install clean (venv vierge).

Windows: Rich console writes emojis via legacy_windows_render which encodes
using the system codepage (cp1252). capture_output pipes use cp1252 on read,
causing UnicodeDecodeError when Rich outputs emoji characters (🔹 etc).
These tests are therefore skipped on Windows in pre-commit.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
IS_WINDOWS = sys.platform == 'win32'


@pytest.mark.install
@pytest.mark.skipif(
    IS_WINDOWS, reason='Rich emoji output incompatible with cp1252 capture on Windows'
)
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
            encoding='utf-8',
            timeout=30,
        )
        assert result.returncode == 0, f'laivelup --help failed: {result.stderr}'

    def test_cli_version(self) -> None:
        """laivelup --version or laivelup evaluate --help works."""
        result = subprocess.run(
            ['laivelup', 'evaluate', '--help'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=30,
        )
        assert result.returncode == 0, f'laivelup evaluate --help failed: {result.stderr}'

    @pytest.mark.slow
    def test_cli_evaluate_real(self) -> None:
        """laivelup evaluate runs a real profile end-to-end after install."""
        profil = REPO / 'exemples' / 'profil-maison-1.json'
        if not profil.exists():
            pytest.skip('profil-maison-1.json not found')
        out_dir = REPO / 'rapports'
        result = subprocess.run(
            ['laivelup', 'evaluate', str(profil), '--out', str(out_dir), '--no-html'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=60,
        )
        assert result.returncode == 0, f'laivelup evaluate failed: {result.stderr}'
        assert 'Niveau' in result.stdout or 'Refus' in result.stdout or 'refus' in result.stdout
