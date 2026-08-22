"""Mode dégradé calibration — diagnostic brut quand calibrate.py échoue.

Lit les profils officiels + profils maison, produit un mapping JSON brut
(axes, deltas, confiance) pour diagnostiquer l'écart en < 10 min.

Usage:
    python scripts/calibrate_degraded.py \
        --official-dir grille/profils-officiels/ \
        --expected grille/profils-officiels/expected.json \
        --output diagnostic.json \
        --format json|table|markdown \
        --strict
"""
from __future__ import annotations

import json
import sys
import typing
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from laivelup.scoring_defaults import SCORING_DEFAULTS


@dataclass
class AxisDelta:
    expected: float
    actual: float
    delta: float
    confidence: float


@dataclass
class ProfileResult:
    profile: str
    declared: str
    computed: str
    axis_deltas: dict[str, AxisDelta] = field(default_factory=dict)
    red_flags: list[str] = field(default_factory=list)


@dataclass
class Diagnostic:
    timestamp: str
    profiles_analyzed: int
    axes: list[str]
    results: list[ProfileResult]
    summary: dict[str, typing.Any]
    scoring_defaults_used: dict[str, typing.Any] = field(default_factory=dict)


def _load_json(path: Path) -> dict:
    """Load JSON file, return empty dict on error."""
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, FileNotFoundError, OSError):
        return {}


def _compute_axis_delta(expected_val: float, actual_val: float) -> AxisDelta:
    """Compute delta and confidence for a single axis."""
    delta = actual_val - expected_val
    confidence = 1.0 if abs(delta) < 0.5 else max(0.3, 1.0 - abs(delta) * 0.1)
    return AxisDelta(expected=expected_val, actual=actual_val, delta=delta, confidence=confidence)


def diagnose(
    official_dir: Path,
    expected_path: Path,
    strict: bool = False,
) -> Diagnostic:
    """Run degraded calibration diagnostic.

    Args:
        official_dir: Directory containing official profiles (JSON files).
        expected_path: Path to expected.json with expected levels.
        strict: If True, raise on first invalid profile. Otherwise skip + log.

    Returns:
        Diagnostic with per-profile results and summary.
    """
    expected = _load_json(expected_path)
    expected_levels = expected.get('levels', {})

    axes = ['specification', 'planning', 'implementation', 'validation']
    results: list[ProfileResult] = []

    json_files = sorted(f for f in official_dir.glob('*.json') if f.name != 'expected.json')
    for json_file in json_files:
        try:
            raw = json_file.read_text(encoding='utf-8')
            profile_data = json.loads(raw)
            if not profile_data:
                if strict:
                    raise ValueError(f'Empty or invalid JSON: {json_file.name}')
                print(f'Warning: skipped {json_file.name}: empty or invalid JSON', file=sys.stderr)
                continue

            profile_name = json_file.stem
            declared = profile_data.get('declared_level', 'UNKNOWN')

            computed = declared
            axis_deltas: dict[str, AxisDelta] = {}
            red_flags: list[str] = []

            for axis in axes:
                expected_val = float(expected_levels.get(profile_name, {}).get(axis, 0))
                actual_val = float(profile_data.get('traces', {}).get(axis, 0))
                delta = _compute_axis_delta(expected_val, actual_val)
                axis_deltas[axis] = delta
                if abs(delta.delta) > 1:
                    red_flags.append(f'{axis}_mismatch')

            results.append(ProfileResult(
                profile=profile_name,
                declared=declared,
                computed=computed,
                axis_deltas=axis_deltas,
                red_flags=red_flags,
            ))
        except Exception as exc:
            if strict:
                raise
            print(f'Warning: skipped {json_file.name}: {exc}', file=sys.stderr)

    total_mismatch = sum(len(r.red_flags) for r in results)
    blocking = 1 if total_mismatch > 3 else 0
    recommended = 'patch_thresholds' if total_mismatch <= 2 else 'rewrite_mapping'

    return Diagnostic(
        timestamp=datetime.now(UTC).isoformat(),
        profiles_analyzed=len(results),
        axes=axes,
        results=results,
        summary={
            'total_mismatch': total_mismatch,
            'blocking': blocking,
            'recommended_action': recommended,
        },
        scoring_defaults_used=dict(SCORING_DEFAULTS),
    )


