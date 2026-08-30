# Copyright 2026 Romy Alula — MIT License
"""Tests pour le dashboard de calibration et la commande calibrate."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from laivelup.calibrate_core import CalibrationResult, run_calibration
from laivelup.calibrate_dashboard import generate_calibrate_html
from laivelup.cli import app
from laivelup.model import AxisScore, Level

runner = CliRunner()


class TestCalibrateCore:
    def test_run_calibration_basic(self):
        result = run_calibration()
        assert result.total > 0
        assert isinstance(result.errors, int)
        assert len(result.rows) == result.total

    def test_calibration_result_structure(self):
        result = run_calibration()
        for row in result.rows:
            assert row.name
            assert row.status in ('OK', 'FAIL', 'SKIP')
            assert row.detail

    def test_calibration_with_expected(self, tmp_path):
        profiles_dir = Path(__file__).parent.parent / 'grille' / 'profils-officiels'
        expected = profiles_dir / 'expected.json'
        if expected.exists():
            result = run_calibration(expected=expected, profiles_dir=profiles_dir)
            assert result.total >= 4  # perceval, bohort, leodagan, arthur


class TestCalibrateDashboard:
    def test_generate_html_ok(self):
        result = CalibrationResult(
            total=4,
            errors=0,
            rows=[],
            profiles_dir=Path('.'),
            expected_path=Path('.'),
        )
        html = generate_calibrate_html(result)
        assert 'Calibration AIDD' in html
        assert '4/4' in html
        assert 'CALIBRÉ' in html

    def test_generate_html_with_errors(self):
        result = CalibrationResult(
            total=4,
            errors=1,
            rows=[],
            profiles_dir=Path('.'),
            expected_path=Path('.'),
        )
        html = generate_calibrate_html(result)
        assert '1 erreur' in html

    def test_empty_result(self):
        result = CalibrationResult(
            total=0,
            errors=0,
            rows=[],
            profiles_dir=Path('.'),
            expected_path=Path('.'),
        )
        html = generate_calibrate_html(result)
        assert 'Calibration AIDD' in html


class TestCalibrateCommand:
    def test_calibrate_help(self):
        r = runner.invoke(app, ['calibrate', '--help'])
        assert r.exit_code == 0
        assert 'Compare' in r.output

    def test_calibrate_basic(self, tmp_path):
        r = runner.invoke(app, ['calibrate', '--out', str(tmp_path)])
        assert r.exit_code == 0
        assert (tmp_path / 'calibrate-dashboard.html').exists()

    def test_calibrate_show_proof(self):
        r = runner.invoke(app, ['calibrate', '--show-proof'])
        assert r.exit_code == 0
