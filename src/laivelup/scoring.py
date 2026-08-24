# Copyright 2026 Romy Alula — MIT License
"""Scoring : évaluation par cellules de la grille AIDD, refus et équité.

Règle officielle : « Un niveau n'est atteint que si tous ses axes le sont. »
Le moteur remonte la grille (du haut vers le bas) : chaque axe dit le niveau
maximal que SA cellule autorise (min de maxima = AND sur les cellules), et le
niveau retenu est le plus haut dont TOUTES les cellules sont satisfaites.
Quand il manque une métadonnée de confirmation pour le cran au-dessus, il
n'invente pas le niveau : il annonce le niveau prouvé et pose la question
(refus de deviner).

Équité structurelle :
- Jamais de verdict plus bas que ce que les données prouvent.
- Valeur inconnue / contradictoire => refus + question, jamais un niveau arbitraire.
- `retries_after_fact` auto-déclaré non triangulé => confiance basse => refus
  plutôt qu'auto-pénalité. Le neurotype n'est jamais demandé ni inféré.
- Hyperfocus : le pic est signalé en preuve, le niveau reste sur l'habituel.
- White n'est jamais « deviné » par défaut : un profil sans adoption et sans
  preuve d'activité reste non tranché (refus + questions). White n'est décidable
  que par la grille elle-même (cellule « parallel = 0 » tirant `min()` vers
  White), jamais par un raccourci.
"""

from __future__ import annotations

from collections import Counter

from .model import AXES, AxisScore, Level, ProfileData, RedFlag, Verdict
from .scoring_defaults import SCORING_DEFAULTS

SIZE_VALUES = {"S", "M", "L", "XL"}
SIZE_ORDER = ["S", "M", "L", "XL"]
ADOPTION_SIGNALS = (
    "context_versioned",
    "agent_rules_versioned",
    "retry_loops",
    "prompts",
)

# Backward-compatible aliases reading from SCORING_DEFAULTS
CONFIDENCE_THRESHOLD: float = SCORING_DEFAULTS["CONFIDENCE_THRESHOLD"]  # type: ignore[assignment]
CONFIDENCE_PEAK: float = SCORING_DEFAULTS["CONFIDENCE_PEAK"]  # type: ignore[assignment]
CONFIDENCE_MEDIUM: float = SCORING_DEFAULTS["CONFIDENCE_MEDIUM"]  # type: ignore[assignment]
CONFIDENCE_LOW: float = SCORING_DEFAULTS["CONFIDENCE_LOW"]  # type: ignore[assignment]
CONFIDENCE_HARNESS_ONLY: float = SCORING_DEFAULTS["CONFIDENCE_HARNESS_ONLY"]  # type: ignore[assignment]
RETRIES_PER_LEVEL: dict[str, float] = SCORING_DEFAULTS["RETRIES_PER_LEVEL"]  # type: ignore[assignment]


def _as_float(value: object) -> float | None:
    """float(value) or None if non-numeric (preserves None mapping → axis not provided)."""
    if value is None:
        return None
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return None


def _as_int(value: object) -> int | None:
    """int(value) or None if non-integer (preserves None mapping → axis not provided)."""
    if value is None:
        return None
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return None