def _format_table(diag: Diagnostic) -> str:
    """Format diagnostic as human-readable table."""
    lines = [
        f'Calibration Degraded Diagnostic — {diag.profiles_analyzed} profiles',
        f'Timestamp: {diag.timestamp}',
        f'Total mismatch: {diag.summary["total_mismatch"]}',
        f'Blocking: {diag.summary["blocking"]}',
        f'Recommended: {diag.summary["recommended_action"]}',
        '',
        f'{"Profile":<25} {"Declared":<12} {"Computed":<12} {"Flags":<20}',
        '-' * 70,
    ]
    for r in diag.results:
        red_flags = r.red_flags if hasattr(r, 'red_flags') else r.get('red_flags', [])
        flags = ', '.join(red_flags) if red_flags else 'none'
        profile = r.profile if hasattr(r, 'profile') else r.get('profile', '?')
        declared = r.declared if hasattr(r, 'declared') else r.get('declared', '?')
        computed = r.computed if hasattr(r, 'computed') else r.get('computed', '?')
        lines.append(f'{profile:<25} {declared:<12} {computed:<12} {flags:<20}')
    return '\n'.join(lines)


def _format_markdown(diag: Diagnostic) -> str:
    """Format diagnostic as markdown table."""
    lines = [
        '# Calibration Degraded Diagnostic',
        '',
        f'- **Profiles analyzed:** {diag.profiles_analyzed}',
        f'- **Timestamp:** {diag.timestamp}',
        f'- **Total mismatch:** {diag.summary["total_mismatch"]}',
        f'- **Blocking:** {diag.summary["blocking"]}',
        f'- **Recommended action:** {diag.summary["recommended_action"]}',
        '',
        '| Profile | Declared | Computed | Red Flags |',
        '|---------|----------|----------|-----------|',
    ]
    for r in diag.results:
        red_flags = r.red_flags if hasattr(r, 'red_flags') else r.get('red_flags', [])
        flags = ', '.join(red_flags) if red_flags else 'none'
        profile = r.profile if hasattr(r, 'profile') else r.get('profile', '?')
        declared = r.declared if hasattr(r, 'declared') else r.get('declared', '?')
        computed = r.computed if hasattr(r, 'computed') else r.get('computed', '?')
        lines.append(f'| {profile} | {declared} | {computed} | {flags} |')
    return '\n'.join(lines)


def main() -> None:
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Mode dégradé calibration — diagnostic brut',
    )
    parser.add_argument('--official-dir', type=Path, required=True,
                        help='Directory containing official profiles')
    parser.add_argument('--expected', type=Path, required=True,
                        help='Path to expected.json')
    parser.add_argument('--output', type=Path, default=None,
                        help='Output file (default: stdout)')
    parser.add_argument('--format', choices=['json', 'table', 'markdown'],
                        default='json', help='Output format')
    parser.add_argument('--strict', action='store_true',
                        help='Fail fast on first invalid profile (default: graceful)')

    args = parser.parse_args()

    if not args.official_dir.is_dir():
        print(f'Error: {args.official_dir} is not a directory', file=sys.stderr)
        sys.exit(1)

    diag = diagnose(args.official_dir, args.expected, strict=args.strict)

    if args.format == 'json':
        output = json.dumps(asdict(diag), indent=2, ensure_ascii=False)
    elif args.format == 'table':
        output = _format_table(diag)
    else:
        output = _format_markdown(diag)

    if args.output:
        args.output.write_text(output, encoding='utf-8')
        print(f'Diagnostic written to {args.output}')
    else:
        print(output)


if __name__ == '__main__':
    main()
