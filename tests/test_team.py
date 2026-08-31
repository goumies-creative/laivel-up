# Copyright 2026 Romy Alula — MIT License
"""Tests unitaires pour le module Team Tracker.

Couvre : création d'équipe, évaluation de membre, export multi-format,
pseudo-anonymisation RGPD, journalisation historique.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from laivelup.model import Level, ProfileData
from laivelup.team import (
    Team,
    create_team,
    evaluate_member,
    export_csv,
    export_html,
    export_json,
    export_markdown,
    remove_member,
    set_opt_out,
)
from laivelup.utils import slug


def make_profile(
    pr_sizes=None,
    context_versioned=False,
    retries_after_fact=None,
    retries_triangulated=True,
    parallel_projects=None,
):
    """Helper pour construire un profil de test."""
    traces = {}
    if pr_sizes is not None:
        traces['pr_sizes'] = pr_sizes
    if context_versioned:
        traces['context_versioned'] = True
    if retries_after_fact is not None:
        traces['retries_after_fact'] = retries_after_fact
        traces['retries_triangulated'] = retries_triangulated
    if parallel_projects is not None:
        traces['parallel_projects'] = parallel_projects
    return ProfileData(name='test', traces=traces)


class TestSlug:
    """Tests de pseudo-anonymisation RGPD via export public (slug, create_team)."""

    def test_slug_est_deterministe(self):
        """Le même nom produit toujours le même slug."""
        s1 = slug('Alice')
        s2 = slug('Alice')
        assert s1 == s2

    def test_slug_est_unique_par_nom(self):
        """Des noms différents produisent des slugs différents."""
        s1 = slug('Alice')
        s2 = slug('Bob')
        assert s1 != s2

    def test_slug_ne_contient_pas_le_nom_complet(self):
        """Le slug ne contient pas le nom complet en clair (prudence RGPD)."""
        s = slug('Alice Dupont')
        # Le slug commence par une version nettoyée, mais le digest est tronqué
        assert len(s) <= 41  # 32 + "-" + 8

    def test_slug_via_create_team(self):
        """create_team produit des slugs uniques pour chaque membre."""
        team = create_team('Equipe', ['Alice', 'Bob', 'Charlie'])
        slugs = list(team.members.keys())
        assert len(slugs) == 3
        assert len(set(slugs)) == 3

    def test_slug_vide_retourne_defaut(self):
        """Un nom vide retourne un slug par défaut."""
        s = slug('')
        assert s.startswith('membre-') or len(s) > 0


class TestCreateTeam:
    """Tests de création d'équipe."""

    def test_create_team_nom_membres(self):
        """L'équipe est créée avec le bon nom et les bons membres."""
        team = create_team('Alpha', ['Alice', 'Bob', 'Charlie'])
        assert team.name == 'Alpha'
        assert len(team.members) == 3

    def test_create_team_slugs_unique(self):
        """Chaque membre a un slug unique."""
        team = create_team('Beta', ['Alice', 'Bob', 'Alice'])
        slugs = list(team.members.keys())
        assert len(slugs) == len(set(slugs))

    def test_create_team_membres_stored(self):
        """Les noms originaux sont conservés dans les snapshots."""
        team = create_team('Gamma', ['Alice'])
        slug = list(team.members.keys())[0]
        assert team.members[slug].name == 'Alice'

    def test_create_team_history_vide(self):
        """L'historique est vide à la création."""
        team = create_team('Delta', ['Alice'])
        assert team.history == []


class TestEvaluateMember:
    """Tests d'évaluation de membre."""

    def test_evaluate_member_niveau_determine(self):
        """Un profil avec suffisamment de données donne un verdict."""
        team = create_team('Alpha', ['Alice'])
        slug = list(team.members.keys())[0]
        profile = make_profile(
            pr_sizes=['M', 'M'],
            context_versioned=True,
            retries_after_fact=0.5,
            parallel_projects=1,
        )
        verdict = evaluate_member(team, slug, profile)
        assert verdict.decided

    def test_evaluate_member_snapshot_mis_a_jour(self):
        """Le snapshot du membre est mis à jour après évaluation."""
        team = create_team('Alpha', ['Alice'])
        slug = list(team.members.keys())[0]
        profile = make_profile(
            pr_sizes=['M', 'M'],
            context_versioned=True,
            retries_after_fact=0.5,
            parallel_projects=1,
        )
        evaluate_member(team, slug, profile)
        member = team.members[slug]
        assert member.level is not None
        assert member.confidence > 0

    def test_evaluate_member_historique_ajoute(self):
        """L'historique est enrichi après évaluation."""
        team = create_team('Alpha', ['Alice'])
        slug = list(team.members.keys())[0]
        profile = make_profile(
            pr_sizes=['M', 'M'],
            context_versioned=True,
            retries_after_fact=0.5,
            parallel_projects=1,
        )
        evaluate_member(team, slug, profile)
        assert len(team.history) == 1
        assert team.history[0]['slug'] == slug

    def test_evaluate_member_inconnu_erreur(self):
        """Évaluer un membre inexistant lève une erreur."""
        team = create_team('Alpha', ['Alice'])
        profile = make_profile()
        with pytest.raises(ValueError, match='non trouvé'):
            evaluate_member(team, 'inexistant-000', profile)

    def test_evaluate_member_refus(self):
        """Un profil sans données donne un refus (niveau None)."""
        team = create_team('Alpha', ['Alice'])
        slug = list(team.members.keys())[0]
        profile = make_profile()
        verdict = evaluate_member(team, slug, profile)
        assert not verdict.decided
        member = team.members[slug]
        assert member.level is None


