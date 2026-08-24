"""Tests skeleton pour calibrate_degraded.py."""

from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture
def sample_diagnostic() -> dict:
    """Sample diagnostic data for tests."""
    return {
        'timestamp': '2026-08-28T12:15:00Z',
        'profiles_analyzed': 2,
        'axes': ['specification', 'planning', 'implementation', 'validation'],
        'results': [
            {
                'profile': 'profil-maison-1',
                'declared': 'BLUE',
                'computed': 'BLUE',
                'axis_deltas': {},
                'red_flags': [],
            },
        ],
        'summary': {
            'total_mismatch': 0,
            'blocking': 0,
            'recommended_action': 'patch_thresholds',
        },
    }


class TestCalibrateDegraded:
    """Tests for calibrate_degraded.py."""

    def test_import(self) -> None:
        """Module imports successfully."""
        from scripts import calibrate_degraded

        assert hasattr(calibrate_degraded, 'diagnose')

    def test_help(self, tmp_path: Path) -> None:
        """CLI --help works."""
        from scripts.calibrate_degraded import main

        with pytest.raises(SystemExit) as exc_info:
            import sys

            sys.argv = ['calibrate_degraded', '--help']
            main()
        assert exc_info.value.code == 0

    def test_diagnose_empty_dir(self, tmp_path: Path) -> None:
        """Diagnose on empty directory returns empty diagnostic."""
        from scripts.calibrate_degraded import diagnose

        expected_path = tmp_path / 'expected.json'
        expected_path.write_text('{"levels": {}}', encoding='utf-8')
        result = diagnose(tmp_path, expected_path)
        assert result.profiles_analyzed == 0

    def test_diagnose_with_profiles(self, tmp_path: Path) -> None:
        """Diagnose with sample profiles."""
        from scripts.calibrate_degraded import diagnose

        profile = tmp_path / 'test-profile.json'
        profile.write_text(
            json.dumps(
                {
                    'name': 'test-profile',
                    'declared_level': 'GREEN',
                    'traces': {},
                }
            ),
            encoding='utf-8',
        )
        expected_path = tmp_path / 'expected.json'
        expected_path.write_text('{"levels": {}}', encoding='utf-8')
        result = diagnose(tmp_path, expected_path)
        assert result.profiles_analyzed == 1

    def test_format_table(self, sample_diagnostic: dict) -> None:
        """Table format produces output."""
        from scripts.calibrate_degraded import Diagnostic, _format_table

        diag = Diagnostic(**sample_diagnostic)
        output = _format_table(diag)
        assert 'Calibration Degraded Diagnostic' in output

    def test_format_markdown(self, sample_diagnostic: dict) -> None:
        """Markdown format produces output."""
        from scripts.calibrate_degraded import Diagnostic, _format_markdown

        diag = Diagnostic(**sample_diagnostic)
        output = _format_markdown(diag)
        assert '# Calibration Degraded Diagnostic' in output

    def test_strict_mode_fails_on_invalid_profile(self, tmp_path: Path) -> None:
        """Strict mode raises on invalid profile."""
        from scripts.calibrate_degraded import diagnose

        bad_profile = tmp_path / 'bad.json'
        bad_profile.write_text('NOT JSON', encoding='utf-8')
        expected_path = tmp_path / 'expected.json'
        expected_path.write_text('{"levels": {}}', encoding='utf-8')
        with pytest.raises((json.JSONDecodeError, ValueError)):
            diagnose(tmp_path, expected_path, strict=True)

    def test_graceful_mode_skips_invalid_profiles(self, tmp_path: Path) -> None:
        """Graceful mode skips invalid profiles and continues."""
        from scripts.calibrate_degraded import diagnose

        bad_profile = tmp_path / 'bad.json'
        bad_profile.write_text('NOT JSON', encoding='utf-8')
        good_profile = tmp_path / 'good.json'
        good_profile.write_text(
            json.dumps(
                {
                    'name': 'good',
                    'declared_level': 'GREEN',
                    'traces': {},
                }
            ),
            encoding='utf-8',
        )
        expected_path = tmp_path / 'expected.json'
        expected_path.write_text('{"levels": {}}', encoding='utf-8')
        result = diagnose(tmp_path, expected_path, strict=False)
        assert result.profiles_analyzed == 1

    def test_reads_scoring_defaults(self) -> None:
        """Diagnostic includes scoring_defaults_used."""
        from scripts.calibrate_degraded import diagnose
        from pathlib import Path
        from laivelup.scoring_defaults import SCORING_DEFAULTS

        tmp = Path('/tmp/test_sd')
        tmp.mkdir(exist_ok=True)
        expected_path = tmp / 'expected.json'
        expected_path.write_text('{"levels": {}}', encoding='utf-8')
        result = diagnose(tmp, expected_path)
        assert result.scoring_defaults_used == dict(SCORING_DEFAULTS)
