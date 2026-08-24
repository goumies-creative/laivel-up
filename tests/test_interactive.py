# Copyright 2026 Romy Alula — MIT License
"""Tests du mode entretien guidé et des heuristiques de fusion des réponses.

Couvre la correction de la passe CE (2026-08-21) : parsing du ratio de reprise
(P0 : « 0.5 » ne doit plus être lu comme 0.005), élisions françaises, mots
ambigus niveau (« or », « argent »), capture des deux chantiers, corroboration,
et rotation anti-boucle du mode interrogate.
"""

from __future__ import annotations

from typer.testing import CliRunner

from laivelup.cli import _merge_answer
from laivelup.model import Level, ProfileData
from laivelup.questions import QUESTION_IDS

runner = CliRunner()


def merge(question_key, answer, traces=None, declared=None):
    p = ProfileData(name='t', traces=traces or {}, declared_level=declared)
    return _merge_answer(p, QUESTION_IDS[question_key], answer)


# --- Ratio de reprise -----------------------------------------------------------


def test_reprise_pourcentage():
    p = merge('RETRIES_RATIO', '60 %')
    assert p.traces['retries_after_fact'] == 0.6


def test_reprise_ratio_brut_inferieur_a_un():
    # Regression P0 : un ratio brut demandé en clair ne doit pas être /100.
    p = merge('RETRIES_RATIO', '0.5')
    assert p.traces['retries_after_fact'] == 0.5


def test_reprise_virgule_francaise():
    p = merge('RETRIES_RATIO', '0,5')
    assert p.traces['retries_after_fact'] == 0.5


def test_reprise_fraction():
    p = merge('RETRIES_RATIO', '1 fois sur 2')
    assert p.traces['retries_after_fact'] == 0.5


def test_reprise_clamp_au_dessus_de_un():
    p = merge('RETRIES_RATIO', '150%')
    assert p.traces['retries_after_fact'] == 1.0


def test_reprise_sans_chiffre_ne_mute_pas():
    p = merge('RETRIES_RATIO', 'pas certain')
    assert 'retries_after_fact' not in p.traces


def test_corroboration_ne_parse_pas_le_ratio():
    # « 3 PR typiques » est une corroboration, pas un ratio (sinon 0.03 => inflation).
    p = merge(
        'RETRIES_TRIANGULATED',
        'oui voici 3 PR typiques',
        traces={'retries_after_fact': 0.5},
    )
    assert p.traces['retries_triangulated'] is True
    assert p.traces['retries_after_fact'] == 0.5


# --- Tailles --------------------------------------------------------------------


def test_taille_majuscule_prise():
    p = merge('PR_SIZES', 'souvent des M')
    assert p.traces['pr_sizes'] == ['M']


def test_taille_elision_ne_matche_pas():
    # « je l'utilise » contient un « l » minuscule : ne doit pas créer une fausse PR L.
    p = merge('PR_SIZES', "je l'utilise partout")
    assert p.traces.get('pr_sizes') is None


def test_taille_dedup_entre_tours():
    p = merge('PR_SIZES', 'souvent des M')
    p = _merge_answer(p, QUESTION_IDS['PR_SIZES'], 'souvent des M')
    assert p.traces['pr_sizes'] == ['M']


# --- Niveau déclaré -------------------------------------------------------------


def test_niveau_bleu_francais():
    p = merge('DECLARED_LEVEL', 'je pense bleu')
    assert p.declared_level == Level.BLUE


def test_niveau_or_conjonction_ne_declare_pas():
    p = merge('DECLARED_LEVEL', 'je débute, or je ne sais pas trop')
    assert p.declared_level is None


def test_niveau_argent_monnaie_ne_declare_pas():
    p = merge('DECLARED_LEVEL', "je gagne de l'argent avec")
    assert p.declared_level is None


def test_niveau_gold_anglais():
    p = merge('DECLARED_LEVEL', 'i think gold')
    assert p.declared_level == Level.GOLD


# --- Chantiers ------------------------------------------------------------------


def test_chantiers_question_parallele_deux_nombres():
    p = merge('PARALLEL_PROJECTS', '3, 2 menés au bout')
    assert p.traces['parallel_projects'] == 3
    assert p.traces['projects_completed'] == 2


def test_chantiers_question_parallele_tous_menes():
    p = merge('PARALLEL_PROJECTS', '3, tous menés au bout')
    assert p.traces['parallel_projects'] == 3
    assert p.traces['projects_completed'] == 3


def test_chantiers_completion_ne_touche_pas_paralleles():
    p = merge(
        'PROJECTS_COMPLETED',
        '2',
        traces={'parallel_projects': 3},
    )
    assert p.traces['parallel_projects'] == 3
    assert p.traces['projects_completed'] == 2


# --- Mode interrogate ------------------------------------------------------------


def test_interrogate_aboutit_a_un_verdict(monkeypatch, tmp_path):
    from laivelup import cli

    answers = iter(
        [
            'souvent des M',
            'mon niveau est bleu',
            '40%',
            'oui voici 3 PR typiques',
            "oui j'ai un contexte",
            '1 chantier',
        ]
    )
    monkeypatch.setattr(cli.Prompt, 'ask', lambda prompt, **kw: next(answers))
    r = runner.invoke(cli.app, ['interrogate', '--max-turns', '6', '--out', str(tmp_path)])
    assert r.exit_code == 0
    assert 'Verdict établi' in r.output


def test_interrogate_ne_repose_jamais_la_meme_question(monkeypatch, tmp_path):
    from laivelup import cli

    asked: list[str] = []
    monkeypatch.setattr(
        cli.Prompt, 'ask', lambda prompt, **kw: asked.append(str(prompt)) or 'pas certain'
    )
    r = runner.invoke(cli.app, ['interrogate', '--max-turns', '6', '--out', str(tmp_path)])
    assert r.exit_code == 0
    assert asked, 'aucune question posée'
    assert len(asked) == len(set(asked))