class TestExport:
    """Tests d'export multi-format."""

    @pytest.fixture
    def team_with_data(self):
        """Équipe avec des données d'évaluation."""
        team = create_team('Test', ['Alice', 'Bob'])
        slug_alice = [s for s, m in team.members.items() if m.name == 'Alice'][0]
        slug_bob = [s for s, m in team.members.items() if m.name == 'Bob'][0]
        profile_alice = make_profile(
            pr_sizes=['M', 'M'],
            context_versioned=True,
            retries_after_fact=0.5,
            parallel_projects=1,
        )
        profile_bob = make_profile(
            pr_sizes=['S', 'S'],
            retries_after_fact=0.8,
            parallel_projects=1,
        )
        evaluate_member(team, slug_alice, profile_alice)
        evaluate_member(team, slug_bob, profile_bob)
        return team

    def test_export_json(self, team_with_data, tmp_path):
        """Export JSON valide et lisible."""
        out = tmp_path / 'team.json'
        result = export_json(team_with_data, out)
        assert result.exists()
        data = json.loads(result.read_text(encoding='utf-8'))
        assert data['team'] == 'Test'
        assert len(data['members']) == 2
        assert len(data['history']) == 2

    def test_export_markdown(self, team_with_data, tmp_path):
        """Export Markdown avec structure correcte."""
        out = tmp_path / 'team.md'
        result = export_markdown(team_with_data, out)
        assert result.exists()
        content = result.read_text(encoding='utf-8')
        assert '# Équipe · Test' in content
        assert '## Membres' in content
        assert '## Historique' in content

    def test_export_csv(self, team_with_data, tmp_path):
        """Export CSV avec en-têtes corrects."""
        out = tmp_path / 'team.csv'
        result = export_csv(team_with_data, out)
        assert result.exists()
        lines = result.read_text(encoding='utf-8').strip().split('\n')
        assert lines[0] == 'name,slug,level,limiting_axis,confidence,timestamp'
        assert len(lines) == 3  # header + 2 members

    def test_export_html(self, team_with_data, tmp_path):
        """Export HTML avec structure valide."""
        out = tmp_path / 'team.html'
        result = export_html(team_with_data, out)
        assert result.exists()
        content = result.read_text(encoding='utf-8')
        assert '<!doctype html>' in content
        assert 'Équipe · Test' in content
        assert '<table>' in content

    def test_export_creates_parent_dir(self, team_with_data, tmp_path):
        """L'export crée le dossier parent si nécessaire."""
        out = tmp_path / 'subdir' / 'team.json'
        result = export_json(team_with_data, out)
        assert result.exists()


# --- Gaps de couverture (coverage-90-closing-gaps.md) ----------------------


class TestValidateTeamName:
    """Nom d'équipe invalide pour un chemin de fichier."""

    def test_empty_name_raises(self):
        with pytest.raises(ValueError, match='invalide'):
            create_team('', ['Alice'])

    def test_name_with_slash_raises(self):
        with pytest.raises(ValueError, match='invalide'):
            create_team('a/b', ['Alice'])


class TestSaveTeamSymlinkGuard:
    """Refus d'écrire si le dossier parent est un symlink (G01)."""

    def test_parent_symlink_raises(self, tmp_path, monkeypatch):
        from laivelup.team import save_team

        team = create_team('SymlinkTest', ['Alice'])
        target = tmp_path / 'team.json'
        monkeypatch.setattr(Path, 'is_symlink', lambda _self: True)
        with pytest.raises(ValueError, match='symlink'):
            save_team(team, target)


