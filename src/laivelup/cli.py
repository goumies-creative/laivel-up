# Copyright 2026 Romy Alula — MIT License
"""CLI d'évaluation AIDD · LAIVEL UP · piste Décodeuse.

Usage :
  laivelup evaluate profil.json                 # verdict + rapports md/html
  laivelup evaluate profil.json --out rapports # choisir le dossier de sortie
  laivelup evaluate profil.json --no-html      # rapport Markdown seul
  laivelup interrogate profil.json             # mode entretien guidé
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import typer
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from .model import LEVEL_LABELS, Level, ProfileData, Verdict, axis_label, level_label
from .questions import QUESTION_IDS
from .report import write_reports
from .schema import validate_profile
from .scoring import evaluate
from .team import (
    Team,
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

app = typer.Typer(
    add_completion=False,
    help="Évaluation du niveau AIDD d'un développeur (piste Décodeuse).",
    no_args_is_help=True,
)
team_app = typer.Typer(help="Gestion d'équipes et suivi multi-membres.")
app.add_typer(team_app, name="team")
console = Console()

MAX_JSON_MB = 2


def _load_profile(path: Path) -> ProfileData:
    """Charge un profil JSON avec une erreur amicale et une borne de taille."""
    try:
        size = path.stat().st_size
    except OSError:
        raise typer.BadParameter(f"Fichier introuvable : {path}")
    if size > MAX_JSON_MB * 1024 * 1024:
        raise typer.BadParameter(f"Fichier trop volumineux (> {MAX_JSON_MB} Mo) : {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        console.print(f"[bold red]JSON invalide dans {path} :[/bold red] {exc}")
        raise typer.Exit(code=2)
    if not isinstance(data, dict):
        console.print("[bold red]Le JSON doit contenir un objet profil.[/bold red]")
        raise typer.Exit(code=2)

    # Validation schema (fail fast)
    schema_errors = validate_profile(data)
    if schema_errors:
        console.print("[bold red]Profil invalide :[/bold red]")
        for e in schema_errors:
            console.print(f"  · {e}")
        raise typer.Exit(code=2)

    declared = data.get("declared_level")
    if isinstance(declared, str) and declared:
        declared = declared.upper()
    declared_level = None
    if declared:
        try:
            declared_level = Level[declared]
        except KeyError:
            console.print(f"[bold red]declared_level inconnu : {declared}[/bold red] "
                          f"(valeurs : {', '.join(l.name for l in Level)})")
            raise typer.Exit(code=2)
    return ProfileData(
        name=data.get("name", path.stem),
        declared_level=declared_level,
        traces=data.get("traces", {}),
        answers=data.get("answers", {}),
        meta=data.get("meta", {}),
    )


def _print_verdict(profile: ProfileData, verbosity: int = 1) -> Verdict:
    """Affiche le verdict et le retourne (une seule évaluation par appel)."""
    verdict = evaluate(profile)
    table = Table(title=f"Verdict · {verdict.name}")
    table.add_column("Axe")
    table.add_column("Niveau")
    table.add_column("Confiance")
    for a in verdict.axis_scores:
        table.add_row(axis_label(a.axe), level_label(a.level),
                      f"{a.confidence:.0%}" if a.level is not None else "—")
    console.print(table)

    if verdict.data_errors:
        console.print("[bold red]Données invalides : refus de trancher.[/bold red]")
        for e in verdict.data_errors:
            console.print(f"  · {e}")
    elif verdict.decided:
        if verdict.level is None:
            return verdict
        console.print(f"[bold green]Niveau : {LEVEL_LABELS[verdict.level]}[/bold green]"
                      f" · axe plancher : [bold]{verdict.limiting_axis}[/bold]")
    else:
        console.print("[bold yellow]Refus de trancher : données insuffisantes ou contradictoires.[/bold yellow]")
        console.print("Questions à poser :")
        for q in verdict.next_steps:
            console.print(f"  · {q}")

    for f in verdict.red_flags:
        console.print(f"[bold red]⚠ {f.titre}[/bold red] · {f.constat}")
        if f.question:
            console.print(f"    → Question : {f.question}")

    if verbosity >= 1 and verdict.decided:
        console.print("[dim]· comment monter d'un cran ·[/dim]")
        for n in verdict.next_steps:
            console.print(f"[dim]  · {n}[/dim]")
    return verdict


@app.command(name="evaluate")
def evaluate_profile(
    profil: Path = typer.Argument(..., help="Profil JSON à évaluer."),
    out: Path = typer.Option(Path("rapports"), "--out", help="Dossier des rapports."),
    html: bool = typer.Option(True, "--html/--no-html", help="Générer le rapport HTML."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Sortie détaillée technique."),
) -> None:
    """Évalue un profil et écrit les rapports Markdown (+ HTML)."""
    profile = _load_profile(profil)
    verdict = _print_verdict(profile, verbosity=2 if verbose else 1)

    md, html_path = write_reports(verdict, out, with_html=html)
    console.print(f"[dim]Rapport Markdown : {md}[/dim]"
                  + (f"\n[dim]Rapport HTML : {html_path}[/dim]" if html_path else ""))


@app.command()
def interrogate(
    profil: Path | None = typer.Argument(None, help="Profil JSON de départ (optionnel)."),
    out: Path = typer.Option(Path("rapports"), "--out", help="Dossier des rapports."),
    max_turns: int = typer.Option(6, "--max-turns", help="Nombre max de questions posées."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Sortie détaillée technique."),
) -> None:
    """Mode entretien guidé (Décodeuse) : pose les questions, fusionne les réponses, re-score."""
    if profil is not None:
        profile = _load_profile(profil)
    else:
        profile = ProfileData(name="entretien")
    console.print("[bold]Mode entretien guidé[/bold] · je pose les questions ouvertes, "
                  "tu réponds, je réévalue à chaque fois.")

    asked: set[str] = set()
    # Une question inédite par tour : si une réponse « éteint » l'état (rien ne
    # change), on ne la re-pose jamais (rotation) ; on finit sinon en refus.
    for _ in range(max_turns):
        verdict = evaluate(profile)
        if verdict.decided:
            break
        candidates = [q for q in verdict.next_steps if any(
            goal in q for goal in ("taille", "niveau AIDD", "reprise", "contexte", "chantiers", "vérifier")
        )]
        questions = [q for q in (candidates or verdict.next_steps) if q not in asked]
        if not questions:
            break
        q = questions[0]
        asked.add(q)
        answer = Prompt.ask(f"[bold]{q}[/bold]")
        profile.answers["last_answer"] = answer
        profile = _merge_answer(profile, q, answer)
    else:
        # Tours épuisés alors qu'aucune question au début n'était décisive :
        # la dernière réponse a pu tout changer, on re-score une fois.
        verdict = evaluate(profile)

    if verdict.decided:
        if verdict.level is None:
            return
        console.print(f"[bold green]Verdict établi : {LEVEL_LABELS[verdict.level]}[/bold green]")
    else:
        console.print("[bold yellow]Fin de l'entretien sans verdict ferme : le refus reste explicite.[/bold yellow]")

    verdict = _print_verdict(profile, verbosity=2 if verbose else 1)
    md, html_path = write_reports(verdict, out)
    console.print(f"[dim]Rapport Markdown : {md}[/dim]"
                  + (f"\n[dim]Rapport HTML : {html_path}[/dim]" if html_path else ""))


# --- Team Tracker commands --------------------------------------------------------


@team_app.command(name="create")
def team_create(
    name: str = typer.Argument(..., help="Nom de l'équipe."),
    members: str = typer.Argument(..., help="Noms des membres séparés par des virgules."),
) -> None:
    """Crée une équipe avec des membres pseudo-anonymisés."""
    member_list = [m.strip() for m in members.split(",") if m.strip()]
    if not member_list:
        console.print("[bold red]Aucun membre fourni.[/bold red]")
        raise typer.Exit(code=1)
    team = create_team(name, member_list)
    save_team(team)
    console.print(f"[bold green]Équipe '{team.name}' créée[/bold green] avec {len(team.members)} membres :")
    for slug, m in team.members.items():
        console.print(f"  · {m.name} → [dim]{slug}[/dim]")


@team_app.command(name="evaluate")
def team_evaluate(
    team_name: str = typer.Argument(..., help="Nom de l'équipe."),
    member_slug: str = typer.Argument(..., help="Slug du membre à évaluer."),
    profil: Path = typer.Argument(..., help="Profil JSON du membre."),
    out: Path = typer.Option(Path("rapports"), "--out", help="Dossier des rapports."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Sortie détaillée."),
) -> None:
    """Évalue un membre de l'équipe et enregistre le résultat."""
    profile = _load_profile(profil)
    team = load_team(team_name)
    if member_slug not in team.members:
        console.print(f"[bold red]Membre '{member_slug}' non trouvé dans l'équipe '{team_name}'.[/bold red]")
        console.print("Membres disponibles :")
        for slug, m in team.members.items():
            console.print(f"  · {m.name} → [dim]{slug}[/dim]")
        raise typer.Exit(code=1)

    verdict = evaluate_member(team, member_slug, profile)
    save_team(team)

    console.print(f"[bold]Verdict pour {member_slug} :[/bold]")
    if verdict.decided and verdict.level is not None:
        console.print(f"[bold green]Niveau : {LEVEL_LABELS[verdict.level]}[/bold green]")
    else:
        console.print("[bold yellow]Refus de trancher.[/bold yellow]")

    md, html_path = write_reports(verdict, out)
    console.print(f"[dim]Rapport : {md}[/dim]")


