# Copyright 2026 Romy Alula — MIT License
"""Team Tracker : gestion d'équipes, journalisation, réévaluation, export multi-format.

Permet de créer des équipes, évaluer leurs membres, suivre l'évolution dans le temps,
et exporter les résultats en HTML, Markdown, CSV ou JSON.

Équité structurelle : les équipes ne stockent aucune donnée sensible.
Le pseudo-anonyme (slug RGPD) protège l'identité dans les rapports partagés.
"""

from __future__ import annotations

import contextlib
import csv
import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from html import escape as html_escape
from pathlib import Path
from typing import TextIO

from .model import Level, ProfileData, Verdict
from .scoring import evaluate
from .utils import generate_team_salt, slug

_DEFAULT_TEAM_DIR = Path(".laivelup") / "teams"


def _team_path(name: str, path: Path | None = None) -> Path:
    """Retourne le chemin du fichier JSON de l'équipe."""
    if path is not None:
        return path
    return _DEFAULT_TEAM_DIR / f"{name}.json"


def save_team(team: Team, path: Path | None = None) -> Path:
    """Sauvegarde l'état de l'équipe en JSON."""
    target = _team_path(team.name, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "name": team.name,
        "salt": team.salt,
        "members": {
            team_slug: {
                "name": m.name,
                "slug": m.slug,
                "level": m.level.name if m.level else None,
                "limiting_axis": m.limiting_axis,
                "confidence": m.confidence,
                "timestamp": m.timestamp,
                "red_flags_count": m.red_flags_count,
                "next_steps_count": m.next_steps_count,
                "opt_out": m.opt_out,
            }
            for team_slug, m in team.members.items()
        },
        "history": team.history,
    }
    target.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return target


def load_team(name: str, path: Path | None = None) -> Team:
    """Charge une équipe depuis un fichier JSON. Retourne une équipe vide si absent."""
    source = _team_path(name, path)
    if not source.exists():
        return Team(name=name)
    data = json.loads(source.read_text(encoding="utf-8"))
    team_salt = data.get("salt", generate_team_salt())
    team = Team(name=data.get("name", name), salt=team_salt)
    for team_slug, m in data.get("members", {}).items():
        level = None
        if m.get("level"):
            with contextlib.suppress(KeyError):
                level = Level[m["level"]]
        team.members[team_slug] = MemberSnapshot(
            slug=team_slug,
            name=m["name"],
            level=level,
            limiting_axis=m.get("limiting_axis"),
            confidence=m.get("confidence", 0.0),
            timestamp=m.get("timestamp", ""),
            red_flags_count=m.get("red_flags_count", 0),
            next_steps_count=m.get("next_steps_count", 0),
            opt_out=m.get("opt_out", False),
        )
    team.history = data.get("history", [])
    return team


@dataclass
class MemberSnapshot:
    """Un instantané d'évaluation d'un membre à un moment donné."""

    slug: str
    name: str
    level: Level | None
    limiting_axis: str | None
    confidence: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    red_flags_count: int = 0
    next_steps_count: int = 0
    opt_out: bool = False


@dataclass
class Team:
    """Représentation d'une équipe avec son historique d'évaluations."""

    name: str
    members: dict[str, MemberSnapshot] = field(default_factory=dict)
    history: list[dict] = field(default_factory=list)
    salt: str = field(default_factory=generate_team_salt)


def _slug(name: str, salt: str | None = None) -> str:
    """Pseudo-anonyme RGPD — wrapper pour compatibilité interne."""
    return slug(name, salt)


def create_team(name: str, member_names: list[str]) -> Team:
    """Crée une équipe avec des membres pseudo-anonymisés."""
    team = Team(name=name)
    for member_name in member_names:
        team_slug = _slug(member_name, team.salt)
        team.members[team_slug] = MemberSnapshot(
            slug=team_slug,
            name=member_name,
            level=None,
            limiting_axis=None,
            confidence=0.0,
        )
    return team


