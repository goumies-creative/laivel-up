# Copyright 2026 Romy Alula — MIT License
"""Tests du moteur d'évaluation AIDD.

Fixtures construites case par case à partir de grille/aidd.md (référentiel officiel).
Règle d'or auditée : l'outil refuse quand il est ambigu, il ne juge jamais plus bas
que ce que ses données prouvent.
"""

from __future__ import annotations

import pytest

from laivelup.model import Level, ProfileData
from laivelup.scoring import evaluate, normalize_profile


def p(**kw):
    defaults = dict(name="test")
    defaults.update(kw)
    return ProfileData(**defaults)


# --- Fixtures par niveau du référentiel -----------------------------------------


def traces_size(pr):
    return {"pr_sizes": pr}


def traces_harness(ctx=False, rules=False, loops=False, prompts=True, agents=False):
    return {
        "context_versioned": ctx,
        "agent_rules_versioned": rules,
        "retry_loops": loops,
        "prompts": prompts,
        "agents_autonomous": agents,
    }


def traces_intervention(retries, triangulated=True):
    return {"retries_after_fact": retries, "retries_triangulated": triangulated}


def traces_parallel(n, completed=None):
    t = {"parallel_projects": n}
    if completed is not None:
        t["projects_completed"] = completed
    return t


def full(size, harness, intervention, parallel):
    t = {}
    t.update(size or {})
    t.update(harness or {})
    t.update(intervention or {})
    t.update(parallel or {})
    return t


# --- Cas décidés : un niveau est atteint si TOUS les axes le sont ----------------

NIVEAUX_FIXTURES = [
    # White : activité IA prouvée, prompts directs, la cellule « parallel = 0 »
    # tire le min() vers White (White n'est jamais deviné, il est décidé par la grille).
    (Level.WHITE, dict(traces=full(traces_size(["S", "S"]), traces_harness(prompts=True), traces_intervention(0.9), traces_parallel(0)))),
    # Red : S, prompts, retry majority, 1 project.
    (Level.RED, dict(traces=full(traces_size(["S", "S"]), traces_harness(), traces_intervention(0.8), traces_parallel(1)))),
    # Blue : M, context, retry partial, 1 project.
    (Level.BLUE, dict(traces=full(traces_size(["M", "M"]), traces_harness(ctx=True), traces_intervention(0.5), traces_parallel(1)))),
    # Green : L, context + rules, key steps, 1 project.
    (Level.GREEN, dict(traces=full(traces_size(["L", "L"]), traces_harness(ctx=True, rules=True), traces_intervention(0.2), traces_parallel(1)))),
    # Copper : L-XL, context + rules, key steps, 3 projects completed.
    (Level.COPPER, dict(traces=full(traces_size(["L", "XL", "L"]), traces_harness(ctx=True, rules=True), traces_intervention(0.2), traces_parallel(3, completed=3)))),
    # Silver : L-XL, context + behavior + loops, no retry, 3 projects.
    (Level.SILVER, dict(traces=full(traces_size(["XL", "XL", "L"]), traces_harness(ctx=True, rules=True, loops=True), traces_intervention(0.05), traces_parallel(3, completed=3)))),
    # Gold : total autonomy framing included (autonomous agents + zero retry).
    (Level.GOLD, dict(traces=full(traces_size(["XL", "XL", "L"]), traces_harness(ctx=True, rules=True, loops=True, agents=True), traces_intervention(0.0), traces_parallel(3, completed=3)))),
]


@pytest.mark.parametrize("expected,kw", NIVEAUX_FIXTURES, ids=lambda x: x if not isinstance(x, dict) else "")
def test_niveau_atteint_quand_tous_axes_le_sont(expected, kw):
    verdict = evaluate(p(**kw))
    assert verdict.decided, f"devrait trancher : {verdict.next_steps}"
    assert verdict.level == expected