@team_app.command(name="export")
def team_export(
    team_name: str = typer.Argument(..., help="Nom de l'équipe."),
    format: str = typer.Option("md", "--format", "-f", help="Format : md, html, csv, json"),
    out: Path = typer.Option(Path("rapports"), "--out", help="Dossier de sortie."),
) -> None:
    """Exporte les résultats de l'équipe dans le format choisi."""
    export_fn = {
        "md": export_markdown,
        "html": export_html,
        "csv": export_csv,
        "json": export_json,
    }.get(format)

    if not export_fn:
        console.print(f"[bold red]Format inconnu : {format}[/bold red]")
        console.print("Formats disponibles : md, html, csv, json")
        raise typer.Exit(code=1)

    team = load_team(team_name)
    if not team.members:
        console.print(f"[bold yellow]Équipe '{team_name}' introuvable ou vide.[/bold yellow]")
        raise typer.Exit(code=1)
    out_file = export_fn(team, out / f"equipe-{team_name}.{format}")
    console.print(f"[bold green]Export : {out_file}[/bold green]")


@team_app.command(name="opt-out")
def team_opt_out(
    team_name: str = typer.Argument(..., help="Nom de l'équipe."),
    member_slug: str = typer.Argument(..., help="Slug du membre."),
    enable: bool = typer.Option(True, "--enable/--disable", help="Activer ou désactiver l'opt-out."),
) -> None:
    """Active ou désactive l'opt-out RGPD pour un membre.

    Un membre en opt-out ne peut plus être évalué et est exclu des exports.
    """
    team = load_team(team_name)
    if member_slug not in team.members:
        console.print(f"[bold red]Membre '{member_slug}' non trouvé dans l'équipe '{team_name}'.[/bold red]")
        raise typer.Exit(code=1)
    set_opt_out(team, member_slug, enable)
    save_team(team)
    action = "activé" if enable else "désactivé"
    console.print(f"[bold green]Opt-out {action}[/bold green] pour le membre {member_slug}")


