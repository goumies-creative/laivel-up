# Copyright 2026 Romy Alula — MIT License
"""Affichage CLI : verdict Rich + chargement profil + filtres JSON.

Extrait de cli.py (res-1) : cli.py reste le cablage Typer fin et
re-exporte ces helpers pour compatibilite (tests monkeypatchent cli.*).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import typer
from rich.table import Table

from .console import console, error_console
from .model import LEVEL_LABELS, ProfileData, Verdict, axis_label, level_label
from .nes_rendering import LEVEL_RICH_COLORS, _nes_box

MAX_JSON_MB = 2


def _load_profile(path: Path) -> ProfileData:
    """Charge un profil JSON avec erreur amicale et borne de taille.

    Construction canonique deleguee a utils.load_profile_data (pas de
    duplication du montage ProfileData). La validation schema reste ici
    car c'est une responsabilite CLI (exit codes 2).
    """
    from .schema import validate_profile
    from .utils import load_profile_data

    try:
        size = path.stat().st_size
    except OSError:
        raise typer.BadParameter(f'Fichier introuvable : {path}') from None
    if size > MAX_JSON_MB * 1024 * 1024:
        raise typer.BadParameter(f'Fichier trop volumineux (> {MAX_JSON_MB} Mo) : {path}')
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        error_console.print(f'[bold red]JSON invalide dans {path} :[/bold red] {exc}')
        raise typer.Exit(code=2) from exc
    if not isinstance(data, dict):
        error_console.print('[bold red]Le JSON doit contenir un objet profil.[/bold red]')
        raise typer.Exit(code=2)

    schema_errors = validate_profile(data)
    if schema_errors:
        error_console.print('[bold red]Profil invalide :[/bold red]')
        for e in schema_errors:
            error_console.print(f'  · {e}')
        raise typer.Exit(code=2)

    try:
        return load_profile_data(path)
    except ValueError as exc:
        error_console.print(f'[bold red]Profil invalide :[/bold red] {exc}')
        raise typer.Exit(code=2) from exc


NES_BORDER = '#3a3a5c'
NES_ACCENT = '#00aaff'
NES_SUCCESS = '#00cc44'
NES_WARNING = '#ccaa00'
NES_DANGER = '#cc3333'


def _print_verdict(verdict: Verdict, is_verbose: bool = False, use_json: bool = False) -> Verdict:
    """Affiche le verdict en style NES 8-bit."""
    if use_json:
        return verdict

    console.print()

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

    for f in verdict.red_flags:  # pragma: no cover — rendu Rich uniquement
        console.print()
        console.print(f'  [bold red]!! ALERTE : {f.titre}[/bold red]')
        console.print(f'     {f.constat} ({f.source})')
        if f.question:
            console.print(f'     [cyan]> {f.question}[/cyan]')

    if verdict.decided:
        console.print()
        console.print("[dim]  --- Comment monter d'un cran ---[/dim]")
        for n in verdict.next_steps:
            console.print(f'  [dim]> {n}[/dim]')

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
