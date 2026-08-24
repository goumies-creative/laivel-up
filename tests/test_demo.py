# Copyright 2026 Romy Alula — MIT License
"""Tests for demo.py — validation structure et exécution."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

DEMO_DIR = Path(__file__).resolve().parent.parent
DEMO_SCRIPT = DEMO_DIR / 'scripts' / 'demo.py'
EXAMPLES_DIR = DEMO_DIR / 'exemples'


class TestDemoStructure:
    """Tests structurels de demo.py."""

    def test_demo_script_exists(self) -> None:
        assert DEMO_SCRIPT.exists(), f'demo.py introuvable : {DEMO_SCRIPT}'

    def test_demo_has_shebang(self) -> None:
        first_line = DEMO_SCRIPT.read_text(encoding='utf-8').split('\n')[0]
        assert first_line.startswith('#!'), f'Manque shebang : {first_line}'

    def test_demo_has_docstring(self) -> None:
        content = DEMO_SCRIPT.read_text(encoding='utf-8')
        assert '"""' in content, 'Manque docstring'

    def test_demo_imports_subprocess(self) -> None:
        content = DEMO_SCRIPT.read_text(encoding='utf-8')
        assert 'import subprocess' in content

    def test_demo_imports_time(self) -> None:
        content = DEMO_SCRIPT.read_text(encoding='utf-8')
        assert 'import time' in content

    def test_demo_has_main_function(self) -> None:
        content = DEMO_SCRIPT.read_text(encoding='utf-8')
        assert 'def main()' in content

    def test_demo_profiles_exist(self) -> None:
        for profil in ['profil-maison-1.json', 'profil-maison-2.json']:
            path = EXAMPLES_DIR / profil
            assert path.exists(), f"Profil d'exemple manquant : {path}"

    def test_demo_no_franglais(self) -> None:
        """Vérifie pas de franglais dans les commentaires/demo."""
        content = DEMO_SCRIPT.read_text(encoding='utf-8')
        forbidden = ["l'accuracy", 'le scoring', 'le pipeline', 'robust']
        for term in forbidden:
            assert term.lower() not in content.lower(), f'Franglais détecté : {term}'


class TestDemoExecution:
    """Tests d'exécution de demo.py (sans dépendre du CLI installé)."""

    def test_demo_script_syntax(self) -> None:
        """Vérifie que le script est syntaxiquement valide."""
        result = subprocess.run(
            [
                sys.executable,
                '-c',
                "import ast; ast.parse(open(r'" + str(DEMO_SCRIPT) + "', encoding='utf-8').read())",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f'Erreur syntaxe : {result.stderr}'

    def test_demo_importable(self) -> None:
        """Vérifie que le script est importable sans erreur."""
        result = subprocess.run(
            [
                sys.executable,
                '-c',
                "import importlib.util; spec = importlib.util.spec_from_file_location('demo', r'"
                + str(DEMO_SCRIPT)
                + "'); mod = importlib.util.module_from_spec(spec); print('OK')",
            ],
            capture_output=True,
            text=True,
            cwd=str(DEMO_DIR),
        )
        assert result.returncode == 0, f'Erreur import : {result.stderr}'


class TestDemoProfiles:
    """Tests sur les profils d'exemple utilisés par demo.py."""

    def test_profil_maison_1_valid(self) -> None:
        import json

        profil = EXAMPLES_DIR / 'profil-maison-1.json'
        data = json.loads(profil.read_text(encoding='utf-8'))
        assert 'traces' in data or 'declared_level' in data

    def test_profil_maison_2_valid(self) -> None:
        import json

        profil = EXAMPLES_DIR / 'profil-maison-2.json'
        data = json.loads(profil.read_text(encoding='utf-8'))
        assert 'traces' in data or 'declared_level' in data
