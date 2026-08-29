#!/usr/bin/env python3
# Copyright 2026 Romy Alula — MIT License
"""Calibration : compare les verdicts du scoring aux niveaux attendus.

Usage :
  python scripts/calibrate.py                                    # mode template (génère expected.json)
  python scripts/calibrate.py --expected grille/profils-officiels/expected.json
  python scripts/calibrate.py --expected grille/profils-officiels/expected.json --fix
  python scripts/calibrate.py --expected grille/profils-officiels/expected.json --diff

Correctif (28/08) : le glob des profils incluait `expected.json` lui-même
(fichier de réponses, pas un profil), listé comme un 5e profil fantôme
"expected: pas dans expected.json" dans la sortie. Exclu du glob désormais.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Ajouter le src au path pour importer laivelup
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from laivelup.model import AXES, Level, ProfileData
from laivelup.scoring import evaluate

PROFILES_DIR = Path(__file__).parent.parent / 'grille' / 'profils-officiels'
EXPECTED_FILE = PROFILES_DIR / 'expected.json'

# Labels FR pour l'affichage
AXIS_LABELS = {
    'size': 'Taille',
    'harness': 'Harness',
    'intervention': 'Intervention',
    'parallel': 'En parallele',
}

LEVEL_LABELS = {
    Level.WHITE: 'White',
    Level.RED: 'Red',
    Level.BLUE: 'Blue',
    Level.GREEN: 'Green',
    Level.COPPER: 'Copper',
    Level.SILVER: 'Silver',
    Level.GOLD: 'Gold',
}


def _profile_files(expected_path: Path | None = None) -> list[Path]:
    """Liste les fichiers de profils, en excluant les fichiers de réponses
    attendues (expected.json ou équivalent passé via --expected)."""
    excluded = {EXPECTED_FILE.name}
    if expected_path is not None:
        excluded.add(expected_path.name)
    return sorted(p for p in PROFILES_DIR.glob('*.json') if p.name not in excluded)


def _load_profile(path: Path) -> ProfileData:
    """Charge un profil JSON en ProfileData."""
    data = json.loads(path.read_text(encoding='utf-8'))
    declared = data.get('declared_level')
    if isinstance(declared, str) and declared:
        declared = Level[declared.upper()]
    else:
        declared = None
    return ProfileData(
        name=data.get('name', path.stem),
        declared_level=declared,
        traces=data.get('traces', {}),
        answers=data.get('answers', {}),
        meta=data.get('meta', {}),
    )


def _load_expected(path: Path) -> dict[str, str]:
    """Charge les niveaux attendus {profil_name: level_name}."""
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding='utf-8'))
    return {k: v.upper() for k, v in data.get('levels', {}).items()}


def generate_template() -> None:
    """Génère un expected.json.template avec tous les profils trouvés."""
    profiles = _profile_files()
    if not profiles:
        print(f'Aucun profil trouvé dans {PROFILES_DIR}')
        return

    levels = {}
    for p in profiles:
        profile = _load_profile(p)
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
        if limiting:
            return (
                f"  -> {name} : axe '{AXIS_LABELS.get(limiting.axe, limiting.axe)}' "
                f'bloque a {LEVEL_LABELS.get(limiting.level, "?")} '
                f'(attendu {expected_level})'
            )
    return f'  -> {name} : verifier les traces'


def calibrate(expected_path: Path, fix: bool = False, diff: bool = False) -> int:
    """Compare les verdicts aux niveaux attendus. Retourne le nombre d'erreurs."""
    expected = _load_expected(expected_path)
    if not expected:
        print(f'Aucun niveau attendu dans {expected_path}')
        return 0

    profiles = _profile_files(expected_path)
    errors = 0
    results = []

    for p in profiles:
        profile = _load_profile(p)
        verdict = evaluate(profile)
        stem = p.stem

        if stem not in expected:
            results.append((stem, 'SKIP', 'pas dans expected.json', verdict, None))
            continue

        expected_level = expected[stem]
        if expected_level == 'UNDECIDED':
            if not verdict.decided:
                results.append((stem, 'OK', 'refus confirme', verdict, None))
            else:
                detail = f'attendu UNDECIDED, obtenu {verdict.level.name}'
                results.append((stem, 'FAIL', detail, verdict, expected_level))
                errors += 1
        elif verdict.decided and verdict.level is not None:
            if verdict.level.name == expected_level:
                results.append((stem, 'OK', verdict.level.name, verdict, expected_level))
            else:
                detail = f'attendu {expected_level}, obtenu {verdict.level.name}'
                results.append((stem, 'FAIL', detail, verdict, expected_level))
                errors += 1
        else:
            detail = f'attendu {expected_level}, obtenu UNDECIDED'
            results.append((stem, 'FAIL', detail, verdict, expected_level))
            errors += 1

    # Affichage
    print(f'\nCalibration : {len(results)} profils testes, {errors} erreurs\n')
    for name, status, detail, verdict, expected_level in results:
        icon = '+' if status == 'OK' else 'X' if status == 'FAIL' else '-'
        print(f'  {icon} {name}: {detail}')

        if diff and expected_level and verdict and verdict.axis_scores:
            for a in verdict.axis_scores:
                if a.level is not None:
                    a_label = AXIS_LABELS.get(a.axe, a.axe)
                    a_level = LEVEL_LABELS.get(a.level, a.level.name)
                    # Comparer avec l'axe correspondant de l'attendu
                    print(f'      {a_label}: {a_level} (confiance {a.confidence:.0%})')

    if errors > 0 and fix:
        print('\n--- Suggestions de fix ---')
        for name, status, detail, verdict, expected_level in results:
            if status == 'FAIL' and expected_level:
                print(
                    _fix_suggestion(
                        name,
                        verdict.level if verdict else None,
                        expected_level,
                        verdict.axis_scores if verdict else [],
                    )
                )

    return errors


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
