# Copyright 2026 Romy Alula — MIT License
"""Tests cli.py : _load_profile erreurs, _parse_retry_ratio, _merge_answer, team commands.

Cible : 85% branch sur cli.py.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from laivelup.cli import _merge_answer, _parse_retry_ratio, app
from laivelup.model import Level, ProfileData

REPO = Path(__file__).parent.parent
runner = CliRunner()


# --- _parse_retry_ratio ------------------------------------------------


class TestParseRetryRatio:
    def test_percent_explicit(self):
        assert _parse_retry_ratio("60 %") == pytest.approx(0.6)

    def test_percent_decimal(self):
        assert _parse_retry_ratio("33,3 %") == pytest.approx(0.333)

    def test_pourcent_french(self):
        assert _parse_retry_ratio("20 pourcent") == pytest.approx(0.2)

    def test_ratio_sur(self):
        assert _parse_retry_ratio("1 fois sur 2") == pytest.approx(0.5)

    def test_ratio_sans_fois(self):
        assert _parse_retry_ratio("3 sur 10") == pytest.approx(0.3)

    def test_number_below_one(self):
        assert _parse_retry_ratio("0.5") == pytest.approx(0.5)

    def test_number_above_one_percentage(self):
        assert _parse_retry_ratio("75") == pytest.approx(0.75)

    def test_no_number(self):
        assert _parse_retry_ratio("aucune idée") is None

    def test_virgule_francaise(self):
        assert _parse_retry_ratio("0,8") == pytest.approx(0.8)

    def test_negative_percent_treated_as_positive(self):
        # Le regex capture le chiffre sans le signe, 5% → 0.05
        assert _parse_retry_ratio("-5 %") == pytest.approx(0.05)

    def test_clamped_to_one(self):
        assert _parse_retry_ratio("150 %") == pytest.approx(1.0)


# --- _merge_answer -----------------------------------------------------


class TestMergeAnswer:
    def test_merge_pr_sizes(self):
        p = ProfileData(name="x")
        _merge_answer(p, "Quelle est la taille habituelle", "souvent des M et L")
        assert "M" in p.traces["pr_sizes"]
        assert "L" in p.traces["pr_sizes"]

    def test_merge_retries_triangulated(self):
        p = ProfileData(name="x")
        _merge_answer(p, "peux-tu fournir", "voici 3 PR")
        assert p.traces["retries_triangulated"] is True

    def test_merge_retries_ratio(self):
        p = ProfileData(name="x")
        _merge_answer(p, "reprise après coup", "40 %")
        assert p.traces["retries_after_fact"] == pytest.approx(0.4)

    def test_merge_context_oui(self):
        p = ProfileData(name="x")
        _merge_answer(p, "mémoire projet contexte", "oui j'ai un contexte")
        assert p.traces["context_versioned"] is True

    def test_merge_context_non(self):
        p = ProfileData(name="x")
        _merge_answer(p, "mémoire projet contexte", "non")
        assert "context_versioned" not in p.traces

    def test_merge_parallel_projects(self):
        p = ProfileData(name="x")
        _merge_answer(p, "combien de chantiers", "3 chantiers en parallèle")
        assert p.traces["parallel_projects"] == 3

    def test_merge_projects_completed(self):
        p = ProfileData(name="x")
        _merge_answer(p, "combien de chantiers", "5 chantiers, 4 menés au bout")
        assert p.traces["parallel_projects"] == 5
        assert p.traces["projects_completed"] == 4

    def test_merge_level_blue(self):
        p = ProfileData(name="x")
        _merge_answer(p, "quel niveau AIDD", "mon niveau est bleu")
        assert p.declared_level == Level.BLUE

    def test_merge_level_gold(self):
        p = ProfileData(name="x")
        _merge_answer(p, "niveau AIDD", "gold")
        assert p.declared_level == Level.GOLD

    def test_merge_answers_stored(self):
        p = ProfileData(name="x")
        _merge_answer(p, "question test", "réponse test")
        assert p.answers["last_question"] == "question test"
        assert p.answers["last_answer"] == "réponse test"


# --- CLI evaluate errors -----------------------------------------------


class TestEvaluateErrors:
    def test_fichier_introuvable(self):
        r = runner.invoke(app, ["evaluate", "inexistant.json"])
        assert r.exit_code != 0

    def test_json_invalide(self, tmp_path):
        bad = tmp_path / "bad.json"
        bad.write_text("{invalid}", encoding="utf-8")
        r = runner.invoke(app, ["evaluate", str(bad)])
        assert r.exit_code == 2

    def test_non_dict_json(self, tmp_path):
        bad = tmp_path / "list.json"
        bad.write_text("[1, 2, 3]", encoding="utf-8")
        r = runner.invoke(app, ["evaluate", str(bad)])
        assert r.exit_code == 2

    def test_declared_level_inconnu(self, tmp_path):
        bad = tmp_path / "bad_level.json"
        bad.write_text(json.dumps({"name": "x", "declared_level": "PLATINUM"}), encoding="utf-8")
        r = runner.invoke(app, ["evaluate", str(bad)])
        assert r.exit_code == 2

    def test_fichier_trop_volumineux(self, tmp_path):
        big = tmp_path / "big.json"
        big.write_text(json.dumps({"name": "x", "traces": {"pr_sizes": ["S"] * 3_000_000}}), encoding="utf-8")
        r = runner.invoke(app, ["evaluate", str(big)])
        assert r.exit_code != 0

    def test_profil_valide(self, tmp_path):
        good = tmp_path / "good.json"
        good.write_text(json.dumps({
            "name": "test",
            "traces": {"pr_sizes": ["S", "M"], "parallel_projects": 1}
        }), encoding="utf-8")
        r = runner.invoke(app, ["evaluate", str(good), "--no-html"])
        assert r.exit_code == 0

    def test_profil_with_declared_string(self, tmp_path):
        good = tmp_path / "good.json"
        good.write_text(json.dumps({
            "name": "test",
            "declared_level": "BLUE",
            "traces": {"pr_sizes": ["S"], "parallel_projects": 1}
        }), encoding="utf-8")
        r = runner.invoke(app, ["evaluate", str(good), "--no-html"])
        assert r.exit_code == 0

    def test_verbose_mode(self, tmp_path):
        good = tmp_path / "good.json"
        good.write_text(json.dumps({
            "name": "test",
            "traces": {"pr_sizes": ["S"], "parallel_projects": 1}
        }), encoding="utf-8")
        r = runner.invoke(app, ["evaluate", str(good), "--no-html", "--verbose"])
        assert r.exit_code == 0


# --- CLI interrogate ---------------------------------------------------


class TestInterrogate:
    def test_interrogate_sans_profil(self, monkeypatch, tmp_path):
        from laivelup import cli
        answers = iter(["souvent des M", "bleu", "40%", "oui", "1 chantier"])
        monkeypatch.setattr(cli.Prompt, "ask", lambda prompt, **kw: next(answers))
        r = runner.invoke(cli.app, ["interrogate", "--max-turns", "5", "--out", str(tmp_path)])
        assert r.exit_code == 0

    def test_interrogate_avec_profil(self, monkeypatch, tmp_path):
        from laivelup import cli
        profil = tmp_path / "p.json"
        profil.write_text(json.dumps({"name": "x", "traces": {"parallel_projects": 1}}), encoding="utf-8")
        answers = iter(["souvent des M", "bleu", "40%", "oui"])
        monkeypatch.setattr(cli.Prompt, "ask", lambda prompt, **kw: next(answers))
        r = runner.invoke(cli.app, ["interrogate", str(profil), "--max-turns", "4", "--out", str(tmp_path)])
        assert r.exit_code == 0


# --- CLI team commands -------------------------------------------------


class TestTeamCommands:
    def test_team_create(self):
        r = runner.invoke(app, ["team", "create", "Alpha", "alice,bob,charlie"])
        assert r.exit_code == 0
        assert "Alpha" in r.output

    def test_team_create_vide(self):
        r = runner.invoke(app, ["team", "create", "Alpha", " "])
        assert r.exit_code == 1

    def test_team_export_md(self, tmp_path):
        r = runner.invoke(app, ["team", "export", "Alpha", "--out", str(tmp_path)])
        assert r.exit_code == 0
        export_file = tmp_path / "equipe-Alpha.md"
        assert export_file.exists()
        content = export_file.read_text(encoding="utf-8")
        assert "Équipe" in content
        assert "Membres" in content

    def test_team_export_format_inconnu(self):
        r = runner.invoke(app, ["team", "export", "Alpha", "--format", "xml"])
        assert r.exit_code == 1

    def test_team_export_json_content(self, tmp_path):
        r_create = runner.invoke(app, ["team", "create", "ExportJSON", "alice,bob"], catch_exceptions=False)
        assert r_create.exit_code == 0
        import re
        slug_lines = [l for l in r_create.output.splitlines() if "→" in l]
        slugs = [re.search(r"([a-z0-9]+-[a-f0-9]+)", l).group(1) for l in slug_lines]
        r = runner.invoke(app, ["team", "export", "ExportJSON", "--format", "json", "--out", str(tmp_path)])
        assert r.exit_code == 0
        export_file = tmp_path / "equipe-ExportJSON.json"
        assert export_file.exists()
        data = json.loads(export_file.read_text(encoding="utf-8"))
        assert data["team"] == "ExportJSON"
        assert len(data["members"]) == 2
        for slug in slugs:
            assert slug in data["members"]
            assert "name" in data["members"][slug]
            assert "confidence" in data["members"][slug]

    def test_team_export_csv_content(self, tmp_path):
        r_create = runner.invoke(app, ["team", "create", "ExportCSV", "alice,bob"], catch_exceptions=False)
        assert r_create.exit_code == 0
        r = runner.invoke(app, ["team", "export", "ExportCSV", "--format", "csv", "--out", str(tmp_path)])
        assert r.exit_code == 0
        export_file = tmp_path / "equipe-ExportCSV.csv"
        assert export_file.exists()
        lines = export_file.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) >= 3  # header + 2 members
        assert "name" in lines[0]
        assert "level" in lines[0]

    def test_team_evaluate(self, tmp_path):
        good = tmp_path / "good.json"
        good.write_text(json.dumps({
            "name": "test",
            "traces": {"pr_sizes": ["S"], "parallel_projects": 1}
        }), encoding="utf-8")
        r_create = runner.invoke(app, ["team", "create", "Alpha", "alice,bob"], catch_exceptions=False)
        assert "alice-" in r_create.output
        slug_line = [l for l in r_create.output.splitlines() if "alice" in l][0]
        alice_slug = slug_line.split("→")[1].strip().strip("[dim]").rstrip("[/dim]").strip()
        # Extract slug from rich markup: "alice → alice-2bd806c9"
        import re
        alice_slug = re.search(r"([a-z0-9]+-[a-f0-9]+)", slug_line).group(1)
        r = runner.invoke(app, ["team", "evaluate", "Alpha", alice_slug, str(good), "--out", str(tmp_path / "out")])
        assert r.exit_code == 0

    def test_team_persistence(self, tmp_path):
        good = tmp_path / "good.json"
        good.write_text(json.dumps({
            "name": "test",
            "traces": {"pr_sizes": ["S"], "parallel_projects": 1}
        }), encoding="utf-8")
        # Create team
        r1 = runner.invoke(app, ["team", "create", "Persist", "alice,bob"], catch_exceptions=False)
        assert r1.exit_code == 0
        import re
        slug_line = [l for l in r1.output.splitlines() if "alice" in l][0]
        alice_slug = re.search(r"([a-z0-9]+-[a-f0-9]+)", slug_line).group(1)
        # Evaluate alice
        r2 = runner.invoke(app, ["team", "evaluate", "Persist", alice_slug, str(good), "--out", str(tmp_path / "out")])
        assert r2.exit_code == 0
        # Verify persistence: team JSON file exists and contains snapshot
        from laivelup.team import load_team, _DEFAULT_TEAM_DIR
        team = load_team("Persist")
        assert alice_slug in team.members
        assert team.members[alice_slug].confidence > 0
        assert len(team.history) == 1
        assert team.history[0]["slug"] == alice_slug


# --- CLI help ----------------------------------------------------------


class TestCLIHelp:
    def test_main_help(self):
        r = runner.invoke(app, ["--help"])
        assert r.exit_code == 0
        assert "LAIVEL UP" in r.output or "évaluation" in r.output.lower()

    def test_evaluate_help(self):
        r = runner.invoke(app, ["evaluate", "--help"])
        assert r.exit_code == 0

    def test_interrogate_help(self):
        r = runner.invoke(app, ["interrogate", "--help"])
        assert r.exit_code == 0

    def test_team_help(self):
        r = runner.invoke(app, ["team", "--help"])
        assert r.exit_code == 0
