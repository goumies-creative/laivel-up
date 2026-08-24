# Copyright 2026 Romy Alula — MIT License
"""Tests du script de calibration (scripts/calibrate.py).

Couvre : chargement profils/expected, generation template, diff par axe,
suggestions de fix, calibration complete (OK/FAIL/SKIP/UNDECIDED).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import sys

SCRIPTS_DIR = Path(__file__).parent.parent / 'scripts'
sys.path.insert(0, str(SCRIPTS_DIR))

from calibrate import (  # noqa: E402
    _axis_diff,
    _fix_suggestion,
    _load_expected,
    _load_profile,
    calibrate,
    generate_template,
)

REPO = Path(__file__).parent.parent
PROFILES_DIR = REPO / 'grille' / 'profils-officiels'


# --- Helpers ---


def _write_json(path: Path, data: dict) -> Path:
    path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
    return path


def _profile_json(tmp_path: Path, name: str, traces: dict, declared: str | None = None) -> Path:
    data = {'name': name, 'traces': traces}
    if declared:
        data['declared_level'] = declared
    return _write_json(tmp_path / f'{name}.json', data)


def _expected_json(tmp_path: Path, levels: dict) -> Path:
    return _write_json(tmp_path / 'expected.json', {'levels': levels})


# Traces completes pour un profil BLUE (tous les axes decident)
_BLUE_TRACES = {
    'pr_sizes': ['M', 'M'],
    'context_versioned': True,
    'retries_after_fact': 0.4,
    'retries_triangulated': True,
    'parallel_projects': 1,
}

# Traces completes pour un profil RED
_RED_TRACES = {
    'pr_sizes': ['S'],
    'prompts': True,
    'retries_after_fact': 0.8,
    'retries_triangulated': True,
    'parallel_projects': 1,
}


# --- _load_profile ---


class TestLoadProfile:
    def test_chargement_minimal(self, tmp_path):
        p = _profile_json(tmp_path, 'alice', {'pr_sizes': ['M', 'M', 'S']})
        profile = _load_profile(p)
        assert profile.name == 'alice'
        assert profile.declared_level is None
        assert profile.traces['pr_sizes'] == ['M', 'M', 'S']

    def test_declared_level_upper(self, tmp_path):
        p = _profile_json(tmp_path, 'bob', {}, declared='blue')
        profile = _load_profile(p)
        assert profile.declared_level.name == 'BLUE'

    def test_declared_level_none_si_absent(self, tmp_path):
        p = _profile_json(tmp_path, 'charlie', {})
        profile = _load_profile(p)
        assert profile.declared_level is None

    def test_name_fallback_sur_stem(self, tmp_path):
        p = _write_json(tmp_path / 'custom-name.json', {'traces': {}})
        profile = _load_profile(p)
        assert profile.name == 'custom-name'

    def test_traces_vides_par_defaut(self, tmp_path):
        p = _write_json(tmp_path / 'empty.json', {'name': 'empty'})
        profile = _load_profile(p)
        assert profile.traces == {}
        assert profile.answers == {}
        assert profile.meta == {}


# --- _load_expected ---


class TestLoadExpected:
    def test_charge_fichier_existant(self, tmp_path):
        p = _expected_json(tmp_path, {'alice': 'RED', 'bob': 'BLUE'})
        result = _load_expected(p)
        assert result == {'alice': 'RED', 'bob': 'BLUE'}

    def test_uppercase_automatique(self, tmp_path):
        p = _expected_json(tmp_path, {'alice': 'red'})
        result = _load_expected(p)
        assert result == {'alice': 'RED'}

    def test_fichier_inexistant_retourne_dict_vide(self, tmp_path):
        result = _load_expected(tmp_path / 'nonexistent.json')
        assert result == {}

    def test_levels_vide_retourne_dict_vide(self, tmp_path):
        p = _write_json(tmp_path / 'empty.json', {'levels': {}})
        result = _load_expected(p)
        assert result == {}


# --- generate_template ---


class TestGenerateTemplate:
    def test_genere_template_avec_profils(self, tmp_path, monkeypatch):
        profiles_dir = tmp_path / 'profils'
        profiles_dir.mkdir()
        _profile_json(profiles_dir, 'p1', {'pr_sizes': ['M', 'M']})
        _profile_json(profiles_dir, 'p2', {'pr_sizes': ['S']})

        monkeypatch.setattr('calibrate.PROFILES_DIR', profiles_dir)
        generate_template()

        template_path = profiles_dir / 'expected.json.template'
        assert template_path.exists()
        data = json.loads(template_path.read_text(encoding='utf-8'))
        assert 'levels' in data
        assert 'p1' in data['levels']
        assert 'p2' in data['levels']

    def test_sans_profils_affiche_message(self, tmp_path, monkeypatch, capsys):
        empty_dir = tmp_path / 'empty'
        empty_dir.mkdir()
        monkeypatch.setattr('calibrate.PROFILES_DIR', empty_dir)
        generate_template()
        captured = capsys.readouterr()
        assert 'Aucun profil' in captured.out


# --- _axis_diff ---


class TestAxisDiff:
    def test_identique(self):
        from laivelup.model import Level

        assert _axis_diff(Level.RED, 'RED') == 'OK'

    def test_trop_haut(self):
        from laivelup.model import Level

        result = _axis_diff(Level.GREEN, 'RED')
        assert 'trop haut' in result
        assert '-2 crans' in result

    def test_trop_bas(self):
        from laivelup.model import Level

        result = _axis_diff(Level.RED, 'GREEN')
        assert 'trop bas' in result
        assert '+2 crans' in result

    def test_undecided(self):
        assert _axis_diff(None, 'RED') == 'verdict = UNDECIDED'


# --- _fix_suggestion ---


class TestFixSuggestion:
    def test_undecided_suggere_ajout_traces(self):
        result = _fix_suggestion('alice', None, 'RED', [])
        assert 'alice' in result
        assert 'insuffisantes' in result

    def test_niveau_trop_bas_identifie_axe_plancher(self):
        from laivelup.model import AxisScore, Level

        axes = [
            AxisScore(axe='size', level=Level.RED, confidence=0.9),
            AxisScore(axe='harness', level=Level.BLUE, confidence=0.8),
        ]
        result = _fix_suggestion('bob', Level.RED, 'BLUE', axes)
        assert 'bob' in result
        assert 'Taille' in result
        assert 'Red' in result

    def test_niveau_ok_retourne_verifier_traces(self):
        from laivelup.model import AxisScore, Level

        axes = [AxisScore(axe='size', level=Level.RED, confidence=0.9)]
        result = _fix_suggestion('charlie', Level.RED, 'RED', axes)
        assert 'verifier' in result


# --- calibrate ---


class TestCalibrate:
    def test_0_erreurs_si_tout_correspond(self, tmp_path, monkeypatch):
        profiles_dir = tmp_path / 'profils'
        profiles_dir.mkdir()
        _profile_json(profiles_dir, 'p1', _BLUE_TRACES)
        _expected_json(tmp_path, {'p1': 'BLUE'})

        monkeypatch.setattr('calibrate.PROFILES_DIR', profiles_dir)
        errors = calibrate(tmp_path / 'expected.json')
        assert errors == 0

    def test_1_erreur_si_niveau_faux(self, tmp_path, monkeypatch):
        profiles_dir = tmp_path / 'profils'
        profiles_dir.mkdir()
        _profile_json(profiles_dir, 'p1', _RED_TRACES)
        _expected_json(tmp_path, {'p1': 'BLUE'})

        monkeypatch.setattr('calibrate.PROFILES_DIR', profiles_dir)
        errors = calibrate(tmp_path / 'expected.json')
        assert errors == 1

    def test_skip_si_profil_non_dans_expected(self, tmp_path, monkeypatch):
        profiles_dir = tmp_path / 'profils'
        profiles_dir.mkdir()
        _profile_json(profiles_dir, 'p1', _BLUE_TRACES)
        _profile_json(profiles_dir, 'p2', _RED_TRACES)
        _expected_json(tmp_path, {'p1': 'BLUE'})

        monkeypatch.setattr('calibrate.PROFILES_DIR', profiles_dir)
        errors = calibrate(tmp_path / 'expected.json')
        assert errors == 0

    def test_undecided_attendu_et_obtenu(self, tmp_path, monkeypatch):
        profiles_dir = tmp_path / 'profils'
        profiles_dir.mkdir()
        _profile_json(profiles_dir, 'p1', {})
        _expected_json(tmp_path, {'p1': 'UNDECIDED'})

        monkeypatch.setattr('calibrate.PROFILES_DIR', profiles_dir)
        errors = calibrate(tmp_path / 'expected.json')
        assert errors == 0

    def test_undecided_attendu_mais_decided(self, tmp_path, monkeypatch):
        profiles_dir = tmp_path / 'profils'
        profiles_dir.mkdir()
        _profile_json(profiles_dir, 'p1', _BLUE_TRACES)
        _expected_json(tmp_path, {'p1': 'UNDECIDED'})

        monkeypatch.setattr('calibrate.PROFILES_DIR', profiles_dir)
        errors = calibrate(tmp_path / 'expected.json')
        assert errors == 1

    def test_expected_vide_retourne_0(self, tmp_path, monkeypatch):
        profiles_dir = tmp_path / 'profils'
        profiles_dir.mkdir()
        _profile_json(profiles_dir, 'p1', _BLUE_TRACES)

        monkeypatch.setattr('calibrate.PROFILES_DIR', profiles_dir)
        errors = calibrate(tmp_path / 'expected.json')
        assert errors == 0

    def test_diff_affiche_axes(self, tmp_path, monkeypatch, capsys):
        profiles_dir = tmp_path / 'profils'
        profiles_dir.mkdir()
        _profile_json(profiles_dir, 'p1', _BLUE_TRACES)
        _expected_json(tmp_path, {'p1': 'BLUE'})

        monkeypatch.setattr('calibrate.PROFILES_DIR', profiles_dir)
        calibrate(tmp_path / 'expected.json', diff=True)
        captured = capsys.readouterr()
        assert 'Taille' in captured.out

    def test_fix_affiche_suggestions(self, tmp_path, monkeypatch, capsys):
        profiles_dir = tmp_path / 'profils'
        profiles_dir.mkdir()
        _profile_json(profiles_dir, 'p1', _RED_TRACES)
        _expected_json(tmp_path, {'p1': 'BLUE'})

        monkeypatch.setattr('calibrate.PROFILES_DIR', profiles_dir)
        calibrate(tmp_path / 'expected.json', fix=True)
        captured = capsys.readouterr()
        assert 'Suggestions de fix' in captured.out

    def test_plusieurs_profils_mixtes(self, tmp_path, monkeypatch):
        profiles_dir = tmp_path / 'profils'
        profiles_dir.mkdir()
        _profile_json(profiles_dir, 'ok', _BLUE_TRACES)
        _profile_json(profiles_dir, 'ko', _RED_TRACES)
        _profile_json(profiles_dir, 'skip', {'pr_sizes': ['L']})
        _expected_json(tmp_path, {'ok': 'BLUE', 'ko': 'BLUE'})

        monkeypatch.setattr('calibrate.PROFILES_DIR', profiles_dir)
        errors = calibrate(tmp_path / 'expected.json')
        assert errors == 1
