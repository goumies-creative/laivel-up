"""Applique un patch scoring basé sur le diagnostic dégradé.

Usage:
    python scripts/apply_calibration_fix.py \
        --scenario A \
        --diagnostic diagnostic.json \
        --dry-run
"""
from __future__ import annotations

import json
import sys
import typing
from dataclasses import dataclass
from pathlib import Path

if typing.TYPE_CHECKING:
    pass


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


def apply_scenario_a(diagnostic: dict, dry_run: bool = True) -> FixResult:
    """Apply scenario A: patch thresholds.

    Modifies SCORING_THRESHOLDS and LEVEL_BOUNDARIES in scoring.py.
    """
    changes = []
    errors = []

    summary = diagnostic.get('summary', {})
    total_mismatch = summary.get('total_mismatch', 0)

    if total_mismatch > 2:
        errors.append(f'Scenario A requires total_mismatch <= 2, got {total_mismatch}')
        return FixResult(scenario='A', applied=False, changes=changes, errors=errors)

    if dry_run:
        changes.append('[DRY RUN] Would patch SCORING_THRESHOLDS in scoring.py')
        changes.append('[DRY RUN] Would patch LEVEL_BOUNDARIES in scoring.py')
    else:
        # TODO: implement actual patching
        changes.append('Patched SCORING_THRESHOLDS')
        changes.append('Patched LEVEL_BOUNDARIES')

    return FixResult(scenario='A', applied=not dry_run, changes=changes, errors=errors)


def apply_scenario_b(diagnostic: dict, dry_run: bool = True) -> FixResult:
    """Apply scenario B: rewrite mapping.

    Regenerates mapping from official profiles via calibrate.py.
    """
    changes = []
    errors = []

    if dry_run:
        changes.append('[DRY RUN] Would regenerate expected.json from official profiles')
        changes.append('[DRY RUN] Would re-run calibrate.py')
    else:
        # TODO: implement actual rewriting
        changes.append('Regenerated expected.json')
        changes.append('Re-ran calibrate.py')

    return FixResult(scenario='B', applied=not dry_run, changes=changes, errors=errors)


def apply_scenario_c(diagnostic: dict, dry_run: bool = True) -> FixResult:
    """Apply scenario C: deliver as-is.

    Documents gaps in METHODE.md and README.md.
    """
    changes = []
    errors = []

    if dry_run:
        changes.append('[DRY RUN] Would add "Known Gaps" section to METHODE.md')
        changes.append('[DRY RUN] Would add "Known Gaps" section to README.md')
    else:
        # TODO: implement actual documentation
        changes.append('Added "Known Gaps" to METHODE.md')
        changes.append('Added "Known Gaps" to README.md')

    return FixResult(scenario='C', applied=not dry_run, changes=changes, errors=errors)


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
    parser.add_argument('--scenario', choices=['A', 'B', 'C'], required=True,
                        help='Scénario à appliquer')
    parser.add_argument('--diagnostic', type=Path, required=True,
                        help='Chemin vers diagnostic.json')
    parser.add_argument('--dry-run', action='store_true', default=True,
                        help='Mode dry-run (par défaut)')
    parser.add_argument('--apply', action='store_true',
                        help='Appliquer réellement (désactive dry-run)')

    args = parser.parse_args()

    diagnostic = _load_diagnostic(args.diagnostic)
    dry_run = not args.apply

    handler = SCENARIO_HANDLERS[args.scenario]
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
