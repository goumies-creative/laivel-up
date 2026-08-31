# Copyright 2026 Romy Alula — MIT License
"""Commandes CLI team extractées depuis cli.py (réduction god-module)."""

from __future__ import annotations

from pathlib import Path

import typer

from .console import console, error_console
from .model import LEVEL_LABELS
from .report import write_reports
from .team import (
    create_team,
    evaluate_member,
    export_csv,
    export_html,
    export_json,
    export_markdown,
    load_team,
    remove_member,
    save_team,
    set_opt_out,
)
from .utils import load_profile_data

_TEAM_SUBCOMMANDS = {'create', 'evaluate', 'export', 'opt-out', 'remove'}


def register_team_commands(team_app: typer.Typer) -> None:
    """Enregistre les sous-commandes team sur le Typer group donné."""

    @team_app.command(name='create')
    def team_create(
        name: str = typer.Argument(..., help="Nom de l'équipe."),
        members: str = typer.Argument(..., help='Noms des membres séparés par des virgules.'),
    ) -> None:
        """Crée une équipe avec des membres pseudo-anonymisés."""
        member_list = [m.strip() for m in members.split(',') if m.strip()]
        if not member_list:
            error_console.print('[bold red]Aucun membre fourni.[/bold red]')
            raise typer.Exit(code=1)
        if name in _TEAM_SUBCOMMANDS:
            error_console.print(
                f'[yellow]Avertissement : le nom d\'équipe "{name}" correspond à une sous-commande. '
                f"Cela peut créer une ambiguïté à l'usage.[/yellow]"
            )
        try:
            team = create_team(name, member_list)
        except ValueError as e:
            error_console.print(f'[bold red]{e}[/bold red]')
            raise typer.Exit(code=2)
        try:
            save_team(team)
        except ValueError as e:
            error_console.print(f'[bold red]{e}[/bold red]')
            raise typer.Exit(code=2)
        console.print(
            f"[bold green]Équipe '{team.name}' créée[/bold green] avec {len(team.members)} membres :"
        )
        for slug, m in team.members.items():
            console.print(f'  · {m.name} → [dim]{slug}[/dim]')

    @team_app.command(name='evaluate')
    def team_evaluate(
        team_name: str = typer.Argument(..., help="Nom de l'équipe."),
        member_slug: str = typer.Argument(..., help='Pseudo anonymisé (slug) du membre à évaluer.'),
        profil: Path = typer.Argument(..., help='Profil JSON du membre.'),
        out: Path = typer.Option(Path('rapports'), '--out', help='Dossier des rapports.'),
        verbose: bool = typer.Option(False, '--verbose', '-v', help='Sortie détaillée.'),
        html: bool = typer.Option(True, '--html/--no-html', help='Générer le rapport HTML.'),
    ) -> None:
        """Évalue un membre de l'équipe et enregistre le résultat."""
        try:
            profile = load_profile_data(profil)
            team = load_team(team_name)
        except ValueError as e:
            error_console.print(f'[bold red]{e}[/bold red]')
            raise typer.Exit(code=2)
        if member_slug not in team.members:
            error_console.print(
                f"[bold red]Membre '{member_slug}' non trouvé dans l'équipe '{team_name}'.[/bold red]"
            )
            if team.members:
                error_console.print('Membres disponibles :')
                for slug, m in team.members.items():
                    error_console.print(f'  · {m.name} → [dim]{slug}[/dim]')
            else:
                error_console.print('[dim]Aucun membre dans cette équipe.[/dim]')
            raise typer.Exit(code=1)

        verdict = evaluate_member(team, member_slug, profile)
        try:
            save_team(team)
        except ValueError as e:
            error_console.print(f'[bold red]{e}[/bold red]')
            raise typer.Exit(code=2)

        console.print(f'[bold]Verdict pour {member_slug} :[/bold]')
        if verdict.decided and verdict.level is not None:
            console.print(f'[bold green]Niveau : {LEVEL_LABELS[verdict.level]}[/bold green]')
        else:
            console.print('[bold yellow]Refus de trancher.[/bold yellow]')

        md, html_path = write_reports(verdict, out, with_html=html)
        console.print(f'[dim]Rapport Markdown : {md}[/dim]')
        if html_path:
            console.print(f'[dim]Rapport HTML     : {html_path}[/dim]')

    @team_app.command(name='export')
    def team_export(
        team_name: str = typer.Argument(..., help="Nom de l'équipe."),
        format: str = typer.Option('md', '--format', '-f', help='Format : md, html, csv, json'),
        out: Path = typer.Option(Path('rapports'), '--out', help='Dossier de sortie.'),
    ) -> None:
        """Exporte les résultats de l'équipe dans le format choisi."""
        export_fn = {
            'md': export_markdown,
            'html': export_html,
            'csv': export_csv,
            'json': export_json,
        }.get(format)

        if not export_fn:
            error_console.print(f'[bold red]Format inconnu : {format}[/bold red]')
            error_console.print('Formats disponibles : md, html, csv, json')
            raise typer.Exit(code=1)

        try:
            team = load_team(team_name)
        except ValueError as e:
            error_console.print(f'[bold red]{e}[/bold red]')
            raise typer.Exit(code=2)
        if not team.members:
            error_console.print(
                f"[bold yellow]Équipe '{team_name}' introuvable ou vide.[/bold yellow]"
            )
            raise typer.Exit(code=1)
        try:
            out_file = export_fn(team, out / f'equipe-{team_name}.{format}')
        except ValueError as e:
            error_console.print(f'[bold red]{e}[/bold red]')
            raise typer.Exit(code=2)
        console.print(f'[bold green]Export : {out_file}[/bold green]')

    @team_app.command(name='opt-out')
    def team_opt_out(
        team_name: str = typer.Argument(..., help="Nom de l'équipe."),
        member_slug: str = typer.Argument(..., help='Pseudo anonymisé (slug) du membre.'),
        enable: bool = typer.Option(
            True,
            '--enable/--disable',
            help="Activer ou désactiver l'opposition au traitement (RGPD art. 21).",
        ),
    ) -> None:
        """Active ou désactive l'opt-out RGPD (droit d'opposition) d'un membre."""
        try:
            team = load_team(team_name)
        except ValueError as e:
            error_console.print(f'[bold red]{e}[/bold red]')
            raise typer.Exit(code=2)
        if member_slug not in team.members:
            error_console.print(
                f"[bold red]Membre '{member_slug}' non trouvé dans l'équipe '{team_name}'.[/bold red]"
            )
            raise typer.Exit(code=1)
        set_opt_out(team, member_slug, enable)
        try:
            save_team(team)
        except ValueError as e:
            error_console.print(f'[bold red]{e}[/bold red]')
            raise typer.Exit(code=2)
        action = 'activé' if enable else 'désactivé'
        console.print(f'[bold green]Opt-out {action}[/bold green] pour le membre {member_slug}')

    @team_app.command(name='remove')
    def team_remove(
        team_name: str = typer.Argument(..., help="Nom de l'équipe."),
        member_slug: str = typer.Argument(
            ..., help='Pseudo anonymisé (slug) du membre à supprimer.'
        ),
        purge: bool = typer.Option(
            False, '--purge', help="Supprimer aussi l'historique du membre (RGPD)."
        ),
    ) -> None:
        """Supprime un membre de l'équipe."""
        try:
            team = load_team(team_name)
        except ValueError as e:
            error_console.print(f'[bold red]{e}[/bold red]')
            raise typer.Exit(code=2)
        if member_slug not in team.members:
            error_console.print(
                f"[bold red]Membre '{member_slug}' non trouvé dans l'équipe '{team_name}'.[/bold red]"
            )
            raise typer.Exit(code=1)
        remove_member(team, member_slug, purge)
        try:
            save_team(team)
        except ValueError as e:
            error_console.print(f'[bold red]{e}[/bold red]')
            raise typer.Exit(code=2)
        action = 'et son historique supprimé' if purge else 'supprimé'
        console.print(f"[bold green]Membre {action}[/bold green] de l'équipe '{team_name}'")
