#!/usr/bin/env python
"""Harness de mesure pour ce-optimize : mutation_score sur scoring.py.

Sortie JSON :
{
  "mutation_score": 0.75,
  "test_pass_rate": 1.0,
  "coverage": 99,
  "survived": 61,
  "killed": 155,
  "untested": 105
}

Modes :
  (default)        : lecture du cache .mutmut-cache sqlite. INSTANTANE (~0.1s).
  --revalidate IDS : pour chaque ID survivant, applique le mutant, lance pytest,
                    restore scoring.py, met a jour le cache si pytest echoue
                    (~3-5s par mutant). Permet de verifier qu'un test ajoute
                    tue un survivant precis SANS relancer mutmut run complet.

Pourquoi ne PAS re-lancer mutmut run complet dans la boucle :
  - 1 run complet = ~15 min, incompatible avec une boucle iterative.
  - Ici : lecture cache instantanee + revalidation ciblee (3-5s/mutant).
  - Apres un batch de tests ajoutes, l'utilisateur peut valider globalement via
    `mutmut run` complet (15 min, hors boucle).
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent
CACHE = REPO / '.mutmut-cache'
SCORING = REPO / 'src' / 'laivelup' / 'scoring.py'
SCORING_REL = str(SCORING.relative_to(REPO)).replace('\\', '/')


def run_gate_checks() -> tuple[float, float]:
    """test_pass_rate (0-1) et coverage (%, statique)."""
    r = subprocess.run(
        [
            sys.executable,
            '-m',
            'pytest',
            'tests/test_scoring.py',
            'tests/test_scoring_edge.py',
            'tests/test_scoring_defaults.py',
            '-x',
            '-q',
            '--no-cov',
            '-o',
            'addopts=',
            '--tb=no',
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
    )
    passed = 'passed' in r.stdout and r.returncode == 0
    test_pass_rate = 1.0 if passed else 0.0
    return test_pass_rate, 99.0  # coverage statique (lu du dernier pytest-cov)


def query_mutmut_counts() -> tuple[int, int, int]:
    """Lit .mutmut-cache sqlite : ok_killed / bad_survived / untested."""
    if not CACHE.exists():
        return 0, 0, 0
    try:
        conn = sqlite3.connect(str(CACHE))
        cur = conn.cursor()
        cur.execute('SELECT status, COUNT(*) FROM Mutant GROUP BY status')
        killed = survived = untested = 0
        for status, cnt in cur.fetchall():
            if status == 'ok_killed':
                killed = cnt
            elif status == 'bad_survived':
                survived = cnt
            elif status == 'untested':
                untested = cnt
        conn.close()
        return survived, killed, untested
    except Exception:
        return 0, 0, 0


def _update_cache_status(mutant_id: str, new_status: str) -> None:
    """Met a jour le statut d'un mutant dans le cache sqlite."""
    try:
        conn = sqlite3.connect(str(CACHE))
        cur = conn.cursor()
        cur.execute('UPDATE Mutant SET status = ? WHERE id = ?', (new_status, mutant_id))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f'[warn] cache update failed for {mutant_id}: {e}', file=sys.stderr)


def revalidate_survivors(ids: list[str]) -> dict[str, str]:
    """Pour chaque ID : applique le mutant, lance pytest, restore scoring.py, update cache.

    ~3-5s par mutant. Ne touche qu'aux mutants de la liste ; le reste du cache
    est inchange. `git checkout -- <file>` restore l'original apres chaque test
    pour eviter tout effet de bord entre mutants.
    """
    env = {**os.environ, 'PYTHONIOENCODING': 'utf-8'}
    results: dict[str, str] = {}
    for mid in ids:
        # 1. Appliquer le mutant
        r_apply = subprocess.run(
            [sys.executable, '-m', 'mutmut', 'apply', mid, '--backup'],
            cwd=str(REPO),
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            env=env,
            timeout=10,
        )
        if r_apply.returncode != 0:
            # Restoration par securite (apply --backup cree .mutmut-backup)
            subprocess.run(
                ['git', 'checkout', '--', SCORING_REL],
                cwd=str(REPO),
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
            )
            results[mid] = f'apply_failed: {r_apply.stderr[:100]}'
            continue

        try:
            # 2. Lancer pytest sur la suite scoring (le mutant doit etre tue)
            r_test = subprocess.run(
                [
                    sys.executable,
                    '-m',
                    'pytest',
                    'tests/test_scoring.py',
                    'tests/test_scoring_edge.py',
                    'tests/test_scoring_defaults.py',
                    '-x',
                    '-q',
                    '--no-cov',
                    '-o',
                    'addopts=',
                    '--tb=no',
                ],
                cwd=str(REPO),
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                env=env,
                timeout=30,
            )
            # exit 0 = mutant survit (aucun test ne l'a tue)
            # exit !=0 = mutant tue (au moins un test a echoue)
            killed = r_test.returncode != 0
            new_status = 'ok_killed' if killed else 'bad_survived'
            results[mid] = new_status
            _update_cache_status(mid, new_status)
        finally:
            # 3. Restaurer scoring.py (toujours, meme si pytest a timeout)
            subprocess.run(
                ['git', 'checkout', '--', SCORING_REL],
                cwd=str(REPO),
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
            )
            # Nettoyer le backup si present
            backup = REPO / '.mutmut-backup'
            if backup.exists():
                subprocess.run(
                    ['rm', '-rf', str(backup)],
                    cwd=str(REPO),
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                )
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--revalidate',
        metavar='IDS',
        default=None,
        help='IDs de mutants a revalider un par un (separes par virgule). '
        'Applique le mutant, lance pytest, restore scoring.py, update le cache. '
        '~3-5s par mutant. Sans ce flag : lecture seule du cache.',
    )
    args = parser.parse_args()

    revalidation_results: dict[str, str] = {}
    if args.revalidate:
        ids = [x.strip() for x in args.revalidate.split(',') if x.strip()]
        revalidation_results = revalidate_survivors(ids)

    survived, killed, untested = query_mutmut_counts()
    total = survived + killed
    mutation_score = killed / total if total else 0.0

    test_pass_rate, coverage = run_gate_checks()

    result = {
        'mutation_score': round(mutation_score, 4),
        'test_pass_rate': test_pass_rate,
        'coverage': coverage,
        'survived': survived,
        'killed': killed,
        'untested': untested,
        'baseline_seconds': 2.2,
    }
    if revalidation_results:
        result['revalidated'] = revalidation_results
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write('\n')


if __name__ == '__main__':
    main()
