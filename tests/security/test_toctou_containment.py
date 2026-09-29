# Copyright 2026 Romy Alula — MIT License
"""Containment anti-TOCTOU de save_team().

Chaque test introduit délibérément la violation interdite et vérifie que
l'écriture est refusée, plutôt que de constater qu'un cas nominal passe.
Un test qui ne peut pas construire la violation (privilèges absents) est marqué
comme non applicable : on ne veut pas un test vert parce qu'il n'a rien fait.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from laivelup.team import MemberSnapshot, Team, create_team, save_team


def _can_make(kind: str) -> bool:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        real = root / 'real'
        real.mkdir()
        if kind == 'symlink':
            try:
                (root / 'link').symlink_to(real, target_is_directory=True)
            except (OSError, NotImplementedError):
                return False
            return True
        return (
            sys.platform == 'win32'
            and subprocess.run(
                ['cmd', '/c', 'mklink', '/J', str(root / 'link'), str(real)], capture_output=True
            ).returncode
            == 0
        )


KINDS = [k for k in ('symlink', 'junction') if _can_make(k)]


def _make_link(kind: str, link: Path, real: Path) -> None:
    if kind == 'symlink':
        link.symlink_to(real, target_is_directory=True)
        return
    proc = subprocess.run(['cmd', '/c', 'mklink', '/J', str(link), str(real)], capture_output=True)
    assert proc.returncode == 0, proc.stderr.decode('utf-8', 'replace')


def _team(name: str = 'alpha') -> Team:
    return create_team(name, ['Alice', 'Bob'])


def _listing(directory: Path) -> list[str]:
    """Noms réels du dossier — `Path.glob` ignore les points sur Python < 3.13."""
    return sorted(p.name for p in directory.iterdir())


@pytest.mark.skipif(not KINDS, reason='aucun type de lien constructible dans cet environnement')
@pytest.mark.parametrize('kind', KINDS)
def test_ground_truth_the_link_really_redirects_writes(tmp_path: Path, kind: str) -> None:
    """Le lien construit redirige vraiment les écritures.

    Sans ce garde-fou, un test de violation pourrait passer au vert sans jamais
    commettre la violation : on vérifie donc la redirection elle-même, avant
    d'appeler le code sous test.
    """
    outside = tmp_path / 'outside'
    outside.mkdir()
    (outside / 'canary').write_text('preuve', encoding='utf-8')
    link = tmp_path / 'link'
    _make_link(kind, link, outside)

    assert link.is_dir()
    assert (link / 'canary').read_text(encoding='utf-8') == 'preuve', 'la violation est bien réelle'
    assert link.resolve() != tmp_path.resolve()


@pytest.mark.skipif(not KINDS, reason='aucun type de lien constructible dans cet environnement')
@pytest.mark.parametrize('kind', KINDS)
def test_write_through_linked_directory_is_refused(tmp_path: Path, kind: str) -> None:
    """Écrire dans un répertoire joignable par un lien est refusé."""
    outside = tmp_path / 'outside'
    outside.mkdir()
    link = tmp_path / 'link'
    _make_link(kind, link, outside)

    with pytest.raises(ValueError, match=r'symlink|jonction'):
        save_team(_team(), link / 'alpha.json')

    assert not (outside / 'alpha.json').exists(), "l'écriture a échappé au répertoire contrôlé"


@pytest.mark.skipif('junction' not in KINDS, reason='jonction non constructible ici')
def test_junction_is_rejected_even_though_pathlib_does_not_see_it(tmp_path: Path) -> None:
    """Une jonction n'est pas un symlink pour pathlib : le garde doit la voir quand même.

    C'est précisément le trou du contrôle d'origine sur Windows, où
    `Path.is_symlink()` répond False sur une jonction alors que le chemin
    redirige ailleurs.
    """
    outside = tmp_path / 'outside'
    outside.mkdir()
    link = tmp_path / 'junction'
    _make_link('junction', link, outside)
    assert link.is_symlink() is False, 'précondition du test cassée : plus de jonction'

    with pytest.raises(ValueError, match=r'symlink|jonction'):
        save_team(_team(), link / 'alpha.json')
    assert not (outside / 'alpha.json').exists()


@pytest.mark.skipif(not KINDS, reason='aucun type de lien constructible dans cet environnement')
@pytest.mark.parametrize('kind', KINDS)
def test_linked_ancestor_is_refused_not_only_the_final_component(tmp_path: Path, kind: str) -> None:
    """Un lien dans les ancêtres suffit à détourner l'écriture.

    Le contrôle d'origine ne regardait que le composant final : un répertoire
    parent accessible par un lien passait.
    """
    outside = tmp_path / 'outside'
    outside.mkdir()
    link = tmp_path / 'link'
    _make_link(kind, link, outside)
    deep = link / 'nested' / 'deeper'

    with pytest.raises(ValueError, match=r'symlink|jonction'):
        save_team(_team(), deep / 'alpha.json')

    assert not (outside / 'nested' / 'deeper' / 'alpha.json').exists()


@pytest.mark.skipif('symlink' not in KINDS, reason='création de symlink interdite ici')
def test_broken_link_parent_is_not_short_circuited_by_exists(tmp_path: Path) -> None:
    """Un lien cassé ne doit pas contourner le contrôle via `exists()`.

    `Path.exists()` suit les liens : un lien dont la cible a disparu répond
    False et court-circuitait `is_symlink()` dans le contrôle d'origine.
    """
    link = tmp_path / 'link'
    link.symlink_to(tmp_path / 'cible-absente', target_is_directory=True)
    assert link.exists() is False, 'précondition du test cassée'

    with pytest.raises(ValueError, match=r'symlink|jonction'):
        save_team(_team(), link / 'alpha.json')


@pytest.mark.skipif(not KINDS, reason='aucun type de lien constructible dans cet environnement')
@pytest.mark.parametrize('kind', KINDS)
def test_directory_replaced_between_check_and_write_is_refused(
    tmp_path: Path, kind: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Le répertoire échangé après le contrôle fait échouer l'écriture.

    C'est la course elle-même : le contrôle d'origine portait sur un chemin,
    l'écriture arrivait plusieurs lignes après sur ce même chemin. Ici on force
    l'échange au moment précis où cette fenêtre s'ouvrait, et on vérifie que le
    fichier final n'atterrit jamais hors du répertoire contrôlé.
    """
    import laivelup.team as team_mod

    parent = tmp_path / 'teams'
    original = team_mod._first_link
    attacker = tmp_path / 'attacker'
    calls = {'n': 0}

    def swap_after_check(path: Path) -> Path | None:
        found = original(path)
        calls['n'] += 1
        if calls['n'] == 1:
            attacker.mkdir()
            for child in list(parent.iterdir()):
                child.replace(attacker / child.name)
            parent.rmdir()
            _make_link(kind, parent, attacker)
        return found

    monkeypatch.setattr(team_mod, '_first_link', swap_after_check)

    with pytest.raises(ValueError, match=r'confinement|symlink|jonction'):
        save_team(_team(), parent / 'alpha.json')

    assert not (attacker / 'alpha.json').exists(), "l'écriture a échappé au répertoire contrôlé"
    assert _listing(attacker) == [], 'un temporaire a survécu dans le répertoire détourné'


