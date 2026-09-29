# Copyright 2026 Romy Alula — MIT License
"""Mode entretien guide : questions, fusion des reponses, feedback.

Extrait de cli.py (res-1) : cli.py reste le cablage Typer fin et
re-exporte ces helpers pour compatibilite (tests monkeypatchent cli.*).
"""

from __future__ import annotations

import re

from .console import console
from .model import Level, ProfileData, Verdict, axis_label
from .nes_rendering import PIXEL_H, _nes_level_bar


def _print_interrogate_score(verdict: Verdict, turn: int, max_turns: int) -> None:
    """Affiche un indicateur visuel du score actuel pendant l'entretien."""
    console.print()
    console.print(f'[dim]  ÉTAPE {turn}/{max_turns} {PIXEL_H * 20}[/dim]')

    if not verdict.axis_scores:
        return

    parts = []
    for a in verdict.axis_scores:
        label = axis_label(a.axe)
        bar = _nes_level_bar(a.level)
        parts.append(f'{label}: {bar}')

    for p in parts:
        console.print(f'  {p}')

    if verdict.limiting_axis:
        console.print(f'  [dim]> Axe plancher : {axis_label(verdict.limiting_axis)}[/dim]')
    console.print()


def _parse_retry_ratio(low: str) -> float | None:
    """Extrait un ratio de reprise (0-1) d'une réponse libre."""
    percent = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:%|pourcent)', low)
    if percent:
        return min(max(float(percent.group(1).replace(',', '.')) / 100.0, 0.0), 1.0)
    ratio = re.search(r'(\d+)\s*(?:fois\s*)?sur\s*(\d+)', low)
    if ratio and int(ratio.group(2)) > 0:
        return min(max(int(ratio.group(1)) / int(ratio.group(2)), 0.0), 1.0)
    number = re.search(r'\d+(?:[.,]\d+)?', low)
    if not number:
        return None
    value = float(number.group(0).replace(',', '.'))
    return min(max(value if value <= 1.0 else value / 100.0, 0.0), 1.0)


_LEVELS_BY_KEYWORD = (
    ('white', 'WHITE'),
    ('red', 'RED'),
    ('blue', 'BLUE'),
    ('green', 'GREEN'),
    ('copper', 'COPPER'),
    ('silver', 'SILVER'),
    ('gold', 'GOLD'),
    ('blanc', 'WHITE'),
    ('rouge', 'RED'),
    ('bleu', 'BLUE'),
    ('vert', 'GREEN'),
    ('cuivre', 'COPPER'),
)


def _feedback_for(profile: ProfileData, question: str, answer: str) -> str:
    """Feedback après fusion : nomme ce qui a été enregistré, pour que la
    réponse ne soit jamais confondue avec la création d'une donnée. La valeur
    d'une trace vient du profil ou du chiffre donné ; une confirmation ne fait
    que la corroborer."""
    from .questions import QUESTION_IDS

    t = profile.traces
    if question == QUESTION_IDS['RETRIES_RATIO'] and t.get('retries_after_fact') is not None:
        return f'Proportion de reprise : {t["retries_after_fact"]:.0%}.'
    if question == QUESTION_IDS['RETRIES_TRIANGULATED'] and t.get('retries_triangulated') is True:
        return 'Reprise corroborée · la valeur des traces reste celle-ci.'
    if (
        question == QUESTION_IDS['ADOPTION_SIGNALS']
        and answer.strip().lower().startswith(('oui', 'yes'))
        and t.get('context_versioned') is True
    ):
        return 'Contexte marqué comme versionné.'
    return 'Réponse enregistrée.'


def _merge_answer(profile: ProfileData, question: str, answer: str) -> ProfileData:
    """Fusionne la réponse dans les traces pour le rescore."""
    from .questions import QUESTION_IDS

    low = answer.strip().lower()

    if question == QUESTION_IDS['PR_SIZES']:
        tokens = set(low.split())
        matched = [s.upper() for s in ('s', 'm', 'l', 'xl') if s in tokens]
        if matched:
            current = profile.traces.setdefault('pr_sizes', [])
            for size in matched:
                if size not in current:
                    current.append(size)

    elif question == QUESTION_IDS['RETRIES_TRIANGULATED']:
        if answer.strip():
            profile.traces['retries_triangulated'] = True

    elif question == QUESTION_IDS['RETRIES_RATIO']:
        parsed = _parse_retry_ratio(low)
        if parsed is not None:
            profile.traces['retries_after_fact'] = parsed

    elif question == QUESTION_IDS['ADOPTION_SIGNALS']:
        if low.startswith(('oui', 'yes')):
            profile.traces['context_versioned'] = True

    elif question == QUESTION_IDS['PROJECTS_COMPLETED']:
        nb = re.search(r'\d+', low)
        if nb:
            profile.traces['projects_completed'] = int(nb.group(0))

    elif question == QUESTION_IDS['PARALLEL_PROJECTS']:
        numbers = re.findall(r'\d+', low)
        if numbers:
            profile.traces['parallel_projects'] = int(numbers[0])
            if len(numbers) >= 2:
                profile.traces['projects_completed'] = int(numbers[1])
            elif re.search(r'tou(?:s|t)\b', low):
                profile.traces['projects_completed'] = int(numbers[0])

    elif question == QUESTION_IDS['DECLARED_LEVEL']:
        for word, level in _LEVELS_BY_KEYWORD:
            if re.search(rf'\b{word}\b', low):
                profile.declared_level = Level[level]
                break

    profile.answers['last_question'] = question
    profile.answers['last_answer'] = answer
    return profile
