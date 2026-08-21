# Copyright 2026 Romy Alula — MIT License
"""Team Tracker : gestion d'équipes, journalisation, réévaluation, export multi-format.

Permet de créer des équipes, évaluer leurs membres, suivre l'évolution dans le temps,
et exporter les résultats en HTML, Markdown, CSV ou JSON.

Équité structurelle : les équipes ne stockent aucune donnée sensible.
Le pseudo-anonyme (slug RGPD) protège l'identité dans les rapports partagés.
"""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TextIO

from .model import Level, ProfileData, Verdict
from .scoring import evaluate


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


@dataclass
class Team:
    """Représentation d'une équipe avec son historique d'évaluations."""

    name: str
    members: dict[str, MemberSnapshot] = field(default_factory=dict)
    history: list[dict] = field(default_factory=list)


def _slug(name: str) -> str:
    """Pseudo-anonyme RGPD pour le partage de rapports."""
    digest = hashlib.sha256(name.encode("utf-8")).hexdigest()[:8]
    cleaned = "".join(c if c.isalnum() else "-" for c in name.lower()).strip("-") or "membre"
    return f"{cleaned[:32]}-{digest}"


def create_team(name: str, member_names: list[str]) -> Team:
    """Crée une équipe avec des membres pseudo-anonymisés."""
    team = Team(name=name)
    for member_name in member_names:
        slug = _slug(member_name)
        team.members[slug] = MemberSnapshot(
            slug=slug,
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

    verdict = evaluate(profile)
    member = team.members[slug]

    snapshot = MemberSnapshot(
        slug=slug,
        name=member.name,
        level=verdict.level,
        limiting_axis=verdict.limiting_axis,
        confidence=(
            max(a.confidence for a in verdict.axis_scores)
            if verdict.axis_scores
            else 0.0
        ),
        red_flags_count=len(verdict.red_flags),
        next_steps_count=len(verdict.next_steps),
    )
    team.members[slug] = snapshot

    # Journaliser dans l'historique
    team.history.append({
        "timestamp": snapshot.timestamp,
        "slug": slug,
        "level": verdict.level.name if verdict.level else None,
        "limiting_axis": verdict.limiting_axis,
        "confidence": snapshot.confidence,
    })

    return verdict


def export_json(team: Team, path: Path) -> Path:
    """Exporte l'état de l'équipe en JSON."""
    data = {
        "team": team.name,
        "exported_at": datetime.now().isoformat(),
        "members": {
            slug: {
                "name": m.name,
                "slug": m.slug,
                "level": m.level.name if m.level else None,
                "limiting_axis": m.limiting_axis,
                "confidence": m.confidence,
                "timestamp": m.timestamp,
            }
            for slug, m in team.members.items()
        },
        "history": team.history,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def export_markdown(team: Team, path: Path) -> Path:
    """Exporte un rapport Markdown de l'équipe."""
    lines = [f"# Équipe · {team.name}"]
    lines.append(f"\n*Exporté le {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")

    lines.append("\n## Membres\n")
    lines.append("| Membre | Slug | Niveau | Axe plancher | Confiance |")
    lines.append("|--------|------|--------|--------------|-----------|")
    for slug, m in team.members.items():
        level = m.level.name if m.level else "—"
        axis = m.limiting_axis or "—"
        conf = f"{m.confidence:.0%}"
        lines.append(f"| {m.name} | `{slug}` | {level} | {axis} | {conf} |")

    if team.history:
        lines.append("\n## Historique\n")
        lines.append("| Date | Membre | Niveau | Axe | Confiance |")
        lines.append("|------|--------|--------|-----|-----------|")
        for entry in team.history[-20:]:  # Dernières 20 entrées
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
    """Exporte les données de l'équipe en CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "slug", "level", "limiting_axis", "confidence", "timestamp"])
        for slug, m in team.members.items():
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
    """Exporte un rapport HTML de l'équipe."""
    rows = []
    for slug, m in team.members.items():
        level = m.level.name if m.level else "—"
        conf = f"{m.confidence:.0%}"
        kelas = "ok" if m.level and m.level >= Level.BLUE else "ko"
        rows.append(
            f'<tr><td>{m.name}</td><td><code>{slug}</code></td>'
            f'<td><span class="badge {kelas}">{level}</span></td>'
            f'<td>{m.limiting_axis or "—"}</td><td>{conf}</td></tr>'
        )

    history_rows = []
    for entry in team.history[-20:]:
        ts = entry["timestamp"][:10]
        level = entry["level"] or "—"
        history_rows.append(
            f'<tr><td>{ts}</td><td>{entry["slug"][:16]}...</td>'
            f'<td>{level}</td><td>{entry["limiting_axis"] or "—"}</td></tr>'
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