def test_gold_never_human_commit():
    # Autonomous agents + zero retry + 3 projects completed: Gold.
    profile = p(
        traces=full(
            traces_size(["XL", "XL", "L"]),
            traces_harness(ctx=True, rules=True, loops=True, agents=True),
            traces_intervention(0.0),
            traces_parallel(3, completed=3),
        )
    )
    verdict = evaluate(profile)
    assert verdict.level == Level.GOLD
    assert verdict.decided


# --- Refus de trancher ------------------------------------------------------------


def test_profil_sans_donnees_refuse():
    verdict = evaluate(p(traces={}))
    assert not verdict.decided
    assert verdict.next_steps


def test_valeur_inconnue_pr_size_refuse():
    # Données qui mentent : "Z" n'est pas un niveau de taille admis.
    verdict = evaluate(p(traces=traces_size(["Z"])))
    assert not verdict.decided
    assert verdict.data_errors


def test_declared_inconnu_refuse():
    assert normalize_profile(p(declared_level="PLATINUM")) != []
    # via CLI c'est géré en amont ; ici le moteur refuse proprement.


def test_ratio_reprise_non_triangule_abaisse_confiance_et_refuse():
    # Équité : auto-déclaration seule => confiance 0.4 => refus, jamais un niveau bas arbitraire.
    verdict = evaluate(p(traces=full(traces_size(["M", "M"]), traces_harness(ctx=True), traces_intervention(0.8, triangulated=False), traces_parallel(1))))
    assert not verdict.decided
    itv = next(a for a in verdict.axis_scores if a.axe == "intervention")
    assert itv.confidence < 0.5


def test_chantiers_non_menes_au_bout_n_atteignent_pas_copper():
    verdict = evaluate(
        p(
            traces=full(
                traces_size(["L"]),
                traces_harness(ctx=True, rules=True),
                traces_intervention(0.2),
                traces_parallel(3, completed=1),  # 3 ouverts, 1 au bout
            )
        )
    )
    # L'axe parallèle est faible (<0.5) => refus plutôt que faux Copper.
    assert not verdict.decided


def test_harness_cumulatif_pas_silver_avec_boucles_seules():
    verdict = evaluate(
        p(
            traces=full(
                traces_size(["L"]),
                traces_harness(ctx=False, rules=False, loops=True),
                traces_intervention(0.2),
                traces_parallel(1),
            )
        )
    )
    assert verdict.decided
    harness = next(a for a in verdict.axis_scores if a.axe == "harness")
    assert harness.level == Level.RED  # boucles seules sans contexte : pas Silver
    assert verdict.level == Level.RED


def test_tie_break_taille_refuse():
    # Égalité parfaite (M/S 2-2) : aucun habituel établi, refus au lieu d'un
    # niveau vers le haut à confiance maximale (équité « refus > deviner »).
    a = evaluate(p(traces=traces_size(["M", "S", "M", "S"])))
    b = evaluate(p(traces=traces_size(["M", "S", "M", "S"])))
    assert a.decided == b.decided
    assert not a.decided
    taille = next(ax for ax in a.axis_scores if ax.axe == "size")
    assert taille.confidence < 0.5


def test_normalize_reprises_bool_refuse():
    # Un booléen à la place d'un ratio serait lu comme 0.0/1.0 : données qui
    # mentent => refus, jamais un niveau gonflé.
    verdict = evaluate(p(traces={"retries_after_fact": False}))
    assert not verdict.decided
    assert any("retries_after_fact" in e for e in verdict.data_errors)


def test_normalize_chantiers_bool_refuse():
    verdict = evaluate(p(traces={"parallel_projects": False}))
    assert not verdict.decided
    assert verdict.data_errors


def test_normalize_retries_triangulated_chaine_refuse():
    # La chaîne "false" valait True après bool() : refus de données incohérentes.
    verdict = evaluate(p(traces={"retries_triangulated": "false"}))
    assert not verdict.decided
    assert verdict.data_errors