def evaluate_member(team: Team, slug: str, profile: ProfileData) -> Verdict:
    """Évalue un membre de l'équipe et enregistre le snapshot."""
    if slug not in team.members:
        raise ValueError(f"Membre '{slug}' non trouvé dans l'équipe '{team.name}'")

    member = team.members[slug]
    if member.opt_out:
        raise ValueError(
            f"Membre '{member.name}' a activé l'opt-out RGPD — évaluation refusée."
        )

    verdict = evaluate(profile)
    member = team.members[slug]

    # Fix #5: confiance de l'axe plancher (pas le max)
    axis_confidences = {a.axe: a.confidence for a in verdict.axis_scores}
    limiting_confidence = (
        axis_confidences.get(verdict.limiting_axis, 0.0)
        if verdict.limiting_axis
        else 0.0
    )

    snapshot = MemberSnapshot(
        slug=slug,
        name=member.name,
        level=verdict.level,
        limiting_axis=verdict.limiting_axis,
        confidence=limiting_confidence,
        red_flags_count=len(verdict.red_flags),
        next_steps_count=len(verdict.next_steps),
    )
    team.members[slug] = snapshot

    # Journaliser dans l'historique (B1: opt_out persisté dans l'historique)
    team.history.append({
        "timestamp": snapshot.timestamp,
        "slug": slug,
        "level": verdict.level.name if verdict.level else None,
        "limiting_axis": verdict.limiting_axis,
        "confidence": snapshot.confidence,
        "opt_out": False,
    })

    return verdict


def remove_member(team: Team, slug: str, purge: bool = False) -> None:
    """Supprime un membre de l'équipe.

    Args:
        team: L'équipe
        slug: Slug du membre à supprimer
        purge: Si True, supprime aussi l'historique de ce membre
    """
    if slug not in team.members:
        raise ValueError(f"Membre '{slug}' non trouvé dans l'équipe '{team.name}'")

    if purge:
        team.history = [h for h in team.history if h.get("slug") != slug]
    else:
        # B1: Marquer les entrées d'historique avec opt_out=True
        team.history = [
            {**h, "opt_out": True} if h.get("slug") == slug else h
            for h in team.history
        ]

    del team.members[slug]


def set_opt_out(team: Team, slug: str, opt_out: bool = True) -> None:
    """Active ou désactive l'opt-out RGPD pour un membre."""
    if slug not in team.members:
        raise ValueError(f"Membre '{slug}' non trouvé dans l'équipe '{team.name}'")
    team.members[slug].opt_out = opt_out


