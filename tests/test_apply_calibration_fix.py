# Copyright 2026 Romy Alula — MIT License
"""Tests for apply_calibration_fix.py (R6, R7, R8)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture
def sample_diagnostic(tmp_path: Path) -> Path:
    """Create a sample diagnostic.json."""
    diag = {
        'timestamp': '2026-08-28T12:15:00Z',
        'profiles_analyzed': 2,
        'axes': ['specification', 'planning', 'implementation', 'validation'],
        'results': [],
        'summary': {
            'total_mismatch': 1,
            'blocking': 0,
            'recommended_action': 'patch_thresholds',
        },
        'scoring_defaults_used': {
            'CONFIDENCE_THRESHOLD': 0.5,
            'CONFIDENCE_PEAK': 0.9,
            'CONFIDENCE_MEDIUM': 0.8,
            'CONFIDENCE_LOW': 0.4,
            'CONFIDENCE_HARNESS_ONLY': 0.7,
            'RETRIES_PER_LEVEL': {'gold': 0.05, 'copper_or_green': 0.2, 'blue': 0.5},
        },
    }
    path = tmp_path / 'diagnostic.json'
    path.write_text(json.dumps(diag), encoding='utf-8')
    return path


class TestApplyCalibrationFix:
    """Tests for apply_calibration_fix.py."""

    def test_import(self) -> None:
        from scripts import apply_calibration_fix

        assert hasattr(apply_calibration_fix, 'apply_scenario_a')

    def test_help(self, tmp_path: Path) -> None:
        from scripts.apply_calibration_fix import main

        with pytest.raises(SystemExit) as exc_info:
            import sys

            sys.argv = ['apply_calibration_fix', '--help']
            main()
        assert exc_info.value.code == 0

    def test_dry_run_no_changes(self, sample_diagnostic: Path) -> None:
        from scripts.apply_calibration_fix import apply_scenario_a

        diag = json.loads(sample_diagnostic.read_text(encoding='utf-8'))
        # Diagnostic has same values as SCORING_DEFAULTS, so "No changes needed"
        result = apply_scenario_a(diag, dry_run=True)
        assert result.applied is False
        assert 'No changes needed' in result.changes[0]

    def test_apply_scenario_a(
        self, sample_diagnostic: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from scripts.apply_calibration_fix import apply_scenario_a

        diag = json.loads(sample_diagnostic.read_text(encoding='utf-8'))
        # Dry run first to verify logic
        result = apply_scenario_a(diag, dry_run=True)
        assert result.errors == []
        assert len(result.changes) > 0

    def test_apply_scenario_b(self, sample_diagnostic: Path) -> None:
        from scripts.apply_calibration_fix import apply_scenario_b

        diag = json.loads(sample_diagnostic.read_text(encoding='utf-8'))
        with pytest.raises(NotImplementedError, match='Scenario B'):
            apply_scenario_b(diag, dry_run=True)

    def test_thresholds_option(self, sample_diagnostic: Path, tmp_path: Path) -> None:
        from scripts.apply_calibration_fix import apply_scenario_a

        diag = json.loads(sample_diagnostic.read_text(encoding='utf-8'))
        thresholds = tmp_path / 'thresholds.json'
        thresholds.write_text(
            json.dumps(
                {
                    'CONFIDENCE_THRESHOLD': 0.6,
                    'RETRIES_PER_LEVEL': {'gold': 0.03, 'copper_or_green': 0.15, 'blue': 0.4},
                }
            ),
            encoding='utf-8',
        )
        result = apply_scenario_a(diag, dry_run=True, thresholds_path=thresholds)
        assert result.applied is False
        assert any('CONFIDENCE_THRESHOLD' in c for c in result.changes)

    def test_total_mismatch_above_2_refuses(self, sample_diagnostic: Path) -> None:
        """Scenario A refuse d'agir si total_mismatch > 2 (garde-fou)."""
        from scripts.apply_calibration_fix import apply_scenario_a

        diag = json.loads(sample_diagnostic.read_text(encoding='utf-8'))
        diag['summary']['total_mismatch'] = 3
        result = apply_scenario_a(diag, dry_run=True)
        assert result.applied is False
        assert any('total_mismatch' in e for e in result.errors)

    def test_no_thresholds_found_returns_error(self) -> None:
        """Scenario A signale une erreur si aucun seuil n'est trouve (ni fichier, ni diagnostic)."""
        from scripts.apply_calibration_fix import apply_scenario_a

        diag = {'summary': {'total_mismatch': 0}}
        result = apply_scenario_a(diag, dry_run=True)
        assert result.applied is False
        assert any('No thresholds found' in e for e in result.errors)


class TestLoadDiagnostic:
    """_load_diagnostic : erreurs de chargement (JSON malforme, fichier absent)."""

    def test_malformed_json_exits_1(self, tmp_path: Path) -> None:
        from scripts.apply_calibration_fix import _load_diagnostic

        bad = tmp_path / 'bad.json'
        bad.write_text('NOT VALID JSON {{{', encoding='utf-8')
        with pytest.raises(SystemExit) as exc_info:
            _load_diagnostic(bad)
        assert exc_info.value.code == 1

    def test_missing_file_exits_1(self, tmp_path: Path) -> None:
        from scripts.apply_calibration_fix import _load_diagnostic

        with pytest.raises(SystemExit) as exc_info:
            _load_diagnostic(tmp_path / 'nope.json')
        assert exc_info.value.code == 1
