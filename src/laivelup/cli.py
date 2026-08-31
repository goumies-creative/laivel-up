# Copyright 2026 Romy Alula — MIT License
"""CLI d'évaluation AIDD · LAIVEL UP.

Usage :
  laivelup evaluate profil.json                 # verdict + rapports md/html
  laivelup evaluate profil.json --json          # sortie JSON (CI/agent)
  laivelup evaluate profil.json --fail-on RED   # exit 1 si niveau < RED
  laivelup evaluate profil.json --out rapports  # choisir le dossier de sortie
  laivelup evaluate profil.json --no-html       # rapport Markdown seul
  laivelup interrogate profil.json              # mode entretien guidé
  laivelup schema                              # schema JSON (auto-découverte agent)
  laivelup --version                           # version

Environment :
  NO_COLOR    désactive les couleurs (supporté par Rich)
  FORCE_COLOR force les couleurs même en pipe (supporté par Rich)

Exit codes :
  0  Succès
  1  Erreur métier (membre non trouvé, format inconnu)
  2  Erreur de validation (profil invalide, JSON mal formé)
  3  Erreur outil (timeout, I/O)
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Optional

import typer
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from . import __version__
from ._completion_patch import patch_completion_encodings
from .console import NO_COLOR, TTY, console, error_console, make_console
from .model import LEVEL_LABELS, Level, ProfileData, Verdict, axis_label, level_label
from .questions import QUESTION_IDS, QUESTION_TRACE_KEYS
from .report import verdict_to_dict, write_reports
from .schema import validate_profile
from .scoring import evaluate
from .team import (
    Team,
    create_team,
    evaluate_member,
    load_team,
    save_team,
)
from .team_cli import register_team_commands

# Bug Typer amont : install_bash/install_zsh lisent ~/.bashrc sans encoding ->
# UnicodeDecodeError sur rc hors ANSI (cp1252 FR). Patch tolérant au chargement.
patch_completion_encodings()

# ─── App ─────────────────────────────────────────────────────────────
app = typer.Typer(
    add_completion=True,
    help="Évaluation du niveau d'adoption de l'AIDD des développeurs.",
    no_args_is_help=True,
)
team_app = typer.Typer(help="Gestion d'équipes et suivi multi-membres.")
app.add_typer(team_app, name='team')
register_team_commands(team_app)

MAX_JSON_MB = 2

# ─── Schema (P0.3) ──────────────────────────────────────────────────
COMMAND_SCHEMA = {
    'name': 'laivelup',
    'version': __version__,
    'description': "Évaluation du niveau d'adoption de l'AIDD des développeurs",
    'commands': {
        'evaluate': {
            'description': 'Évalue un profil et génère les rapports',
            'args': {'profil': {'type': 'string', 'required': True, 'description': 'Profil JSON'}},
            'options': {
                '--out': {
                    'type': 'string',
                    'default': 'rapports',
                    'description': 'Dossier de sortie',
                },
                '--html/--no-html': {
                    'type': 'boolean',
                    'default': True,
                    'description': 'Rapport HTML',
                },
                '--json': {'type': 'boolean', 'default': False, 'description': 'Sortie JSON'},
                '--fail-on': {
                    'type': 'string',
                    'description': 'Échoue si le niveau est inférieur (ex. : RED)',
                },
                '--fields': {'type': 'string', 'description': 'Filtrer champs JSON'},
                '--verbose': {
                    'type': 'boolean',
                    'default': False,
                    'description': 'Sortie détaillée',
                },
            },
        },
        'interrogate': {
            'description': 'Mode entretien guidé',
            'args': {
                'profil': {
                    'type': 'string',
                    'required': False,
                    'description': 'Profil JSON de départ',
                }
            },
            'options': {
                '--out': {'type': 'string', 'default': 'rapports'},
                '--max-turns': {'type': 'integer', 'default': 6},
                '--verbose': {'type': 'boolean', 'default': False},
            },
        },
        'team': {
            'description': "Gestion d'équipes",
            'subcommands': {
                'create': {'args': {'name': {}, 'members': {}}},
                'evaluate': {'args': {'team_name': {}, 'member_slug': {}, 'profil': {}}},
                'export': {
                    'args': {'team_name': {}},
                    'options': {'--format': {'enum': ['md', 'html', 'csv', 'json']}},
                },
                'opt-out': {'args': {'team_name': {}, 'member_slug': {}}},
                'remove': {'args': {'team_name': {}, 'member_slug': {}}},
            },
        },
        'schema': {'description': 'Retourne le schema JSON (auto-découverte agent)'},
    },
    'exit_codes': {
        '0': 'Succès',
        '1': 'Erreur métier',
        '2': 'Erreur de validation',
        '3': 'Erreur outil',
    },
}


# ─── --version (P1.2) ────────────────────────────────────────────────
def _version_callback(value: bool) -> None:
    if value:
        error_console.print(f'laivelup {__version__}')
        raise typer.Exit(0)


@app.callback(invoke_without_command=True)
def main(
    version: bool | None = typer.Option(
        None,
        '--version',
        '-V',
        callback=_version_callback,
        is_eager=True,
        help='Affiche la version',
    ),
    color: bool | None = typer.Option(
        None,
        '--color/--no-color',
        help='Force ou désactive la couleur (surcharge NO_COLOR/FORCE_COLOR).',
    ),
) -> None:
    """Évaluation du niveau d'adoption de l'AIDD des développeurs."""
    if color is not None:
        # Le flag explicite surcharge NO_COLOR/FORCE_COLOR (lus une seule fois
        # à l'import). console/error_console sont recréés ici plutôt que
        # mutés en place : Console n'expose pas de setter fiable post-construction
        # pour son système de couleurs.
        global console, error_console
        console = make_console(no_color=not color)
        error_console = Console(stderr=True, no_color=not color)


# ─── schema command (P0.3) ──────────────────────────────────────────
@app.command('schema')
def schema_cmd() -> None:
    """Retourne le schema JSON de ce tool (auto-découverte agent)."""
    print(json.dumps(COMMAND_SCHEMA, indent=2, ensure_ascii=False))


# ─── Helpers ─────────────────────────────────────────────────────────
def _load_profile(path: Path) -> ProfileData:
    """Charge un profil JSON avec une erreur amicale et une borne de taille."""
    try:
        size = path.stat().st_size
    except OSError:
        raise typer.BadParameter(f'Fichier introuvable : {path}')
    if size > MAX_JSON_MB * 1024 * 1024:
        raise typer.BadParameter(f'Fichier trop volumineux (> {MAX_JSON_MB} Mo) : {path}')
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        error_console.print(f'[bold red]JSON invalide dans {path} :[/bold red] {exc}')
        raise typer.Exit(code=2)
    if not isinstance(data, dict):
        error_console.print('[bold red]Le JSON doit contenir un objet profil.[/bold red]')
        raise typer.Exit(code=2)

    schema_errors = validate_profile(data)
    if schema_errors:
        error_console.print('[bold red]Profil invalide :[/bold red]')
        for e in schema_errors:
            error_console.print(f'  · {e}')
        raise typer.Exit(code=2)

    declared = data.get('declared_level')
    if isinstance(declared, str) and declared:
        declared = declared.upper()
    declared_level = None
    if declared:
        try:
            declared_level = Level[declared]
        except KeyError:
            error_console.print(
                f'[bold red]declared_level inconnu : {declared}[/bold red] '
                f'(valeurs : {", ".join(l.name for l in Level)})'
            )
            raise typer.Exit(code=2)
    return ProfileData(
        name=data.get('name', path.stem),
        declared_level=declared_level,
        traces=data.get('traces', {}),
        answers=data.get('answers', {}),
        meta=data.get('meta', {}),
    )


# ─── 8-bit NES art constants ───────────────────────────────────────
NES_BORDER = '#3a3a5c'
NES_ACCENT = '#00aaff'
NES_SUCCESS = '#00cc44'
NES_WARNING = '#ccaa00'
NES_DANGER = '#cc3333'

# Couleur Rich par niveau, partagée entre la barre de progression
# (_nes_level_bar) et le tableau d'axes (_print_verdict) : un axe RED doit
# se voir en rouge partout, pas seulement dans l'un des deux rendus (9.1.c).
LEVEL_RICH_COLORS: dict[Level, str] = {
    Level.WHITE: 'dim',
    Level.RED: 'red',
    Level.BLUE: 'blue',
    Level.GREEN: 'green',
    Level.COPPER: 'yellow',
    Level.SILVER: 'bright_white',
    Level.GOLD: 'bright_yellow',
}

PIXEL_H = '\u2580'  # ▀ upper half block
PIXEL_L = '\u2584'  # ▄ lower half block
PIXEL_F = '\u2588'  # █ full block
PIXEL_M = '\u2592'  # ▒ medium shade
PIXEL_D = '\u2591'  # ░ light shade

# ASCII art borders for NES-style boxes
BOX_TL = '+'
BOX_TR = '+'
BOX_BL = '+'
BOX_BR = '+'
BOX_H = '-'
BOX_V = '|'


def _nes_box(lines: list[str], color: str = 'cyan', width: int = 40) -> None:
    """Affiche un cadre NES-style en ASCII art."""
    border = BOX_H * (width - 2)
    open_tag = f'[bold {color}]'
    close_tag = '[/' + f'bold {color}]'
    console.print(open_tag + BOX_TL + border + BOX_TR + close_tag)
    for line in lines:
        padded = line.ljust(width - 4)
        console.print(
            open_tag + BOX_V + close_tag + ' ' + padded + ' ' + open_tag + BOX_V + close_tag
        )
    console.print(open_tag + BOX_BL + border + BOX_BR + close_tag)


def _nes_progress_bar(current: int, total: int, width: int = 20, color: str = 'green') -> str:
    """Barre de progression NES en blocs pixel."""
    filled = int((current / total) * width) if total > 0 else 0
    empty = width - filled
    return f'[{color}]{PIXEL_F * filled}[/{color}][dim]{PIXEL_D * empty}[/dim]'


def _nes_level_bar(level: Level | None, max_level: Level = Level.GOLD) -> str:
    """Barre de niveau pixel pour un axe."""
    if level is None:
        return f'[dim]{PIXEL_D * 7}[/dim]'
    filled = level.value + 1
    empty = max_level.value + 1 - filled
    c = LEVEL_RICH_COLORS.get(level, 'dim')
    return f'[{c}]{PIXEL_F * filled}[/{c}][dim]{PIXEL_D * empty}[/dim]'


def _print_verdict(verdict: Verdict, is_verbose: bool = False, use_json: bool = False) -> Verdict:
    """Affiche le verdict en style NES 8-bit."""
    if use_json:
        return verdict

    console.print()

    # Tableau des axes
    table = Table(
        title=f'VERDICT · {verdict.name}',
        border_style=NES_BORDER,
        header_style='bold cyan',
    )
    table.add_column('AXE', style='bold')
    table.add_column('NIVEAU')
    table.add_column('CONFIANCE')

    for a in verdict.axis_scores:
        lvl_str = level_label(a.level)
        conf = f'{a.confidence:.0%}' if a.level is not None else '--'
        color = LEVEL_RICH_COLORS.get(a.level, 'dim') if a.level is not None else 'dim'
        table.add_row(
            axis_label(a.axe),
            f'[{color}]{lvl_str}[/{color}]',
            conf,
        )
    console.print(table)

    console.print()

    if verdict.data_errors:  # pragma: no cover — rendu Rich uniquement, schema bloque en amont
        _nes_box(
            [
                '[bold red]!! DONNÉES INVALIDES !![/bold red]',
                '[red]Refus de trancher.[/red]',
            ],
            color='red',
            width=44,
        )
        for e in verdict.data_errors:
            console.print(f'  [red]> {e}[/red]')
    elif verdict.decided:
        assert verdict.level is not None
        label = LEVEL_LABELS[verdict.level]
        console.print(f'  [bold green]> NIVEAU : {label}[/bold green]')
        if verdict.limiting_axis:
            console.print(f'  [bold]> Axe plancher : {axis_label(verdict.limiting_axis)}[/bold]')
    else:
        _nes_box(
            [
                '[bold yellow]!! REFUS DE TRANCHER !![/bold yellow]',
                '[yellow]Données insuffisantes.[/yellow]',
            ],
            color='yellow',
            width=44,
        )
        console.print()
        console.print('[dim]  Questions à poser :[/dim]')
        for q in verdict.next_steps:
            console.print(f'  [dim]> {q}[/dim]')

    # Red flags
    for f in verdict.red_flags:  # pragma: no cover — rendu Rich uniquement
        console.print()
        console.print(f'  [bold red]!! ALERTE : {f.titre}[/bold red]')
        console.print(f'     {f.constat} ({f.source})')
        if f.question:
            console.print(f'     [cyan]> {f.question}[/cyan]')

    # Next steps
    if verdict.decided:
        console.print()
        console.print("[dim]  --- Comment monter d'un cran ---[/dim]")
        for n in verdict.next_steps:
            console.print(f'  [dim]> {n}[/dim]')

    # Verbose
    if is_verbose:  # pragma: no cover — rendu Rich uniquement
        console.print()
        console.print('[dim]  --- Détails techniques ---[/dim]')
        for a in verdict.axis_scores:
            label = axis_label(a.axe)
            lvl = level_label(a.level)
            conf = f'{a.confidence:.0%}' if a.level is not None else '--'
            console.print(f'  [dim]> {label}: {lvl} ({conf})[/dim]')
            if a.evidence:
                for ev in a.evidence:
                    console.print(f'     [dim]  source · {ev}[/dim]')
            if a.variance:
                console.print(f'     [dim]  variance · {a.variance}[/dim]')
        if verdict.data_errors:
            console.print('[dim]  > données invalides :[/dim]')
            for e in verdict.data_errors:
                console.print(f'     [dim]  > {e}[/dim]')

    return verdict


def _filter_fields(data: dict[str, Any], fields_str: str) -> dict[str, Any]:
    """Filtre les champs d'un dict JSON."""
    field_list = [f.strip() for f in fields_str.split(',')]
    return {k: v for k, v in data.items() if k in field_list}


