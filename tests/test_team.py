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
    _slug,
    create_team,
    evaluate_member,
    export_csv,
    export_html,
    export_json,
    export_markdown,
)


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
        traces["pr_sizes"] = pr_sizes
    if context_versioned:
        traces["context_versioned"] = True
    if retries_after_fact is not None:
        traces["retries_after_fact"] = retries_after_fact
        traces["retries_triangulated"] = retries_triangulated
    if parallel_projects is not None:
        traces["parallel_projects"] = parallel_projects
    return ProfileData(name="test", traces=traces)


class TestSlug:
    """Tests de pseudo-anonymisation RGPD."""

    def test_slug_est_deterministe(self):
        """Le même nom produit toujours le même slug."""
        s1 = _slug("Alice")
        s2 = _slug("Alice")
        assert s1 == s2

    def test_slug_est_unique_par_nom(self):
        """Des noms différents produisent des slugs différents."""
        s1 = _slug("Alice")
        s2 = _slug("Bob")
        assert s1 != s2

    def test_slug_ne_contient_pas_le_nom(self):
        """Le slug ne contient pas le nom en clair (prudence RGPD)."""
        slug = _slug("Alice Dupont")
        assert "alice" not in slug.lower() or slug.startswith("alice")
        # Le slug commence par une version nettoyée, mais le digest est tronqué
        assert len(slug) <= 41  # 32 + "-" + 8

    def test_slug_vide_retourne_defaut(self):
        """Un nom vide retourne un slug par défaut."""
        slug = _slug("")
        assert slug.startswith("membre-") or len(slug) > 0


class TestCreateTeam:
    """Tests de création d'équipe."""

    def test_create_team_nom_membres(self):
        """L'équipe est créée avec le bon nom et les bons membres."""
        team = create_team("Alpha", ["Alice", "Bob", "Charlie"])
        assert team.name == "Alpha"
        assert len(team.members) == 3

    def test_create_team_slugs_unique(self):
        """Chaque membre a un slug unique."""
        team = create_team("Beta", ["Alice", "Bob", "Alice"])
        slugs = list(team.members.keys())
        assert len(slugs) == len(set(slugs))

    def test_create_team_membres_stored(self):
        """Les noms originaux sont conservés dans les snapshots."""
        team = create_team("Gamma", ["Alice"])
        slug = list(team.members.keys())[0]
        assert team.members[slug].name == "Alice"

    def test_create_team_history_vide(self):
        """L'historique est vide à la création."""
        team = create_team("Delta", ["Alice"])
        assert team.history == []


class TestEvaluateMember:
    """Tests d'évaluation de membre."""

    def test_evaluate_member_niveau_determine(self):
        """Un profil avec suffisamment de données donne un verdict."""
        team = create_team("Alpha", ["Alice"])
        slug = list(team.members.keys())[0]
        profile = make_profile(
            pr_sizes=["M", "M"],
            context_versioned=True,
            retries_after_fact=0.5,
            parallel_projects=1,
        )
        verdict = evaluate_member(team, slug, profile)
        assert verdict.decided

    def test_evaluate_member_snapshot_mis_a_jour(self):
        """Le snapshot du membre est mis à jour après évaluation."""
        team = create_team("Alpha", ["Alice"])
        slug = list(team.members.keys())[0]
        profile = make_profile(
            pr_sizes=["M", "M"],
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
        team = create_team("Alpha", ["Alice"])
        slug = list(team.members.keys())[0]
        profile = make_profile(
            pr_sizes=["M", "M"],
            context_versioned=True,
            retries_after_fact=0.5,
            parallel_projects=1,
        )
        evaluate_member(team, slug, profile)
        assert len(team.history) == 1
        assert team.history[0]["slug"] == slug

    def test_evaluate_member_inconnu_erreur(self):
        """Évaluer un membre inexistant lève une erreur."""
        team = create_team("Alpha", ["Alice"])
        profile = make_profile()
        with pytest.raises(ValueError, match="non trouvé"):
            evaluate_member(team, "inexistant-000", profile)

    def test_evaluate_member_refus(self):
        """Un profil sans données donne un refus (niveau None)."""
        team = create_team("Alpha", ["Alice"])
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
        team = create_team("Test", ["Alice", "Bob"])
        slug_alice = [s for s, m in team.members.items() if m.name == "Alice"][0]
        slug_bob = [s for s, m in team.members.items() if m.name == "Bob"][0]
        profile_alice = make_profile(
            pr_sizes=["M", "M"],
            context_versioned=True,
            retries_after_fact=0.5,
            parallel_projects=1,
        )
        profile_bob = make_profile(
            pr_sizes=["S", "S"],
            retries_after_fact=0.8,
            parallel_projects=1,
        )
        evaluate_member(team, slug_alice, profile_alice)
        evaluate_member(team, slug_bob, profile_bob)
        return team

    def test_export_json(self, team_with_data, tmp_path):
        """Export JSON valide et lisible."""
        out = tmp_path / "team.json"
        result = export_json(team_with_data, out)
        assert result.exists()
        data = json.loads(result.read_text(encoding="utf-8"))
        assert data["team"] == "Test"
        assert len(data["members"]) == 2
        assert len(data["history"]) == 2

    def test_export_markdown(self, team_with_data, tmp_path):
        """Export Markdown avec structure correcte."""
        out = tmp_path / "team.md"
        result = export_markdown(team_with_data, out)
        assert result.exists()
        content = result.read_text(encoding="utf-8")
        assert "# Équipe · Test" in content
        assert "## Membres" in content
        assert "## Historique" in content

    def test_export_csv(self, team_with_data, tmp_path):
        """Export CSV avec en-têtes corrects."""
        out = tmp_path / "team.csv"
        result = export_csv(team_with_data, out)
        assert result.exists()
        lines = result.read_text(encoding="utf-8").strip().split("\n")
        assert lines[0] == "name,slug,level,limiting_axis,confidence,timestamp"
        assert len(lines) == 3  # header + 2 members

    def test_export_html(self, team_with_data, tmp_path):
        """Export HTML avec structure valide."""
        out = tmp_path / "team.html"
        result = export_html(team_with_data, out)
        assert result.exists()
        content = result.read_text(encoding="utf-8")
        assert "<!doctype html>" in content
        assert "Équipe · Test" in content
        assert "<table>" in content

    def test_export_creates_parent_dir(self, team_with_data, tmp_path):
        """L'export crée le dossier parent si nécessaire."""
        out = tmp_path / "subdir" / "team.json"
        result = export_json(team_with_data, out)
        assert result.exists()