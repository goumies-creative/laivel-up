"""Tests skeleton pour install clean (venv vierge).

Utilise un helper subprocess avec PYTHONIOENCODING=utf-8 pour éviter
les problèmes d'encodage cp1252 sur Windows lors de la lecture des
sorties Rich (emojis, caractères Unicode).
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent


def _run_cli(
    *args: str,
    timeout: int = 120,
    check: bool = False,
) -> subprocess.CompletedProcess[str]:
    """Wrapper subprocess avec UTF-8 forcé pour Windows."""
    env = {**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1'}
    result = subprocess.run(
        list(args),
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        env=env,
        timeout=timeout,
    )
    if check:
        assert result.returncode == 0, (
            f'Command failed: {" ".join(args)}\nstdout: {result.stdout}\nstderr: {result.stderr}'
        )
    return result


@pytest.mark.install
class TestInstallClean:
    """Tests for clean installation in a fresh venv."""

    def test_cli_help(self) -> None:
        """laivelup --help works after install."""
        result = _run_cli('laivelup', '--help', timeout=30)
        assert result.returncode == 0, f'laivelup --help failed: {result.stderr}'

    def test_cli_version(self) -> None:
        """laivelup evaluate --help works."""
        result = _run_cli('laivelup', 'evaluate', '--help', timeout=30)
        assert result.returncode == 0, f'laivelup evaluate --help failed: {result.stderr}'

    @pytest.mark.slow
    def test_cli_evaluate_real(self) -> None:
        """laivelup evaluate runs a real profile end-to-end after install."""
        profil = REPO / 'exemples' / 'profil-maison-1.json'
        if not profil.exists():
            pytest.skip('profil-maison-1.json not found')
        out_dir = REPO / 'rapports'
        result = _run_cli(
            'laivelup',
            'evaluate',
            str(profil),
            '--out',
            str(out_dir),
            '--no-html',
            timeout=60,
        )
        assert result.returncode == 0, f'laivelup evaluate failed: {result.stderr}'
        # Non-TTY (subprocess) => JSON par design ; TTY => verdict texte
        assert (
            'Niveau' in result.stdout
            or 'Refus' in result.stdout
            or 'refus' in result.stdout
            or '"level"' in result.stdout
        )
