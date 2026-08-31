# Copyright 2026 Romy Alula — MIT License
"""Calibration core : compare les verdicts du scoring aux niveaux attendus.

Module réutilisable par calibrate.py (script) et cli.py (commande).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .scoring import evaluate
from .utils import load_profile_data

PROFILES_DIR = Path(__file__).parent.parent.parent / 'grille' / 'profils-officiels'
EXPECTED_FILE = PROFILES_DIR / 'expected.json'


@dataclass
class CalibrationRow:
    name: str
    status: str  # 'OK', 'FAIL', 'SKIP'
    detail: str
    obtained: str | None
    expected: str | None
    axis_scores: list = field(default_factory=list)


@dataclass
class CalibrationResult:
    total: int
    errors: int
    rows: list[CalibrationRow]
    profiles_dir: Path
    expected_path: Path


def _profile_files(profiles_dir: Path, expected_name: str) -> list[Path]:
    excluded = {expected_name}
    return sorted(p for p in profiles_dir.glob('*.json') if p.name not in excluded)


def _load_expected(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding='utf-8'))
    return {k: v.upper() for k, v in data.get('levels', {}).items()}


def run_calibration(
    expected: Path | None = None,
    profiles_dir: Path | None = None,
) -> CalibrationResult:
    """Exécute la calibration complète et retourne les résultats structurés."""
    exp_path = expected or EXPECTED_FILE
    prof_dir = profiles_dir or PROFILES_DIR
    expected_data = _load_expected(exp_path)
    profile_files = _profile_files(prof_dir, exp_path.name)

    rows: list[CalibrationRow] = []
    errors = 0

    for p in profile_files:
        profile = load_profile_data(p)
        verdict = evaluate(profile)
        stem = p.stem

        if stem not in expected_data:
            rows.append(
                CalibrationRow(
                    name=stem,
                    status='SKIP',
                    detail='pas dans expected.json',
                    obtained=verdict.level.name if verdict.level else 'UNDECIDED',
                    expected=None,
                    axis_scores=verdict.axis_scores,
                )
            )
            continue

        exp_level = expected_data[stem]
        obt_level = verdict.level.name if verdict.level else 'UNDECIDED'

        if exp_level == 'UNDECIDED':
            if not verdict.decided:
                rows.append(
                    CalibrationRow(
                        name=stem,
                        status='OK',
                        detail='refus confirmé',
                        obtained='UNDECIDED',
                        expected='UNDECIDED',
                        axis_scores=verdict.axis_scores,
                    )
                )
            else:
                rows.append(
                    CalibrationRow(
                        name=stem,
                        status='FAIL',
                        detail=f'attendu UNDECIDED, obtenu {obt_level}',
                        obtained=obt_level,
                        expected='UNDECIDED',
                        axis_scores=verdict.axis_scores,
                    )
                )
                errors += 1
        elif verdict.decided and verdict.level is not None:
            if verdict.level.name == exp_level:
                rows.append(
                    CalibrationRow(
                        name=stem,
                        status='OK',
                        detail=obt_level,
                        obtained=obt_level,
                        expected=exp_level,
                        axis_scores=verdict.axis_scores,
                    )
                )
            else:
                rows.append(
                    CalibrationRow(
                        name=stem,
                        status='FAIL',
                        detail=f'attendu {exp_level}, obtenu {obt_level}',
                        obtained=obt_level,
                        expected=exp_level,
                        axis_scores=verdict.axis_scores,
                    )
                )
                errors += 1
        else:
            rows.append(
                CalibrationRow(
                    name=stem,
                    status='FAIL',
                    detail=f'attendu {exp_level}, obtenu UNDECIDED',
                    obtained='UNDECIDED',
                    expected=exp_level,
                    axis_scores=verdict.axis_scores,
                )
            )
            errors += 1

    return CalibrationResult(
        total=len(rows),
        errors=errors,
        rows=rows,
        profiles_dir=prof_dir,
        expected_path=exp_path,
    )
