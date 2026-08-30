# Copyright 2026 Romy Alula — MIT License
"""Tests calibrate_core.py : gaps de couverture (coverage-90-closing-gaps.md).

Cible : _load_expected sans cle 'levels', run_calibration SKIP/FAIL/UNDECIDED.
Note : distinct de scripts/calibrate.py (module different, teste dans
test_calibrate.py) — ici on cible laivelup.calibrate_core.run_calibration,
utilise par la commande CLI `laivelup calibrate` et le dashboard.
"""

from __future__ import annotations

import json
from pathlib import Path

from laivelup.calibrate_core import _load_expected, run_calibration

# Traces completes pour un profil BLUE (tous les axes decident)
_BLUE_TRACES = {
    'pr_sizes': ['M', 'M'],
    'context_versioned': True,
    'retries_after_fact': 0.4,
    'retries_triangulated': True,
    'parallel_projects': 1,
}


def _write_profile(dir_: Path, name: str, traces: dict, declared: str | None = None) -> Path:
    data = {'name': name, 'traces': traces}
    if declared:
        data['declared_level'] = declared
    path = dir_ / f'{name}.json'
    path.write_text(json.dumps(data), encoding='utf-8')
    return path


def _write_expected(path: Path, levels: dict) -> Path:
    path.write_text(json.dumps({'levels': levels}), encoding='utf-8')
    return path


# --- _load_expected ------------------------------------------------------


class TestLoadExpectedNoLevelsKey:
    def test_missing_levels_key_returns_empty_dict(self, tmp_path):
        expected = tmp_path / 'expected.json'
        expected.write_text('{}', encoding='utf-8')
        assert _load_expected(expected) == {}


# --- run_calibration : SKIP -----------------------------------------------


class TestRunCalibrationSkip:
    def test_profile_absent_from_expected_is_skipped(self, tmp_path):
        profiles_dir = tmp_path / 'profils'
        profiles_dir.mkdir()
        _write_profile(profiles_dir, 'alice', _BLUE_TRACES)
        expected = _write_expected(tmp_path / 'expected.json', {})

        result = run_calibration(expected=expected, profiles_dir=profiles_dir)
        assert result.total == 1
        assert result.rows[0].status == 'SKIP'
        assert result.errors == 0


# --- run_calibration : UNDECIDED ------------------------------------------


class TestRunCalibrationUndecided:
    def test_undecided_expected_and_obtained_is_ok(self, tmp_path):
        profiles_dir = tmp_path / 'profils'
        profiles_dir.mkdir()
        _write_profile(profiles_dir, 'alice', {})  # traces vides -> undecided
        expected = _write_expected(tmp_path / 'expected.json', {'alice': 'UNDECIDED'})

        result = run_calibration(expected=expected, profiles_dir=profiles_dir)
        assert result.errors == 0
        assert result.rows[0].status == 'OK'

    def test_undecided_expected_but_decided_is_fail(self, tmp_path):
        profiles_dir = tmp_path / 'profils'
        profiles_dir.mkdir()
        _write_profile(profiles_dir, 'alice', _BLUE_TRACES)
        expected = _write_expected(tmp_path / 'expected.json', {'alice': 'UNDECIDED'})

        result = run_calibration(expected=expected, profiles_dir=profiles_dir)
        assert result.errors == 1
        assert result.rows[0].status == 'FAIL'
        assert 'UNDECIDED' in result.rows[0].detail


# --- run_calibration : niveau decide -------------------------------------


class TestRunCalibrationDecidedLevel:
    def test_decided_matching_level_is_ok(self, tmp_path):
        profiles_dir = tmp_path / 'profils'
        profiles_dir.mkdir()
        _write_profile(profiles_dir, 'alice', _BLUE_TRACES)
        expected = _write_expected(tmp_path / 'expected.json', {'alice': 'BLUE'})

        result = run_calibration(expected=expected, profiles_dir=profiles_dir)
        assert result.errors == 0
        assert result.rows[0].status == 'OK'

    def test_decided_but_wrong_level_is_fail(self, tmp_path):
        profiles_dir = tmp_path / 'profils'
        profiles_dir.mkdir()
        _write_profile(profiles_dir, 'alice', _BLUE_TRACES)
        expected = _write_expected(tmp_path / 'expected.json', {'alice': 'GOLD'})

        result = run_calibration(expected=expected, profiles_dir=profiles_dir)
        assert result.errors == 1
        assert result.rows[0].status == 'FAIL'
        assert 'attendu GOLD' in result.rows[0].detail

    def test_expected_decided_but_verdict_undecided_is_fail(self, tmp_path):
        profiles_dir = tmp_path / 'profils'
        profiles_dir.mkdir()
        _write_profile(profiles_dir, 'alice', {})  # pas de traces -> undecided
        expected = _write_expected(tmp_path / 'expected.json', {'alice': 'GOLD'})

        result = run_calibration(expected=expected, profiles_dir=profiles_dir)
        assert result.errors == 1
        assert result.rows[0].status == 'FAIL'
        assert 'obtenu UNDECIDED' in result.rows[0].detail
