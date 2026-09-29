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
from pathlib import Path

import typer
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from . import __version__
from ._completion_patch import patch_completion_encodings
from .cli_display import (
    MAX_JSON_MB,
    _filter_fields,
    _load_profile,
    _print_verdict,
)
from .cli_interrogate import (
    _feedback_for,
    _merge_answer,
    _parse_retry_ratio,
    _print_interrogate_score,
)
from .console import TTY, console, error_console, make_console
from .model import LEVEL_LABELS, Level, ProfileData, axis_label
from .nes_rendering import PIXEL_F, PIXEL_H, _nes_box, _nes_progress_bar
from .report import verdict_to_dict, write_reports
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
    from .scoring import evaluate

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
    from .questions import QUESTION_IDS
    from .scoring import evaluate

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


# ─── calibrate command (dashboard HTML) ──────────────────────────────
@app.command(name='calibrate')
def calibrate_cmd(
    expected: Path | None = typer.Option(
        None,
        '--expected',
        help='Chemin vers expected.json (défaut : grille/profils-officiels/expected.json)',
    ),
    profiles_dir: Path | None = typer.Option(
        None, '--profiles-dir', help='Dossier des profils officiels'
    ),
    out: Path = typer.Option(Path('rapports'), '--out', help='Dossier de sortie.'),
    show_proof: bool = typer.Option(
        False, '--show-proof', help='Affiche le tableau de preuve en CLI.'
    ),
) -> None:
    """Compare les verdicts aux niveaux attendus et génère un tableau de bord HTML."""
    from .calibrate_core import run_calibration
    from .calibrate_dashboard import generate_calibrate_html

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


if __name__ == '__main__':
    app()