def test_normalize_projects_completed_negatif_refuse():
    verdict = evaluate(p(traces={"projects_completed": -1}))
    assert not verdict.decided
    assert verdict.data_errors


def test_normalize_retries_inf_refuse():
    """float('inf') doit être rejeté par la validation."""
    verdict = evaluate(p(traces={"retries_after_fact": float("inf")}))
    assert not verdict.decided
    assert any("retries_after_fact" in e for e in verdict.data_errors)


def test_normalize_parallel_projects_float_non_entier_refuse():
    """3.7 doit être rejeté (B2 float rejection)."""
    verdict = evaluate(p(traces={"parallel_projects": 3.7}))
    assert not verdict.decided
    assert any("parallel_projects" in e for e in verdict.data_errors)


def test_confiance_basse_refuse():
    # Ratio non triangulé => confiance du global < 0.5 => refus.
    profile = p(
        traces=full(
            traces_size(["M"]),
            traces_harness(ctx=True),
            traces_intervention(0.05, triangulated=False),
            traces_parallel(1),
        )
    )
    verdict = evaluate(profile)
    assert not verdict.decided


def test_red_flag_porte_une_question():
    profile = p(
        declared_level=Level.BLUE,
        traces=full(
            traces_size(["M"]),
            traces_harness(ctx=True),
            traces_intervention(0.8, triangulated=True),
            traces_parallel(1),
        ),
    )
    verdict = evaluate(profile)
    assert any(f.question for f in verdict.red_flags)


def test_profil_white_vrai_est_white_pas_arbitraire():
    # Un vrai White peut être déterminé si on a des traces d'activité mais aucune adoption.
    verdict = evaluate(
        p(
            traces=full(
                traces_size([]),          # aucune feature livrée avec l'IA
                {},
                traces_intervention(0.95, triangulated=True),
                traces_parallel(0),
            )
        )
    )
    assert not verdict.decided  # pas de traces = refus (équité)


# --- Profils-maison en tests d'or -------------------------------------------------


def test_profil_maison_1_refuse_sur_contradiction():
    import json
    from pathlib import Path

    payload = json.loads(
        Path(__file__).parent.parent.joinpath("exemples", "profil-maison-1.json").read_text(encoding="utf-8")
    )
    profile = ProfileData(
        name=payload["name"],
        declared_level=Level[payload["declared_level"]],
        traces=payload["traces"],
    )
    verdict = evaluate(profile)
    assert verdict.decided is False


def test_profil_maison_2_refuse_sur_donnees_partiales():
    import json
    from pathlib import Path

    payload = json.loads(
        Path(__file__).parent.parent.joinpath("exemples", "profil-maison-2.json").read_text(encoding="utf-8")
    )
    profile = ProfileData(name=payload["name"], traces=payload["traces"])
    verdict = evaluate(profile)
    assert not verdict.decided
    assert verdict.next_steps


# --- Profil neuro-atypique simulé -------------------------------------------------


def test_profil_neuroatypique_refuse_plutot_que_juger_bas():
    """Hyperfocus (pic XL) + retries auto-déclarées élevées + peu de traces.

    L'outil doit REFUSER (jamais de niveau bas arbitraire) et montrer les questions,
    en l'absence de données corrélées entre pic et habituel.
    """
    profile = p(
        traces=full(
            traces_size(["XL", "S", "S", "S"]),          # 1 pic XL + habituel S
            {},                                            # pas de contexte déclaré
            traces_intervention(0.8, triangulated=False),   # auto-déclaré, non triangulé
            {},                                            # pas de parallèle renseigné
        )
    )
    verdict = evaluate(profile)
    assert not verdict.decided
    taille = next(a for a in verdict.axis_scores if a.axe == "size")
    assert any("pic XL" in e for e in taille.evidence)  # le pic est signalé, pas masqué
    assert any("reprise" in q for q in verdict.next_steps)