def normalize_profile(profile: ProfileData) -> list[str]:
    """Valide et coerce le profil. Retourne les erreurs lisibles (données qui mentent)."""
    errors: list[str] = []
    traces = profile.traces

    if not isinstance(traces, dict):
        return ["traces must be an object (dict)."]

    pr_sizes = traces.get("pr_sizes")
    if pr_sizes is not None:
        if not isinstance(pr_sizes, list):
            errors.append("traces.pr_sizes must be a list.")
        else:
            for s in pr_sizes:
                if s not in SIZE_VALUES:
                    errors.append(
                        f"traces.pr_sizes contains '{s}': allowed values "
                        f"{sorted(SIZE_VALUES)}."
                    )

    retries = traces.get("retries_after_fact")
    if retries is not None:
        if isinstance(retries, bool):
            errors.append("traces.retries_after_fact must be a number (ratio 0-1).")
        else:
            try:
                r = float(retries)
                if not 0.0 <= r <= 1.0:
                    errors.append("traces.retries_after_fact must be a ratio between 0 and 1.")
            except (TypeError, ValueError):
                errors.append("traces.retries_after_fact must be a number (ratio 0-1).")

    for key in ("parallel_projects", "projects_completed"):
        value = traces.get(key)
        if value is not None:
            if isinstance(value, bool):
                errors.append(f"traces.{key} must be a non-negative integer.")
            else:
                try:
                    # B2: Rejeter les floats non-entiers (3.7 → erreur, 3.0 → OK)
                    if isinstance(value, float):
                        if not value.is_integer():
                            errors.append(
                                f"traces.{key} must be an integer, not {value}. "
                                f"Use int({value}) = {int(value)} if truncation is intended."
                            )
                        else:
                            value = int(value)
                    else:
                        value = int(value)
                    if value < 0:
                        errors.append(f"traces.{key} must be a non-negative integer.")
                except (TypeError, ValueError):
                    errors.append(f"traces.{key} must be an integer.")

    if profile.declared_level is not None and not isinstance(profile.declared_level, Level):
        errors.append(f"declared_level '{profile.declared_level}': unknown level.")

    for key in ADOPTION_SIGNALS + ("agents_autonomous", "retries_triangulated"):
        if key in traces and not isinstance(traces[key], bool):
            errors.append(f"traces.{key} must be a boolean.")
    return errors


# --- Score « niveau maximum que cet axe autorise » (cellules de la grille) --------


def _dominant(pr_sizes: list[str]) -> tuple[str, Counter]:
    """Taille la plus fréquente et ses comptes bruts. À égalité, c'est
    `size_max` qui refuse (un habituel partagé n'en est pas un)."""
    counts = Counter(pr_sizes)
    best = max(counts[s] for s in SIZE_ORDER)
    tied = [s for s in SIZE_ORDER if counts[s] == best]
    return tied[-1], counts


def _peak_info(pr_sizes: list[str]) -> tuple[str | None, float]:
    """(taille max présente, ratio de présence). Un pic est isolé quand la taille
    la plus grosse présente reste minoritaire (habituel plus bas)."""
    if not pr_sizes:
        return None, 0.0
    counts = Counter(pr_sizes)
    n = len(pr_sizes)
    max_present = next(s for s in reversed(SIZE_ORDER) if counts[s] > 0)
    return max_present, counts[max_present] / n


def size_max(traces: dict) -> tuple[Level | None, float, list[str]]:
    """Cellule « Size » : S=>Red, M=>Blue, L/XL=>Gold (L-XL covers Copper to Gold).
    Un pic isolé (XL minoritaire) est signalé sans fixer le niveau, l'habituel
    restant la taille la plus fréquente. Une égalité parfaite entre deux tailles
    n'établit aucun habituel : confiance sous le seuil => refus (équité)."""
    pr_sizes = traces.get("pr_sizes")
    if pr_sizes is None or not isinstance(pr_sizes, list) or not pr_sizes:
        return None, 0.0, []
    dominant, counts = _dominant(pr_sizes)
    n = len(pr_sizes)
    evidence = [f"{counts[s]} PR {s}" for s in SIZE_ORDER if counts[s] > 0]
    max_present, ratio = _peak_info(pr_sizes)

    best = max(counts[s] for s in SIZE_ORDER)
    tied = [s for s in SIZE_ORDER if counts[s] == best]
    if len(tied) > 1:
        evidence.append(f"tailles à égalité ({'/'.join(tied)}) : habituel ambigu")
        return SCORING_DEFAULTS["SIZE_LEVEL"][tied[-1]], CONFIDENCE_LOW, evidence  # type: ignore[index]

    isolated_peak = max_present is not None and ratio < 0.5
    if isolated_peak:
        evidence.append(f"pic {max_present} isolé (habituel plus bas)")
    if isolated_peak and dominant == max_present:
        # Le pic est la taille la plus fréquente mais reste minoritaire :
        # l'habituel n'est pas établi, on ne tranche pas (refus, confiance basse).
        return Level.BLUE, CONFIDENCE_LOW, evidence
    # La confiance croît avec le nombre de PR observées, plafonnée à 0.9.
    confidence = min(CONFIDENCE_PEAK, 0.5 + 0.1 * n)
    return SCORING_DEFAULTS["SIZE_LEVEL"][dominant], confidence, evidence  # type: ignore[index]


