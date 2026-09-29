# Copyright 2026 Romy Alula — MIT License
"""Modèle de données : axes AIDD, profil, verdict.

Aligné sur la grille officielle (grille/aidd.md) : 4 axes, 7 niveaux cumulatifs.
Le niveau n'est atteint que si tous les axes le sont (règle AND).

`grille/aidd.md` est la seule source de la grille : elle est chargée au
démarrage, et `Level`, `AXES` et les libellés ci-dessous en sont dérivés. Si la
grille se contredit — un niveau qui exige moins que celui du dessous, une
cellule inconnue, un tableau lisible qui diverge du bloc machine — l'import
échoue plutôt que de laisser tourner un calcul faux.

Équité structurelle : aucun champ lié au neurotype, aucune donnée sensible.
Le profil décrit des traces observables et des réponses déclaratives neutres.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum

from .grid_doc import GridError, load_grid


class Level(IntEnum):
    WHITE = 0
    RED = 1
    BLUE = 2
    GREEN = 3
    COPPER = 4
    SILVER = 5
    GOLD = 6


GRID = load_grid()


def _check_against_grid() -> None:
    """La grille fait foi ; l'enum doit en être l'image exacte."""
    enum_ids = tuple(level.name.lower() for level in Level)
    if enum_ids != GRID.level_ids:
        raise GridError(
            f'{GRID.path} : les niveaux de la grille {GRID.level_ids} ne correspondent '
            f'pas à Level {enum_ids}'
        )
    if tuple(level.value for level in Level) != tuple(level.rank for level in GRID.levels):
        raise GridError(
            f'{GRID.path} : les rangs de la grille ne correspondent pas aux valeurs de Level'
        )


_check_against_grid()

LEVEL_LABELS = {Level[level_id.upper()]: label for level_id, label in GRID.labels().items()}

AXES = GRID.axis_ids

# Display labels for axes (technical key unchanged: "parallel").
AXIS_LABELS = GRID.axis_labels()

# Couleurs par niveau (canonical — importées par report.py, calibrate_dashboard.py)
LEVEL_COLORS: dict[Level, dict[str, str]] = {
    Level.WHITE: {'bg': '#e8e8e8', 'fg': '#666', 'accent': '#999', 'icon': '❖'},
    Level.RED: {'bg': '#fde8e8', 'fg': '#c0392b', 'accent': '#e74c3c', 'icon': '🔺'},
    Level.BLUE: {'bg': '#e8f0fd', 'fg': '#2471a3', 'accent': '#3498db', 'icon': '🔹'},
    Level.GREEN: {'bg': '#e8fde8', 'fg': '#1e8449', 'accent': '#27ae60', 'icon': '🟢'},
    Level.COPPER: {'bg': '#fdf2e8', 'fg': '#b7950b', 'accent': '#d4ac0d', 'icon': '🥉'},
    Level.SILVER: {'bg': '#f0f0f8', 'fg': '#7f8c8d', 'accent': '#95a5a6', 'icon': '🥈'},
    Level.GOLD: {'bg': '#fdf8e8', 'fg': '#b7950b', 'accent': '#f1c40f', 'icon': '🥇'},
}


def level_label(level: Level | None) -> str:
    """Libellé d'un niveau, « — » si aucun niveau (cellule vide, comme la grille)."""
    return LEVEL_LABELS[level] if level is not None else '—'


def axis_label(axe: str) -> str:
    """Libellé lisible d'un axe pour le texte visible (accents corrects)."""
    return AXIS_LABELS.get(axe, axe)


@dataclass
class AxisScore:
    """Score discret d'un axe + degré de certitude (0-1) + variance éventuelle.

    Confiance basse (< 0.5) => l'axe est « faible » : on refuse de trancher
    sur le niveau global tant qu'il n'est pas corroboré.
    variance : signale un écart habituel vs pic (ex : hyperfocus) sans le
    transformer en pénalité : le niveau reste sur l'habituel.
    """

    axe: str
    level: Level | None
    confidence: float = 1.0
    evidence: list[str] = field(default_factory=list)
    variance: str | None = None


@dataclass
class ProfileData:
    """Le profil brut, tel que fourni ou recueilli.

    Hybride : des traces quand elles existent, un déclaratif quand elles manquent.
    La journée d'ouverture du hackathon fournit le format exact des 4 profils
    officiels ; le schéma est aligné dessus à ce moment-là.
    """

    name: str
    declared_level: Level | None = None
    traces: dict = field(default_factory=dict)  # commits, PR, branches, context files...
    answers: dict = field(default_factory=dict)  # réponses au questionnaire de cadrage
    meta: dict = field(default_factory=dict)


@dataclass
class RedFlag:
    severite: int  # 1..3
    titre: str
    constat: str
    source: str
    question: str | None = None  # la question à poser pour vérifier l'hypothèse


@dataclass
class Verdict:
    name: str
    level: Level | None  # None => les données ne permettent pas de trancher
    axis_scores: list[AxisScore]
    limiting_axis: str | None  # l'axe plancher qui fixe le niveau (ou l'axe faible)
    data_errors: list[str] = field(default_factory=list)  # profils invalides (données qui mentent)
    red_flags: list[RedFlag] = field(default_factory=list)
    next_steps: list[str] = field(default_factory=list)  # comment monter d'un cran / questions

    @property
    def decided(self) -> bool:
        return self.level is not None
