# Copyright 2026 Romy Alula — MIT License
"""Invariant : une seule boucle de comparaison de calibration.

Le script scripts/calibrate.py et la commande CLI partagent le meme moteur,
`laivelup.calibrate_core.run_calibration`. Ces tests verrouillent le fait que
le script n'evalue plus les profils lui-meme et rend les memes resultats.
"""

from __future__ import annotations

import inspect
import json
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent
SCRIPTS_DIR = REPO / 'scripts'
sys.path.insert(0, str(SCRIPTS_DIR))
sys.path.insert(0, str(REPO / 'src'))

import calibrate as script  # noqa: E402

from laivelup import calibrate_core  # noqa: E402

# Traces completes pour un profil BLUE (tous les axes decident)
_BLUE_TRACES = {
    'pr_sizes': ['M', 'M'],
    'context_versioned': True,
    'retries_after_fact': 0.4,
    'retries_triangulated': True,
    'parallel_projects': 1,
}

_RED_TRACES = {
    'pr_sizes': ['S'],
    'prompts': True,
    'retries_after_fact': 0.8,
    'retries_triangulated': True,
    'parallel_projects': 1,
}


def _profiles_dir(tmp_path: Path, names_traces: dict[str, dict]) -> Path:
    profiles_dir = tmp_path / 'profils'
    profiles_dir.mkdir()
    for name, traces in names_traces.items():
        (profiles_dir / f'{name}.json').write_text(
            json.dumps({'name': name, 'traces': traces}), encoding='utf-8'
        )
    return profiles_dir


def _expected(tmp_path: Path, levels: dict) -> Path:
    path = tmp_path / 'expected.json'
    path.write_text(json.dumps({'levels': levels}), encoding='utf-8')
    return path


# --- une seule boucle ------------------------------------------------------


class TestSingleComparisonLoop:
    def test_script_delegates_to_core_run_calibration(self):
        assert script.run_calibration is calibrate_core.run_calibration

    def test_calibrate_ne_construit_aucun_verdict(self):
        source = inspect.getsource(script.calibrate)
        assert 'evaluate(' not in source
        assert 'run_calibration(' in source

    def test_une_seule_evaluation_par_profil(self, tmp_path, monkeypatch):
        profiles_dir = _profiles_dir(tmp_path, {'p1': _BLUE_TRACES, 'p2': _RED_TRACES})
        expected = _expected(tmp_path, {'p1': 'BLUE', 'p2': 'BLUE'})
        monkeypatch.setattr(script, 'PROFILES_DIR', profiles_dir)

        core_calls = []
        script_calls = []
        real_core = calibrate_core.evaluate
        monkeypatch.setattr(
            calibrate_core, 'evaluate', lambda p: (core_calls.append(p), real_core(p))[1]
        )
        monkeypatch.setattr(script, 'evaluate', lambda p: (script_calls.append(p), real_core(p))[1])

        errors = script.calibrate(expected)

        assert errors == 1
        assert len(core_calls) == 2
        assert script_calls == []


# --- rendu identique au resultat structure ---------------------------------


class TestRenderingMatchesResult:
    def test_compteurs_issues_du_resultat(self, tmp_path, monkeypatch, capsys):
        profiles_dir = _profiles_dir(tmp_path, {'p1': _BLUE_TRACES, 'ko': _RED_TRACES})
        expected = _expected(tmp_path, {'p1': 'BLUE', 'ko': 'BLUE'})
        monkeypatch.setattr(script, 'PROFILES_DIR', profiles_dir)

        errors = script.calibrate(expected)
        out = capsys.readouterr().out

        result = calibrate_core.run_calibration(expected=expected, profiles_dir=profiles_dir)
        assert errors == result.errors
        assert f'{result.total} profils testes, {result.errors} erreurs' in out
        for row in result.rows:
            icon = '+' if row.status == 'OK' else 'X' if row.status == 'FAIL' else '-'
            assert f'  {icon} {row.name}: {row.detail}' in out

    def test_diff_utilise_le_verdict_de_la_ligne_sans_reevaluer(
        self, tmp_path, monkeypatch, capsys
    ):
        profiles_dir = _profiles_dir(tmp_path, {'p1': _BLUE_TRACES})
        expected = _expected(tmp_path, {'p1': 'BLUE'})
        monkeypatch.setattr(script, 'PROFILES_DIR', profiles_dir)

        real_core = calibrate_core.evaluate
        core_calls = []
        monkeypatch.setattr(
            calibrate_core, 'evaluate', lambda p: (core_calls.append(p), real_core(p))[1]
        )

        def _boom(_profile):
            raise AssertionError('le rendu --diff ne doit pas reevaluer le profil')

        monkeypatch.setattr(script, 'evaluate', _boom)

        script.calibrate(expected, diff=True)
        out = capsys.readouterr().out

        assert len(core_calls) == 1
        assert 'Taille' in out


# --- les verdicts sont portees par CalibrationRow --------------------------


class TestRowCarriesVerdict:
    def test_verdict_present_sur_chaque_ligne(self, tmp_path):
        profiles_dir = _profiles_dir(tmp_path, {'p1': _BLUE_TRACES, 'skip': {'pr_sizes': ['L']}})
        expected = _expected(tmp_path, {'p1': 'BLUE'})

        result = calibrate_core.run_calibration(expected=expected, profiles_dir=profiles_dir)

        assert result.total == 2
        assert all(r.verdict is not None for r in result.rows)
        assert {r.name: r.status for r in result.rows} == {'p1': 'OK', 'skip': 'SKIP'}

    def test_verdict_optionnel_ne_rompt_pas_le_dashboard(self, tmp_path):
        from laivelup.calibrate_dashboard import generate_calibrate_html

        profiles_dir = _profiles_dir(tmp_path, {'p1': _BLUE_TRACES})
        expected = _expected(tmp_path, {'p1': 'BLUE'})

        result = calibrate_core.run_calibration(expected=expected, profiles_dir=profiles_dir)
        html = generate_calibrate_html(result)

        assert '<!doctype html>' in html
        assert 'p1' in html


# --- expected.json n'est jamais un profil ----------------------------------


class TestExpectedExcludedFromProfiles:
    def test_run_custom_exclut_expected_json_du_glob(self, tmp_path):
        profiles_dir = _profiles_dir(tmp_path, {'p1': _BLUE_TRACES})
        (profiles_dir / 'expected.json').write_text(
            json.dumps({'levels': {'p1': 'BLUE'}}), encoding='utf-8'
        )
        autre = tmp_path / 'ailleurs' / 'reponses.json'
        autre.parent.mkdir()
        autre.write_text(json.dumps({'levels': {'p1': 'BLUE'}}), encoding='utf-8')

        result = calibrate_core.run_calibration(expected=autre, profiles_dir=profiles_dir)

        assert result.total == 1
        assert result.rows[0].name == 'p1'
