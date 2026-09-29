#!/usr/bin/env python3
# Copyright 2026 Romy Alula — MIT License
"""Calibration : compare les verdicts du scoring aux niveaux attendus.

Usage :
  python scripts/calibrate.py                                    # mode template (génère expected.json)
  python scripts/calibrate.py --expected grille/profils-officiels/expected.json
  python scripts/calibrate.py --expected grille/profils-officiels/expected.json --fix
  python scripts/calibrate.py --expected grille/profils-officiels/expected.json --diff

La boucle de comparaison est unique : `laivelup.calibrate_core.run_calibration`.
Ce script ne fait que le rendu texte et le mode `--template`.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Ajouter le src au path pour importer laivelup
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from laivelup.calibrate_core import EXPECTED_FILE, PROFILES_DIR, _load_expected, run_calibration
from laivelup.calibrate_core import _profile_files as core_profile_files
from laivelup.model import AXIS_LABELS, Level
from laivelup.scoring import evaluate
from laivelup.utils import load_profile_data

# Re-export pour compatibilité tests (test_calibrate.py importe _load_profile)
_load_profile = load_profile_data


def _level_name(level: Level) -> str:
    """Nom de niveau en texte plat (LEVEL_LABELS porte un emoji, hors script)."""
    return level.name.capitalize()


def _profile_files(expected_path: Path | None = None) -> list[Path]:
    """Liste les fichiers de profils, en excluant les fichiers de réponses
    attendues (expected.json ou équivalent passé via --expected)."""
    return core_profile_files(PROFILES_DIR, *((expected_path.name,) if expected_path else ()))


def generate_template() -> None:
    """Génère un expected.json.template avec tous les profils trouvés."""
    profiles = _profile_files()
    if not profiles:
        print(f'Aucun profil trouvé dans {PROFILES_DIR}')
        return

    levels = {}
    for p in profiles:
        profile = load_profile_data(p)
        verdict = evaluate(profile)
        if verdict.decided and verdict.level is not None:
            levels[p.stem] = verdict.level.name
        else:
            levels[p.stem] = 'UNDECIDED'

    template = {
        '_comment': 'Niveaux attendus par profil. Modifier quand les profils officiels sont disponibles.',
        'levels': levels,
    }
    out = PROFILES_DIR / 'expected.json.template'
    out.write_text(json.dumps(template, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'Template généré : {out}')
    print('Niveaux actuels ( basés sur les profils existants ) :')
    for name, level in sorted(levels.items()):
        print(f'  {name}: {level}')


def _axis_diff(verdict_level: Level | None, expected_level: str) -> str:
    """Diff détaillée par axe entre le verdict obtenu et l'attendu."""
    if verdict_level is None:
        return 'verdict = UNDECIDED'
    expected = Level[expected_level]
    diff = verdict_level.value - expected.value
    if diff > 0:
        return f'{verdict_level.name} trop haut (attendu {expected_level}, -{diff} crans)'
    if diff < 0:
        return f'{verdict_level.name} trop bas (attendu {expected_level}, +{abs(diff)} crans)'
    return 'OK'


def _fix_suggestion(
    name: str, verdict_level: Level | None, expected_level: str, axis_scores: list
) -> str:
    """Suggestion de fix basée sur l'axe plancher."""
    if verdict_level is None:
        return f'  -> Profil {name} : données insuffisantes, ajouter des traces'

    expected = Level[expected_level]
    if verdict_level.value < expected.value:
        # Il manque des crans : identifier l'axe plancher
        limiting = next((a for a in axis_scores if a.level == verdict_level), None)
        if limiting and limiting.level:
            return (
                f"  -> {name} : axe '{AXIS_LABELS.get(limiting.axe, limiting.axe)}' "
                f'bloque a {_level_name(limiting.level)} (attendu {expected_level})'
            )
    return f'  -> {name} : verifier les traces'


def calibrate(expected_path: Path, fix: bool = False, diff: bool = False) -> int:
    """Compare les verdicts aux niveaux attendus. Retourne le nombre d'erreurs."""
    if not _load_expected(expected_path):
        print(f'Aucun niveau attendu dans {expected_path}')
        return 0

    result = run_calibration(expected=expected_path, profiles_dir=PROFILES_DIR)

    print(f'\nCalibration : {result.total} profils testes, {result.errors} erreurs\n')
    for row in result.rows:
        icon = '+' if row.status == 'OK' else 'X' if row.status == 'FAIL' else '-'
        print(f'  {icon} {row.name}: {row.detail}')

        if diff and row.expected and row.axis_scores:
            for a in row.axis_scores:
                if a.level is not None:
                    a_label = AXIS_LABELS.get(a.axe, a.axe)
                    a_level = _level_name(a.level)
                    # Comparer avec l'axe correspondant de l'attendu
                    print(f'      {a_label}: {a_level} (confiance {a.confidence:.0%})')

    if result.errors > 0 and fix:
        print('\n--- Suggestions de fix ---')
        for row in result.rows:
            if row.status == 'FAIL' and row.expected:
                print(
                    _fix_suggestion(
                        row.name,
                        row.verdict.level if row.verdict else None,
                        row.expected,
                        row.verdict.axis_scores if row.verdict else [],
                    )
                )

    return result.errors


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description='Calibration des verdicts AIDD')
    parser.add_argument('--template', action='store_true', help='Generer expected.json.template')
    parser.add_argument(
        '--expected', type=Path, default=EXPECTED_FILE, help='Chemin vers expected.json'
    )
    parser.add_argument('--fix', action='store_true', help='Suggestions de fix')
    parser.add_argument('--diff', action='store_true', help='Afficher les diffs par axe')
    args = parser.parse_args()

    if args.template:
        generate_template()
    else:
        errors = calibrate(args.expected, fix=args.fix, diff=args.diff)
        sys.exit(1 if errors > 0 else 0)


if __name__ == '__main__':
    main()