def harness_max(traces: dict) -> tuple[Level | None, float, list[str]]:
    """Cellule « Harness » : prompts=>Red, context=>Blue, +behavior=>Green/Copper,
    +retry_loops=>Silver/Gold. La distinction Silver/Gold ne relève pas du harness."""
    any_signal = any(bool(traces.get(k)) for k in ADOPTION_SIGNALS)

    if not any_signal:
        return None, 0.0, []

    ctx = bool(traces.get("context_versioned"))
    rules = bool(traces.get("agent_rules_versioned"))
    loops = bool(traces.get("retry_loops"))

    if ctx and rules and loops:
        return Level.GOLD, CONFIDENCE_PEAK, ["context + behavior + retry loops"]
    if ctx and rules:
        return Level.COPPER, CONFIDENCE_PEAK, ["context + versioned agent rules"]
    if ctx:
        return Level.BLUE, CONFIDENCE_PEAK, ["project memory present and maintained"]
    return Level.RED, CONFIDENCE_HARNESS_ONLY, ["direct prompts, no context"]


def intervention_max(traces: dict) -> tuple[Level | None, float, list[str]]:
    """Cellule « Intervention » : majorité=>Red, une partie=>Blue, étapes clés=>
    Green/Copper, jamais=>Silver/Gold (Gold si agents autonomes).
    Non triangulé (auto-déclaré seul) => confiance 0.4, sous le seuil => refus."""
    retries = _as_float(traces.get("retries_after_fact"))
    if retries is None:
        return None, 0.0, []

    triangulated = bool(traces.get("retries_triangulated"))
    agents = bool(traces.get("agents_autonomous"))

    if retries <= RETRIES_PER_LEVEL["gold"]:
        if agents:
            level, evidence = Level.GOLD, ["never, framing included (autonomous agents)"]
        else:
            level, evidence = Level.SILVER, ["never, once task is framed"]
    elif retries <= RETRIES_PER_LEVEL["copper_or_green"]:
        level, evidence = Level.COPPER, ["intervention at key steps"]
    elif retries <= RETRIES_PER_LEVEL["blue"]:
        level, evidence = Level.BLUE, ["retry after the fact, on a portion"]
    else:
        level, evidence = Level.RED, ["retry after the fact, on majority"]

    if not triangulated:
        # Auto-déclaration seule : signal faible => confiance sous le seuil => refus.
        return level, CONFIDENCE_LOW, evidence
    return level, CONFIDENCE_MEDIUM, evidence


def parallel_max(traces: dict) -> tuple[Level | None, float, list[str]]:
    """Cellule « Parallel » : 0=>White, 1/2=>Green (case « 1 »),
    3=>Copper à Gold mais seulement si les chantiers sont menés au bout."""
    n = _as_int(traces.get("parallel_projects"))
    if n is None:
        return None, 0.0, []

    completed_int = _as_int(traces.get("projects_completed"))

    if n == 0:
        return Level.WHITE, CONFIDENCE_MEDIUM, ["no parallel projects"]
    if n < 3:
        return Level.GREEN, CONFIDENCE_MEDIUM, [f"{n} parallel projects"]
    if completed_int is not None and completed_int >= 3:
        return Level.GOLD, CONFIDENCE_MEDIUM, [f"{n} parallel projects, all completed"]
    if completed_int is None:
        return Level.GREEN, CONFIDENCE_LOW, [f"{n} parallel projects (completion to confirm)"]
    return Level.GREEN, CONFIDENCE_LOW, [f"{n} open projects but {completed_int} completed"]