def test_no_temporary_file_survives_a_failed_serialisation(tmp_path: Path) -> None:
    """Une exception pendant json.dump() ne laisse pas de .tmp sur le disque.

    Avec `delete=False`, le `with` se ferme avant que le `try/except` ne soit
    atteint : le temporaire restait.
    """

    class Unserialisable:
        def __repr__(self) -> str:
            raise RuntimeError('boom')

    team = Team(name='alpha')
    team.members['x'] = MemberSnapshot(
        slug='x', name='x', level=None, limiting_axis=None, confidence=0.0
    )
    team.history.append({'when': Unserialisable()})

    target = tmp_path / 'teams' / 'alpha.json'
    with pytest.raises(Exception):  # noqa: B017 — la règle testée est le nettoyage, pas le type
        save_team(team, target)

    assert _listing(target.parent) == []


def test_successful_write_still_produces_readable_json(tmp_path: Path) -> None:
    """Le cas nominal reste intact après le durcissement."""
    team = create_team('alpha', ['Alice', 'Bob'])
    target = save_team(team, tmp_path / 'teams' / 'alpha.json')

    data = json.loads(target.read_text(encoding='utf-8'))
    assert data['name'] == 'alpha'
    assert len(data['members']) == 2
    assert _listing(target.parent) == [target.name]