# ─── evaluate command (P0.1 + P1.3 + P2.2) ─────────────────────────
EVALUATE_EPILOG = """
Exemples :

  laivelup evaluate profil.json                 Verdict + rapports md/html
  laivelup evaluate profil.json --json          Sortie JSON (CI/agent)
  laivelup evaluate profil.json --fail-on RED   Code 1 si niveau < RED
  laivelup evaluate profil.json --out rapports  Choisir le dossier de sortie
  laivelup evaluate profil.json --no-html       Rapport Markdown seul
"""


@app.command(name='evaluate', epilog=EVALUATE_EPILOG)
def evaluate_profile(
    profil: Path = typer.Argument(..., help='Profil JSON à évaluer.'),
    out: Path = typer.Option(Path('rapports'), '--out', help='Dossier des rapports.'),
    html: bool = typer.Option(True, '--html/--no-html', help='Générer le rapport HTML.'),
    verbose: bool = typer.Option(False, '--verbose', '-v', help='Sortie détaillée technique.'),
    json_output: bool = typer.Option(False, '--json', '-j', help='Sortie JSON (CI/agent).'),
    fail_on: str | None = typer.Option(
        None,
        '--fail-on',
        help='Échoue si le niveau est inférieur (valeurs : RED, BLUE, GREEN, COPPER, SILVER, GOLD).',
    ),
    fields: str | None = typer.Option(None, '--fields', help='Filtrer champs JSON.'),
) -> None:
    """Évalue un profil et écrit les rapports Markdown (+ HTML)."""
    profile = _load_profile(profil)

    use_json = json_output or not TTY
    verdict = evaluate(profile)
    _print_verdict(verdict, is_verbose=verbose, use_json=use_json)

    # JSON output (P0.1)
    if use_json:
        data = verdict_to_dict(verdict)
        if fields:
            data = _filter_fields(data, fields)
        output = json.dumps(data, indent=2, ensure_ascii=False)
        print(output)
        # Also write reports if --out is explicitly provided
        if out != Path('rapports'):
            out.mkdir(parents=True, exist_ok=True)
            md, html_path = write_reports(verdict, out, with_html=html)
    else:
        md, html_path = write_reports(verdict, out, with_html=html)
        console.print()
        console.print(f'[dim]> Rapport Markdown : {md}[/dim]')
        if html_path:
            console.print(f'[dim]> Rapport HTML     : {html_path}[/dim]')
        console.print()

    # --fail-on (P1.3)
    if fail_on:
        if verdict.level is None:
            if not use_json:
                error_console.print(
                    '[yellow]Avertissement : verdict non décidé (niveau=None), --fail-on ignoré[/yellow]'
                )
        else:
            try:
                fail_level = Level[fail_on.upper()]
            except KeyError:
                valid = ', '.join(l.name for l in Level)
                error_console.print(
                    f'[bold red]Niveau inconnu pour --fail-on : {fail_on}[/bold red] '
                    f'(valeurs : {valid})'
                )
                raise typer.Exit(code=2)
            if verdict.level.value < fail_level.value:
                if not use_json:
                    error_console.print(
                        f'\n[red]ÉCHEC : niveau {LEVEL_LABELS[verdict.level]} < {LEVEL_LABELS[fail_level]}[/red]'
                    )
                raise typer.Exit(1)