# --- Diagnostics d'équité ---------------------------------------------------------


def detect_red_flags(profile: ProfileData) -> list[RedFlag]:
    flags: list[RedFlag] = []
    declared = profile.declared_level
    if declared is None:
        return flags
    retries = _as_float(profile.traces.get("retries_after_fact"))
    if retries is not None and retries > 0.5 and declared >= Level.BLUE:
        flags.append(
            RedFlag(
                severite=2,
                titre="Déclaré vs observé : reprise élevée",
                constat=(
                    f"Déclare {declared.name} avec un ratio de reprise de "
                    f"{retries:.0%}."
                ),
                source="traces / auto-déclaration",
                question=(
                    "La reprise vient-elle d'erreurs de l'IA, de raffinement, "
                    "ou de contexte perdu ?"
                ),
            )
        )
    if declared >= Level.BLUE and not profile.traces.get("context_versioned"):
        flags.append(
            RedFlag(
                severite=2,
                titre="Blue déclaré sans contexte",
                constat="Niveau Blue suppose une mémoire projet, aucun fichier de contexte repéré.",
                source="état du dépôt",
                question="As-tu une mémoire projet dans la tête ou versionnée ailleurs (wiki, tickets) ?",
            )
        )
    return flags


def progress_for_axis(axe: str, level: Level | None) -> list[str]:
    """Comment monter d'un cran sur cet axe, ou quoi prouver pour trancher."""
    if level is None:
        return [f"Axe « {axe} » : données insuffisantes pour trancher, voir les questions posées."]
    steps = {
        "size": {
            Level.RED: "Passer de features S à M : livrer des PR multi-étapes et les tenir au bout.",
            Level.BLUE: "Passer à des features L : enchaîner plusieurs étapes dans une même PR.",
            Level.GREEN: "Pousser à des features XL multi-modules régulières.",
            Level.COPPER: "Maintenir un habituel L-XL, pas seulement un pic.",
        },
        "harness": {
            Level.WHITE: "Créer une mémoire projet (contexte) et la maintenir.",
            Level.RED: "Créer une mémoire projet (contexte) et la maintenir.",
            Level.BLUE: "Versionner règles et agents dans le dépôt (behavior).",
            Level.GREEN: "Ajouter une boucle de relance automatique tant que la validation échoue.",
            Level.COPPER: "Ajouter une boucle de relance automatique tant que la validation échoue.",
            Level.SILVER: "Passer la relance en autonomie des agents pour viser Gold.",
        },
        "intervention": {
            Level.RED: "Réduire la reprise après coup : cadrer avant, corriger moins.",
            Level.BLUE: "Intervenir seulement aux étapes clés au lieu de partout.",
            Level.GREEN: "S'il reste une reprise, elle est ponctuelle ; viser zéro reprise.",
            Level.COPPER: "S'il reste une reprise, elle est ponctuelle ; viser zéro reprise.",
            Level.SILVER: "Confirmer que les agents prennent les tâches en autonomie (cadrage compris).",
        },
        "parallel": {
            Level.RED: "Mener 2 chantiers de front et les mener jusqu'au bout.",
            Level.BLUE: "Mener 3 chantiers en parallèle, menés au bout.",
            Level.GREEN: "Confirmer la complétude des 3 chantiers pour viser Copper et plus.",
            Level.COPPER: "Maintenir 3 chantiers en parallèle, tous menés au bout.",
            Level.SILVER: "Maintenir 3 chantiers en parallèle, tous menés au bout.",
        },
    }
    return [steps.get(axe, {}).get(level, "Maintenir le niveau actuel.")]