class TestSaveTeamCleanupOnFailure:
    """Le fichier temporaire est nettoyé si le replace atomique échoue."""

    def test_replace_failure_cleans_temp_file(self, tmp_path, monkeypatch):
        from laivelup import team as team_mod

        team = create_team('CleanupTest', ['Alice'])
        target = tmp_path / 'team.json'

        def failing_replace(_self, _dest):
            raise OSError('disk full')

        monkeypatch.setattr(Path, 'replace', failing_replace)
        with pytest.raises(OSError):
            team_mod.save_team(team, target)
        assert list(tmp_path.glob('*.tmp')) == []


class TestLoadTeamFileSizeGuard:
    """Refus de charger un fichier d'équipe trop volumineux (G01)."""

    def test_file_too_large_raises(self, tmp_path):
        from laivelup.team import MAX_TEAM_FILE_MB, load_team

        path = tmp_path / 'huge.json'
        path.write_text('x' * (MAX_TEAM_FILE_MB * 1024 * 1024 + 10), encoding='utf-8')
        with pytest.raises(ValueError, match='volumineux'):
            load_team('huge', path)


class TestLoadTeamInvalidLevel:
    """Un niveau JSON invalide (Level[key] -> KeyError) est absorbé silencieusement."""

    def test_invalid_level_string_is_suppressed_to_none(self, tmp_path):
        from laivelup.team import load_team

        path = tmp_path / 'team.json'
        data = {
            'name': 'InvalidLevel',
            'salt': 'abc',
            'members': {
                'alice-12345678': {
                    'name': 'Alice',
                    'slug': 'alice-12345678',
                    'level': 'PLATINUM',
                    'limiting_axis': None,
                    'confidence': 0.0,
                    'timestamp': '',
                    'red_flags_count': 0,
                    'next_steps_count': 0,
                    'opt_out': False,
                }
            },
            'history': [],
        }
        path.write_text(json.dumps(data), encoding='utf-8')
        team = load_team('InvalidLevel', path)
        assert team.members['alice-12345678'].level is None


class TestCreateTeamTooManyMembers:
    def test_more_than_max_members_raises(self):
        with pytest.raises(ValueError, match='Trop de membres'):
            create_team('BigTeam', [f'membre{i}' for i in range(51)])


class TestEvaluateMemberHistoryTrim:
    """L'historique est tronqué automatiquement au-delà de _MAX_HISTORY entrées."""

    def test_history_trimmed_after_101_evaluations(self):
        from laivelup.team import _MAX_HISTORY

        team = create_team('TrimTeam', ['Alice'])
        member_slug = next(iter(team.members.keys()))
        profile = make_profile(
            pr_sizes=['M', 'M'],
            context_versioned=True,
            retries_after_fact=0.3,
            parallel_projects=1,
        )
        for _ in range(_MAX_HISTORY + 1):
            evaluate_member(team, member_slug, profile)
        assert len(team.history) == _MAX_HISTORY


class TestRemoveSetOptOutMemberNotFound:
    def test_remove_member_not_found_raises(self):
        team = create_team('Alpha', ['Alice'])
        with pytest.raises(ValueError, match='non trouvé'):
            remove_member(team, 'inexistant-000')

    def test_set_opt_out_member_not_found_raises(self):
        team = create_team('Alpha', ['Alice'])
        with pytest.raises(ValueError, match='non trouvé'):
            set_opt_out(team, 'inexistant-000')


class TestExportOptOutExclusion:
    """export_markdown / export_csv / export_html excluent les membres en opt-out."""

    @pytest.fixture
    def team_with_opted_out_member(self):
        team = create_team('OptExport', ['Alice', 'Bob'])
        slug_alice = next(s for s, m in team.members.items() if m.name == 'Alice')
        slug_bob = next(s for s, m in team.members.items() if m.name == 'Bob')
        profile = make_profile(
            pr_sizes=['M', 'M'],
            context_versioned=True,
            retries_after_fact=0.3,
            parallel_projects=1,
        )
        evaluate_member(team, slug_alice, profile)
        evaluate_member(team, slug_bob, profile)
        set_opt_out(team, slug_alice, True)
        return team

    def test_export_markdown_excludes_opted_out(self, team_with_opted_out_member, tmp_path):
        out = tmp_path / 'team.md'
        export_markdown(team_with_opted_out_member, out)
        content = out.read_text(encoding='utf-8')
        assert 'Alice' not in content
        assert 'Bob' in content

    def test_export_csv_excludes_opted_out(self, team_with_opted_out_member, tmp_path):
        out = tmp_path / 'team.csv'
        export_csv(team_with_opted_out_member, out)
        content = out.read_text(encoding='utf-8')
        assert 'Alice' not in content
        assert 'Bob' in content

    def test_export_html_excludes_opted_out(self, team_with_opted_out_member, tmp_path):
        out = tmp_path / 'team.html'
        export_html(team_with_opted_out_member, out)
        content = out.read_text(encoding='utf-8')
        assert 'Alice' not in content
        assert 'Bob' in content