# ─── interrogate command ────────────────────────────────────────────
INTERROGATE_EPILOG = """
Exemples :

  laivelup interrogate                          Démarre un entretien à vide
  laivelup interrogate profil.json              Repart d'un profil existant
  laivelup interrogate profil.json --max-turns 3
"""


@app.command(epilog=INTERROGATE_EPILOG)
def interrogate(
    profil: Path | None = typer.Argument(None, help='Profil JSON de départ (optionnel).'),
    out: Path = typer.Option(Path('rapports'), '--out', help='Dossier des rapports.'),
    max_turns: int = typer.Option(6, '--max-turns', help='Nombre max de questions posées.'),
    verbose: bool = typer.Option(False, '--verbose', '-v', help='Sortie détaillée technique.'),
) -> None:
    """Mode entretien guidé : pose les questions, fusionne les réponses, ré-évalue."""
    if profil is not None:
        profile = _load_profile(profil)
    else:
        profile = ProfileData(name='entretien')

    # ── Introduction 8-bit ──
    console.print()
    _nes_box(
        [
            '[bold cyan]LAIVEL UP[/bold cyan]',
            '[cyan]Mode Entretien[/cyan]',
            '',
            '[dim]Questions ouvertes · Réponses · Nouvelle évaluation[/dim]',
            "[dim]L'évaluateur pose les questions · la personne répond[/dim]",
        ],
        color='cyan',
        width=56,
    )
    console.print()

    # Build reverse mapping: question text -> question ID
    qid_by_text = {text: qid for qid, text in QUESTION_IDS.items()}
    asked: set[str] = set()

    for turn in range(1, max_turns + 1):
        verdict = evaluate(profile)

        if verdict.decided:
            break

        # ── Indicateur de progression 8-bit ──
        _print_interrogate_score(verdict, turn, max_turns)

        candidates = [
            q
            for q in verdict.next_steps
            if any(
                goal in q
                for goal in (
                    'taille',
                    "niveau d'adoption",
                    'reprise',
                    'contexte',
                    'chantiers',
                    'vérifier',
                )
            )
        ]
        questions = [
            q for q in (candidates or verdict.next_steps) if qid_by_text.get(q, q) not in asked
        ]
        if not questions:
            break
        q = questions[0]
        qid = qid_by_text.get(q, q)
        asked.add(qid)

        # ── Question 8-bit ──
        console.print()
        console.print(f'[bold cyan]> QUESTION {turn}/{max_turns} {PIXEL_F * 10}[/bold cyan]')
        console.print()
        answer = Prompt.ask(f'[white]{q}[/white]')
        profile = _merge_answer(profile, q, answer)

        # ── Feedback 8-bit ──
        console.print()
        console.print(f'[green]> OK[/green] [dim]{_feedback_for(profile, q, answer)}[/dim]')
    else:
        verdict = evaluate(profile)

    # ── Resultat final 8-bit ──
    console.print()
    console.print(f'[dim]{PIXEL_H * 44}[/dim]')
    console.print()

    if verdict.decided:
        assert verdict.level is not None
        label = LEVEL_LABELS[verdict.level]
        _nes_box(
            [
                '[bold green]*** NIVEAU DÉBLOQUÉ ***[/bold green]',
                '',
                f'  [bold green]{label}[/bold green]',
                '',
                f'  [dim]Axe plancher : {axis_label(verdict.limiting_axis or "")}[/dim]',
            ],
            color='green',
            width=44,
        )
    else:
        _nes_box(
            [
                '[bold yellow]!! REFUS DE TRANCHER !![/bold yellow]',
                '',
                '[dim]  Données insuffisantes.[/dim]',
                '[dim]  Le refus est explicite.[/dim]',
            ],
            color='yellow',
            width=44,
        )

    console.print()
    _print_verdict(verdict, is_verbose=verbose)
    md, html_path = write_reports(verdict, out)
    console.print()
    console.print(f'[dim]> Rapport Markdown : {md}[/dim]')
    if html_path:
        console.print(f'[dim]> Rapport HTML     : {html_path}[/dim]')
    console.print()


