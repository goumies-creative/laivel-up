"""Applique un patch scoring basé sur le diagnostic dégradé.

Usage:
    python scripts/apply_calibration_fix.py \\
        --scenario A \\
        --diagnostic diagnostic.json \\
        --thresholds expected.json \\
        --dry-run

Safety: --apply creates a .bak backup and validates syntax before declaring success.
"""

from __future__ import annotations

import ast
import json
import re
import shutil
import sys
import typing
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'src'))
from laivelup.scoring_defaults import SCORING_DEFAULTS


@dataclass
class FixResult:
    scenario: str
    applied: bool
    changes: list[str]
    errors: list[str]


def _load_diagnostic(path: Path) -> dict:
    """Load diagnostic JSON file."""
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, FileNotFoundError, OSError) as e:
        print(f'Error loading diagnostic: {e}', file=sys.stderr)
        sys.exit(1)


def apply_scenario_a(
    diagnostic: dict,
    dry_run: bool = True,
    thresholds_path: Path | None = None,
) -> FixResult:
    """Apply scenario A: patch thresholds in SCORING_DEFAULTS.

    Reads expected thresholds from --thresholds file or diagnostic.json,
    computes deltas against current SCORING_DEFAULTS, and patches scoring_defaults.py.
    """
    changes = []
    errors = []

    summary = diagnostic.get('summary', {})
    total_mismatch = summary.get('total_mismatch', 0)

    if total_mismatch > 2:
        errors.append(f'Scenario A requires total_mismatch <= 2, got {total_mismatch}')
        return FixResult(scenario='A', applied=False, changes=changes, errors=errors)

    # Load thresholds from file or diagnostic
    if thresholds_path and thresholds_path.exists():
        expected = json.loads(thresholds_path.read_text(encoding='utf-8'))
    else:
        expected = diagnostic.get('scoring_defaults_used', {})

    if not expected:
        errors.append('No thresholds found in --thresholds file or diagnostic.json')
        return FixResult(scenario='A', applied=False, changes=changes, errors=errors)

    # Compute deltas
    scoring_defaults_path = (
        Path(__file__).resolve().parent.parent / 'src' / 'laivelup' / 'scoring_defaults.py'
    )
    current_source = scoring_defaults_path.read_text(encoding='utf-8')

    for key in (
        'CONFIDENCE_THRESHOLD',
        'CONFIDENCE_PEAK',
        'CONFIDENCE_MEDIUM',
        'CONFIDENCE_LOW',
        'CONFIDENCE_HARNESS_ONLY',
    ):
        old_val = SCORING_DEFAULTS.get(key)
        new_val = expected.get(key)
        if new_val is not None and old_val != new_val:
            if dry_run:
                changes.append(f'[DRY RUN] {key}: {old_val} -> {new_val}')
            else:
                current_source = current_source.replace(
                    f"'{key}': {old_val}",
                    f"'{key}': {new_val}",
                )
                changes.append(f'{key}: {old_val} -> {new_val}')

    rpl = expected.get('RETRIES_PER_LEVEL', {})
    current_rpl = SCORING_DEFAULTS.get('RETRIES_PER_LEVEL', {})
    for sub_key in ('gold', 'copper_or_green', 'blue'):
        old_val = current_rpl.get(sub_key)
        new_val = rpl.get(sub_key)
        if new_val is not None and old_val != new_val:
            if dry_run:
                changes.append(f'[DRY RUN] RETRIES_PER_LEVEL.{sub_key}: {old_val} -> {new_val}')
            else:
                current_source = current_source.replace(
                    f"'{sub_key}': {old_val}",
                    f"'{sub_key}': {new_val}",
                )
                changes.append(f'RETRIES_PER_LEVEL.{sub_key}: {old_val} -> {new_val}')

    if not dry_run and changes:
        # Backup before patching
        backup_path = scoring_defaults_path.with_suffix('.py.bak')
        shutil.copy2(scoring_defaults_path, backup_path)
        changes.insert(0, f'Backup created: {backup_path}')

        scoring_defaults_path.write_text(current_source, encoding='utf-8')
        changes.insert(1, f'Patched {scoring_defaults_path}')

        # Validate syntax post-patch
        try:
            ast.parse(current_source)
            changes.insert(2, 'Syntax validation: OK')
        except SyntaxError as e:
            # Restore backup on syntax error
            shutil.copy2(backup_path, scoring_defaults_path)
            errors.append(f'Syntax error after patch — backup restored: {e}')
            return FixResult(scenario='A', applied=False, changes=changes, errors=errors)

        # Validate import works
        try:
            import importlib

            import laivelup.scoring_defaults

            importlib.reload(laivelup.scoring_defaults)
            changes.insert(3, 'Import validation: OK')
        except Exception as e:
            errors.append(f'Import validation failed (syntax OK, but import broken): {e}')
            # Don't restore — syntax is valid, likely a runtime issue

    if not changes:
        changes.append('No changes needed — SCORING_DEFAULTS already matches expected')

    return FixResult(scenario='A', applied=not dry_run, changes=changes, errors=errors)


