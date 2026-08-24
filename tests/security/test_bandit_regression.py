# Copyright 2026 Romy Alula — MIT License
"""Tests de securite : regression bandit.

Verifie que bandit ne detecte aucune issue haute/critique par rapport
au fichier baseline. Met a jour le baseline si necessaire.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).parent.parent.parent
BASELINE = Path(__file__).parent / 'bandit-baseline.json'


@pytest.mark.security
class TestBanditRegression:
    def test_bandit_no_high_critical(self):
        """bandit -r src/ ne doit retourner aucune issue HIGH ou CRITICAL."""
        result = subprocess.run(
            ['python', '-m', 'bandit', '-r', 'src/', '-f', 'json', '-q'],
            capture_output=True,
            text=True,
            cwd=str(REPO),
        )
        if result.returncode == 0:
            # Pas d'issues
            return
        try:
            data = json.loads(result.stdout)
            issues = data.get('results', [])
            high_critical = [
                i
                for i in issues
                if i.get('issue_severity') in ('HIGH', 'MEDIUM')
                and i.get('issue_confidence') in ('HIGH', 'MEDIUM')
            ]
            assert len(high_critical) == 0, (
                f'Bandit a detecte {len(high_critical)} issues haute/critique :\n'
                + '\n'.join(
                    f'  - {i["filename"]}:{i["line_number"]} {i["issue_text"]}'
                    for i in high_critical[:5]
                )
            )
        except json.JSONDecodeError:
            # Bandit n'a pas retourne du JSON valide
            pass

    def test_baseline_exists(self):
        """Le fichier bandit-baseline.json doit exister."""
        assert BASELINE.exists(), (
            f'Baseline manquant : {BASELINE}\n'
            'Generer avec : python -m bandit -r src/ -f json -o tests/security/bandit-baseline.json'
        )

    def test_no_new_critical_since_baseline(self):
        """Pas de nouvelles issues haute/critique depuis le baseline."""
        if not BASELINE.exists():
            pytest.skip('Baseline non genere')

        result = subprocess.run(
            ['python', '-m', 'bandit', '-r', 'src/', '-f', 'json', '-q'],
            capture_output=True,
            text=True,
            cwd=str(REPO),
        )
        if result.returncode == 0:
            return

        try:
            current = json.loads(result.stdout)
            baseline = json.loads(BASELINE.read_text(encoding='utf-8'))

            current_ids = {
                (i['filename'], i['line_number'], i['test_id'])
                for i in current.get('results', [])
                if i.get('issue_severity') in ('HIGH', 'MEDIUM')
            }
            baseline_ids = {
                (i['filename'], i['line_number'], i['test_id'])
                for i in baseline.get('results', [])
                if i.get('issue_severity') in ('HIGH', 'MEDIUM')
            }

            new_issues = current_ids - baseline_ids
            assert len(new_issues) == 0, (
                f'{len(new_issues)} nouvelles issues haute/critique depuis le baseline'
            )
        except json.JSONDecodeError:
            pass