def _print_interrogate_score(verdict: Verdict, turn: int, max_turns: int) -> None:
    """Affiche un indicateur visuel du score actuel pendant l'entretien."""
    console.print()
    console.print(f'[dim]  ÉTAPE {turn}/{max_turns} {PIXEL_H * 20}[/dim]')

    if not verdict.axis_scores:
        return

    # Barre de progression par axe (style NES)
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


# ─── calibrate command (dashboard HTML) ──────────────────────────────
@app.command(name='calibrate')
def calibrate_cmd(
    expected: Path = typer.Option(
        None,
        '--expected',
        help='Chemin vers expected.json (défaut : grille/profils-officiels/expected.json)',
    ),
    profiles_dir: Path = typer.Option(None, '--profiles-dir', help='Dossier des profils officiels'),
    out: Path = typer.Option(Path('rapports'), '--out', help='Dossier de sortie.'),
    show_proof: bool = typer.Option(
        False, '--show-proof', help='Affiche le tableau de preuve en CLI.'
    ),
) -> None:
    """Compare les verdicts aux niveaux attendus et génère un tableau de bord HTML."""
    from .calibrate_core import run_calibration

    result = run_calibration(expected=expected, profiles_dir=profiles_dir)

    if show_proof:
        # Tableau CLI
        table = Table(title=f'Calibration · {result.total} profils · {result.errors} erreurs')
        table.add_column('Profil')
        table.add_column('Obtenu')
        table.add_column('Attendu')
        table.add_column('Statut')
        for r in result.rows:
            status_icon = '✅' if r.status == 'OK' else '❌' if r.status == 'FAIL' else '⏭️'
            obtained = 'Undécis' if r.obtained in (None, 'UNDECIDED') else r.obtained
            table.add_row(
                r.name,
                obtained,
                r.expected or '—',
                f'{status_icon} {r.detail}',
            )
        console.print(table)
        if result.errors == 0:
            console.print('[bold green]Calibration réussie : 0 erreur[/bold green]')
        else:
            console.print(f'[bold red]{result.errors} erreur(s) de calibration[/bold red]')

    # Dashboard HTML
    html_path = out / 'calibrate-dashboard.html'
    out.mkdir(parents=True, exist_ok=True)
    html_content = generate_calibrate_html(result)
    html_path.write_text(html_content, encoding='utf-8')
    console.print(f'[dim]Tableau de bord calibration : {html_path}[/dim]')


# --- Retry ratio parsing ---------------------------------------------------------


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


if __name__ == '__main__':
    app()