@team_app.command(name="remove")
def team_remove(
    team_name: str = typer.Argument(..., help="Nom de l'équipe."),
    member_slug: str = typer.Argument(..., help="Slug du membre à supprimer."),
    purge: bool = typer.Option(False, "--purge", help="Supprimer aussi l'historique du membre (RGPD)."),
) -> None:
    """Supprime un membre de l'équipe.

    Sans --purge, le membre est retiré mais son historique est conservé.
    Avec --purge, l'historique du membre est aussi supprimé (droit à l'oubli).
    """
    team = load_team(team_name)
    if member_slug not in team.members:
        console.print(f"[bold red]Membre '{member_slug}' non trouvé dans l'équipe '{team_name}'.[/bold red]")
        raise typer.Exit(code=1)
    remove_member(team, member_slug, purge)
    save_team(team)
    action = "et son historique supprimé" if purge else "supprimé"
    console.print(f"[bold green]Membre {action}[/bold green] de l'équipe '{team_name}'")


# --- Retry ratio parsing ---------------------------------------------------------


def _parse_retry_ratio(low: str) -> float | None:
    """Extrait un ratio de reprise (0-1) d'une réponse libre.

    Ordre de priorité : pourcentage explicite (« 60 % » → 0.6) → fraction
    (« 1 fois sur 2 » → 0.5) → nombre seul. Un nombre ≤ 1 est un ratio brut
    (« 0.5 » → 0.5, virgule française acceptée), > 1 un pourcentage en clair.
    Aucun chiffre reconnu => None (la trace n'est pas touchée)."""
    percent = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:%|pourcent)", low)
    if percent:
        return min(max(float(percent.group(1).replace(",", ".")) / 100.0, 0.0), 1.0)
    ratio = re.search(r"(\d+)\s*(?:fois\s*)?sur\s*(\d+)", low)
    if ratio and int(ratio.group(2)) > 0:
        return min(max(int(ratio.group(1)) / int(ratio.group(2)), 0.0), 1.0)
    number = re.search(r"\d+(?:[.,]\d+)?", low)
    if not number:
        return None
    value = float(number.group(0).replace(",", "."))
    return min(max(value if value <= 1.0 else value / 100.0, 0.0), 1.0)


