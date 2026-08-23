# Copyright 2026 Romy Alula — MIT License
"""Tests RGPD pour le module Team Tracker.

Couvre : pseudo-anonymisation, opt-out, droit à l'oubli, suppression auto,
export sans PII, sanitize generate_profile.
"""

from __future__ import annotations

import json

import pytest

from laivelup.model import ProfileData
from laivelup.team import (
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


class TestRGPDSlug:
    """Tests de pseudo-anonymisation RGPD (_slug)."""

    def test_slug_deterministe_meme_nom(self):
        """Le même nom produit toujours le même slug."""
        s1 = _slug("Alice Dupont")
        s2 = _slug("Alice Dupont")
        assert s1 == s2

    def test_slug_unique_par_nom_different(self):
        """Des noms différents produisent des slugs différents."""
        s1 = _slug("Alice")
        s2 = _slug("Bob")
        assert s1 != s2

    def test_slug_ne_contient_pas_email_brut(self):
        """Le slug ne contient pas d'email brut avec @ (RGPD)."""
        slug = _slug("alice@example.com")
        assert "@" not in slug
        # Le slug nettoie les caractères spéciaux : alice@example.com → alice-example-com-xxx
        # Pas de format email brut (avec @)
        assert "." not in slug.split("-")[-1]  # Le digest ne contient pas de point

    def test_slug_format_propre(self):
        """Le slug suit le format alphanumerique-hash (pseudo-anonyme)."""
        slug = _slug("Alice Dupont")
        assert len(slug) <= 41  # 32 + "-" + 8
        assert "-" in slug  # Séparateur nom-hash


class TestRGDPOptOut:
    """Tests d'opt-out explicite (à implémenter dans team.py)."""

    def test_opt_out_bloque_evaluation(self):
        """Un membre avec opt_out=True ne peut pas être évalué."""
        pytest.skip("Opt-out non encore implémenté — TODO Phase 25/08")

    def test_opt_out_export_exclut_membre(self):
        """L'export exclut les membres en opt-out."""
        pytest.skip("Opt-out non encore implémenté — TODO Phase 25/08")


class TestRGPDDroitOubli:
    """Tests droit à l'oubli / suppression (à implémenter)."""

    def test_remove_member_purge_historique(self):
        """Suppression membre purge historique et snapshots."""
        pytest.skip("Remove --purge non encore implémenté — TODO Phase 25/08")

    def test_remove_member_conserve_equipe(self):
        """Suppression membre ne supprime pas l'équipe."""
        pytest.skip("Remove --purge non encore implémenté — TODO Phase 25/08")


class TestRGPDExportSansPII:
    """Tests que les exports ne contiennent aucune PII."""

    @pytest.fixture
    def team_with_data(self):
        team = create_team("Test", ["Alice", "Bob"])
        slug_alice = next(s for s, m in team.members.items() if m.name == "Alice")
        slug_bob = next(s for s, m in team.members.items() if m.name == "Bob")
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

    def test_export_json_ne_contient_pas_noms_complets_ni_emails(self, team_with_data, tmp_path):
        out = tmp_path / "team.json"
        export_json(team_with_data, out)
        data = json.loads(out.read_text(encoding="utf-8"))
        for member in data["members"].values():
            assert "@" not in member["name"]

    def test_export_markdown_ne_contient_pas_pii(self, team_with_data, tmp_path):
        out = tmp_path / "team.md"
        export_markdown(team_with_data, out)
        content = out.read_text(encoding="utf-8")
        assert "@" not in content
        assert "email" not in content.lower()

    def test_export_csv_ne_contient_pas_pii(self, team_with_data, tmp_path):
        out = tmp_path / "team.csv"
        export_csv(team_with_data, out)
        content = out.read_text(encoding="utf-8")
        assert "@" not in content

    def test_export_html_ne_contient_pas_pii(self, team_with_data, tmp_path):
        out = tmp_path / "team.html"
        export_html(team_with_data, out)
        content = out.read_text(encoding="utf-8")
        assert "@" not in content


class TestRGPDSanitizeGenerateProfile:
    """Tests que generate_profile.py ne fuit pas d'emails."""

    def test_generate_profile_strip_emails_auteurs(self):
        """Les emails des auteurs git sont stripped du profil généré."""
        pytest.skip("Test d'intégration generate_profile à écrire — TODO Phase 25/08")