def _questions_for(profile: ProfileData) -> list[str]:
    from .questions import QUESTION_IDS

    questions: list[str] = []
    t = profile.traces
    if t.get("pr_sizes") is None:
        questions.append(QUESTION_IDS["PR_SIZES"])
    if profile.declared_level is None:
        questions.append(QUESTION_IDS["DECLARED_LEVEL"])
    if t.get("retries_after_fact") is None:
        questions.append(QUESTION_IDS["RETRIES_RATIO"])
    elif not t.get("retries_triangulated"):
        questions.append(QUESTION_IDS["RETRIES_TRIANGULATED"])
    if not any(bool(t.get(k)) for k in ADOPTION_SIGNALS):
        questions.append(QUESTION_IDS["ADOPTION_SIGNALS"])
    n_par = t.get("parallel_projects")
    if n_par is None:
        questions.append(QUESTION_IDS["PARALLEL_PROJECTS"])
    elif t.get("projects_completed") is None and (_as_int(n_par) or 0) >= 3:
        questions.append(QUESTION_IDS["PROJECTS_COMPLETED"])
    if not questions:
        questions.append(QUESTION_IDS["DEFAULT"])
    return questions


# --- Évaluation -------------------------------------------------------------------


def evaluate(profile: ProfileData) -> Verdict:
    errors = normalize_profile(profile)
    if errors:
        return Verdict(
            name=profile.name,
            level=None,
            axis_scores=[],
            limiting_axis=None,
            data_errors=errors,
            next_steps=_questions_for(profile),
        )

    scorers = {
        "size": size_max,
        "harness": harness_max,
        "intervention": intervention_max,
        "parallel": parallel_max,
    }

    axes = []
    for axe in AXES:
        level, confidence, evidence = scorers[axe](profile.traces)
        axes.append(AxisScore(axe=axe, level=level, confidence=confidence, evidence=evidence))
    tails = next((a for a in axes if a.axe == "size"), None)
    if tails:
        pr_sizes = profile.traces.get("pr_sizes")
        if isinstance(pr_sizes, list) and pr_sizes:
            max_present, ratio = _peak_info(pr_sizes)
            if ratio < 0.5:
                tails.variance = (
                    f"pic {max_present} intervenant, habituel plus bas "
                    "(niveau sur l'habituel)"
                )

    undecided_axes = [a for a in axes if a.level is None]
    low_conf_axes = [a for a in axes if a.level is not None and a.confidence < CONFIDENCE_THRESHOLD]

    def _refuse(limiting: str | None) -> Verdict:
        return Verdict(
            name=profile.name,
            level=None,
            axis_scores=axes,
            limiting_axis=limiting,
            next_steps=_questions_for(profile),
        )

    if undecided_axes:
        return _refuse(undecided_axes[0].axe)

    if low_conf_axes:
        return _refuse(low_conf_axes[0].axe)

    # All axes have levels at this point (undecided_axes filtered out)
    global_level = min(a.level for a in axes if a.level is not None)  # min des maxima => AND sur les cellules
    limiting = next(a.axe for a in axes if a.level == global_level)

    # Cran au-dessus non confirmé : on annonce le niveau prouvé et on pose la question.
    extra: list[str] = []
    t = profile.traces
    if global_level == Level.SILVER and not t.get("agents_autonomous"):
        extra.append(
            "Niveau Silver prouvé : les agents prennent-ils les tâches en autonomie "
            "plusieurs fois par jour (ping pour Gold) ?"
        )

    next_steps = progress_for_axis(limiting, global_level) + extra
    return Verdict(
        name=profile.name,
        level=global_level,
        axis_scores=axes,
        limiting_axis=limiting,
        red_flags=detect_red_flags(profile),
        next_steps=next_steps,
    )