def apply_scenario_b(diagnostic: dict, dry_run: bool = True) -> FixResult:
    """Apply scenario B: rewrite mapping.

    Regenerates mapping from official profiles via calibrate.py.
    NOT YET IMPLEMENTED — raises NotImplementedError.
    """
    raise NotImplementedError(
        'Scenario B (rewrite mapping) requires manual setup:\n'
        '1. Run: python scripts/calibrate.py --profiles <official_profiles_dir>\n'
        '2. Review generated expected.json\n'
        '3. Run: python scripts/apply_calibration_fix.py --scenario A --thresholds expected.json --apply'
    )


def apply_scenario_c(diagnostic: dict, dry_run: bool = True) -> FixResult:
    """Apply scenario C: deliver as-is.

    Documents gaps in METHODE.md and README.md.
    NOT YET IMPLEMENTED — raises NotImplementedError.
    """
    raise NotImplementedError(
        'Scenario C (deliver as-is) requires manual documentation:\n'
        "1. Add 'Known Gaps' section to METHODE.md\n"
        "2. Add 'Known Gaps' section to README.md\n"
        '3. Document specific axis limitations in reports'
    )


SCENARIO_HANDLERS = {
    'A': apply_scenario_a,
    'B': apply_scenario_b,
    'C': apply_scenario_c,
}


def main() -> None:
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Applique un patch scoring basé sur le diagnostic dégradé',
    )
    parser.add_argument(
        '--scenario', choices=['A', 'B', 'C'], required=True, help='Scénario à appliquer'
    )
    parser.add_argument(
        '--diagnostic', type=Path, required=True, help='Chemin vers diagnostic.json'
    )
    parser.add_argument(
        '--dry-run', action='store_true', default=True, help='Mode dry-run (par défaut)'
    )
    parser.add_argument(
        '--apply', action='store_true', help='Appliquer réellement (désactive dry-run)'
    )
    parser.add_argument(
        '--thresholds',
        type=Path,
        default=None,
        help='Chemin vers expected.json avec seuils attendus',
    )

    args = parser.parse_args()

    diagnostic = _load_diagnostic(args.diagnostic)
    dry_run = not args.apply

    handler = SCENARIO_HANDLERS[args.scenario]
    if args.scenario == 'A':
        result = handler(diagnostic, dry_run=dry_run, thresholds_path=args.thresholds)
    else:
        result = handler(diagnostic, dry_run=dry_run)

    print(f'Scenario: {result.scenario}')
    print(f'Applied: {result.applied}')
    if result.changes:
        print('Changes:')
        for change in result.changes:
            print(f'  - {change}')
    if result.errors:
        print('Errors:', file=sys.stderr)
        for error in result.errors:
            print(f'  - {error}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
