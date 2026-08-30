# Copyright 2026 Romy Alula — MIT License
"""ViewModel pour adapter le Verdict à la présentation TUI.

Le ViewModel ne recalculle jamais le score.
Il adapte uniquement les données du domaine au format d'affichage.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from laivelup.model import AxisScore, Level, RedFlag, Verdict


@dataclass
class AxisViewModel:
    """Données adaptées d'un axe pour l'affichage."""

    label: str
    key: str
    level: Level | None
    confidence: float
    evidence: list[str]
    variance: str | None
    is_limiting: bool

    @classmethod
    def from_axis_score(
        cls,
        score: AxisScore,
        limiting_axis: str | None = None,
    ) -> AxisViewModel:
        from laivelup.model import axis_label

        return cls(
            label=axis_label(score.axe),
            key=score.axe,
            level=score.level,
            confidence=score.confidence,
            evidence=score.evidence,
            variance=score.variance,
            is_limiting=score.axe == limiting_axis,
        )


@dataclass
class VerdictViewModel:
    """Données adaptées du Verdict pour l'affichage TUI.

    Jamais de calcul métier. Uniquement formatage et adaptation.
    """

    name: str
    level: Level | None
    decided: bool
    axis_views: list[AxisViewModel]
    limiting_axis_label: str | None
    red_flags: list[RedFlag]
    next_steps: list[str]
    data_errors: list[str]

    @classmethod
    def from_verdict(cls, verdict: Verdict) -> VerdictViewModel:
        from laivelup.model import axis_label

        limiting_label = axis_label(verdict.limiting_axis) if verdict.limiting_axis else None

        return cls(
            name=verdict.name,
            level=verdict.level,
            decided=verdict.decided,
            axis_views=[
                AxisViewModel.from_axis_score(a, verdict.limiting_axis) for a in verdict.axis_scores
            ],
            limiting_axis_label=limiting_label,
            red_flags=verdict.red_flags,
            next_steps=verdict.next_steps,
            data_errors=verdict.data_errors,
        )