def export_json(team: Team, path: Path) -> Path:
    """Exporte l'état de l'équipe en JSON (exclut les membres en opt-out)."""
    opt_out_slugs = {s for s, m in team.members.items() if m.opt_out}
    data = {
        "team": team.name,
        "exported_at": datetime.now().isoformat(),
        "members": {
            team_slug: {
                "name": m.name,
                "slug": m.slug,
                "level": m.level.name if m.level else None,
                "limiting_axis": m.limiting_axis,
                "confidence": m.confidence,
                "timestamp": m.timestamp,
            }
            for team_slug, m in team.members.items()
            if not m.opt_out
        },
        # B1: filtre par opt_out du membre OU opt_out persisté dans l'historique
        "history": [
            h for h in team.history
            if h.get("slug") not in opt_out_slugs and not h.get("opt_out")
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def export_markdown(team: Team, path: Path) -> Path:
    """Exporte un rapport Markdown de l'équipe (exclut les membres en opt-out)."""
    lines = [f"# Équipe · {team.name}"]
    lines.append(f"\n*Exporté le {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")

    lines.append("\n## Membres\n")
    lines.append("| Membre | Slug | Niveau | Axe plancher | Confiance |")
    lines.append("|--------|------|--------|--------------|-----------|")
    for m_slug, m in team.members.items():
        if m.opt_out:
            continue
        level = m.level.name if m.level else "—"
        axis = m.limiting_axis or "—"
        conf = f"{m.confidence:.0%}"
        lines.append(f"| {m.name} | `{m_slug}` | {level} | {axis} | {conf} |")

    opt_out_slugs = {s for s, m in team.members.items() if m.opt_out}
    history_filtered = [
        h for h in team.history
        if h.get("slug") not in opt_out_slugs and not h.get("opt_out")
    ]

    if history_filtered:
        lines.append("\n## Historique\n")
        lines.append("| Date | Membre | Niveau | Axe | Confiance |")
        lines.append("|------|--------|--------|-----|-----------|")
        for entry in history_filtered[-20:]:
            ts = entry["timestamp"][:10]
            level = entry["level"] or "—"
            axis = entry["limiting_axis"] or "—"
            conf = f"{entry['confidence']:.0%}"
            slug_short = entry["slug"][:16] + "..."
            lines.append(f"| {ts} | {slug_short} | {level} | {axis} | {conf} |")

    lines.append(
        "\n---\n\n*Données techniques déclarées uniquement. "
        "Aucune donnée personnelle, aucun neurotype demandé ni inféré.*"
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def export_csv(team: Team, path: Path) -> Path:
    """Exporte les données de l'équipe en CSV (exclut les membres en opt-out)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "slug", "level", "limiting_axis", "confidence", "timestamp"])
        for slug, m in team.members.items():
            if m.opt_out:
                continue
            writer.writerow([
                m.name,
                m.slug,
                m.level.name if m.level else "",
                m.limiting_axis or "",
                f"{m.confidence:.2f}",
                m.timestamp,
            ])
    return path


def export_html(team: Team, path: Path) -> Path:
    """Exporte un rapport HTML de l'équipe (exclut les membres en opt-out)."""
    rows = []
    for team_slug, m in team.members.items():
        if m.opt_out:
            continue
        level = m.level.name if m.level else "—"
        conf = f"{m.confidence:.0%}"
        kelas = "ok" if m.level and m.level >= Level.BLUE else "ko"
        rows.append(
            f'<tr><td>{html_escape(m.name)}</td><td><code>{html_escape(team_slug)}</code></td>'
            f'<td><span class="badge {kelas}">{html_escape(level)}</span></td>'
            f'<td>{html_escape(m.limiting_axis or "—")}</td><td>{conf}</td></tr>'
        )

    opt_out_slugs = {s for s, m in team.members.items() if m.opt_out}
    history_filtered = [
        h for h in team.history
        if h.get("slug") not in opt_out_slugs and not h.get("opt_out")
    ]

    history_rows = []
    for entry in history_filtered[-20:]:
        ts = entry["timestamp"][:10]
        level = entry["level"] or "—"
        history_rows.append(
            f'<tr><td>{html_escape(ts)}</td><td>{html_escape(entry["slug"][:16])}...</td>'
            f'<td>{html_escape(level)}</td><td>{html_escape(entry["limiting_axis"] or "—")}</td></tr>'
        )

    html = f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Équipe · {team.name}</title>
<style>
  body {{ font-family: system-ui, sans-serif; max-width: 800px; margin: 2rem auto; padding: 0 1rem; }}
  .badge {{ display: inline-block; padding: .2rem .5rem; border-radius: 999px; font-weight: 700; font-size: .85em; }}
  .ok {{ background: #d1f5d8; color: #0b5b23; }}
  .ko {{ background: #ffe3e3; color: #8b1a1a; }}
  table {{ border-collapse: collapse; width: 100%; margin-top: 1rem; }}
  th, td {{ text-align: left; padding: .4rem .6rem; border-bottom: 1px solid #ddd; }}
  th {{ background: #f6f6f6; }}
  code {{ background: #eee; padding: .1rem .3rem; border-radius: 3px; font-size: .85em; }}
</style>
</head>
<body>
<h1>Équipe · {team.name}</h1>
<p><em>Exporté le {datetime.now().strftime('%Y-%m-%d %H:%M')}</em></p>

<h2>Membres</h2>
<table>
  <tr><th>Nom</th><th>Slug</th><th>Niveau</th><th>Axe</th><th>Confiance</th></tr>
  {''.join(rows)}
</table>

<h2>Historique</h2>
<table>
  <tr><th>Date</th><th>Membre</th><th>Niveau</th><th>Axe</th></tr>
  {''.join(history_rows)}
</table>

<p style="margin-top:2rem;color:#666;font-size:.9em;">
<em>Données techniques déclarées uniquement. Aucune donnée personnelle, aucun neurotype demandé ni inféré.</em>
</p>
</body>
</html>"""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    return path