# Level keywords, English first (better targeting). French words too ambiguous
# (« or » conjonction, « argent » monnaie) are deliberately excluded.
_LEVELS_BY_KEYWORD = (
    ("white", "WHITE"), ("red", "RED"), ("blue", "BLUE"), ("green", "GREEN"),
    ("copper", "COPPER"), ("silver", "SILVER"), ("gold", "GOLD"),
    ("blanc", "WHITE"), ("rouge", "RED"), ("bleu", "BLUE"), ("vert", "GREEN"),
    ("cuivre", "COPPER"),
)


def _merge_answer(profile: ProfileData, question: str, answer: str) -> ProfileData:
    """Fusionne la réponse dans les traces pour le rescore. Heuristiques simples,
    documentées dans METHODE.md, jamais de jugement basé sur la personne."""
    low = answer.strip().lower()

    # B3: Matching par ID de question (stable) plutôt que par sous-chaîne texte libre
    if question == QUESTION_IDS["PR_SIZES"]:
        matched = [size for size in ("S", "M", "L", "XL")
                   if re.search(rf"\b{size}\b", answer)]
        if matched:
            current = profile.traces.setdefault("pr_sizes", [])
            for size in matched:
                if size not in current:
                    current.append(size)

    elif question == QUESTION_IDS["RETRIES_TRIANGULATED"]:
        if answer.strip():
            profile.traces["retries_triangulated"] = True

    elif question == QUESTION_IDS["RETRIES_RATIO"]:
        parsed = _parse_retry_ratio(low)
        if parsed is not None:
            profile.traces["retries_after_fact"] = parsed

    elif question == QUESTION_IDS["ADOPTION_SIGNALS"]:
        if low.startswith(("oui", "yes")):
            profile.traces["context_versioned"] = True

    elif question == QUESTION_IDS["PROJECTS_COMPLETED"]:
        nb = re.search(r"\d+", low)
        if nb:
            profile.traces["projects_completed"] = int(nb.group(0))

    elif question == QUESTION_IDS["PARALLEL_PROJECTS"]:
        numbers = re.findall(r"\d+", low)
        if numbers:
            profile.traces["parallel_projects"] = int(numbers[0])
            if len(numbers) >= 2:
                profile.traces["projects_completed"] = int(numbers[1])
            elif re.search(r"tou(?:s|t)\b", low):
                profile.traces["projects_completed"] = int(numbers[0])

    elif question == QUESTION_IDS["DECLARED_LEVEL"]:
        for word, level in _LEVELS_BY_KEYWORD:
            if re.search(rf"\b{word}\b", low):
                profile.declared_level = Level[level]
                break

    profile.answers["last_question"] = question
    profile.answers["last_answer"] = answer
    return profile


if __name__ == "__main__":
    app()
