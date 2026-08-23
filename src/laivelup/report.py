# Copyright 2026 Romy Alula — MIT License
"""Rapport de verdict : Markdown (source de vérité) + HTML (relecture humaine).

Transparence : chaque rapport documente les données utilisées, la méthode
(min() sur 4 axes), les sources des preuves et les limites de l'évaluation.
Aucun neurotype n'est mesuré, demandé ni inféré.
"""

from __future__ import annotations

import hashlib
from html import escape
from pathlib import Path

from .model import Verdict, axis_label, level_label


def render_markdown(verdict: Verdict) -> str:
    lines = [f"# Verdict AIDD · {verdict.name}"]
    if verdict.data_errors:
        lines.append("\n**Données invalides :** l'évaluation refuse de trancher.")
        for e in verdict.data_errors:
            lines.append(f"\n- {e}")
    elif verdict.decided:
        lines.append(f"\n**Niveau :** {level_label(verdict.level)}")
    else:
        lines.append("\n**Niveau :** non déterminable · données insuffisantes ou contradictoires")
    if verdict.limiting_axis:
        lines.append(f"\n**Axe plancher / faible :** `{verdict.limiting_axis}`")
    if verdict.axis_scores:
        lines.append("\n## Axes")
        lines.append("\n| Axe | Niveau | Confiance | Éléments observés |")
        lines.append("|---|---|---|---|")
        for a in verdict.axis_scores:
            label = level_label(a.level)
            conf = f"{a.confidence:.0%}" if a.level is not None else "—"
            ev = ", ".join(a.evidence)
            if a.variance:
                ev = f"{ev} · variance : {a.variance}"
            lines.append(f"| {axis_label(a.axe)} | {label} | {conf} | {ev} |")
    if verdict.red_flags:
        lines.append("\n## Red flags (hypothèses à vérifier)")
        for f in verdict.red_flags:
            lines.append(f"\n- **{f.titre}** ({'⚠' * f.severite}) · {f.constat} _({f.source})_")
            if f.question:
                lines.append(f"  → Question : {f.question}")
    if verdict.next_steps:
        lines.append("\n## Comment monter d'un cran / point de levée d'incertitude")
        for n in verdict.next_steps:
            lines.append(f"\n- {n}")
    lines.append(
        "\n## Transparence\n"
        "\n- **Données utilisées :** traces techniques déclarées seulement (commits, PR, "
        "contexte). Aucune donnée personnelle, aucun neurotype demandé ni inféré.\n"
        "- **Méthode :** score discret par axe puis règle officielle « tous les axes le "
        "sont » (`min()`), avec une confiance par axe. Une confiance faible ou des "
        "données contradictoires conduisent au refus de trancher plutôt qu'à un verdict "
        "arbitraire.\n"
        "- **Limites :** la séniorité, la qualité de code et le neurotype ne sont pas "
        "mesurés. Un niveau reflète une adoption observée, pas une valeur humaine.\n"
        "- **Sources :** référentiel AIDD officiel "
        "(https://github.com/ai-driven-dev/laivel-up)."
    )
    return "\n".join(lines) + "\n"


def render_html(verdict: Verdict) -> str:
    if verdict.data_errors:
        badge = "Données invalides : refus de trancher"
        kelas = "ko"
    elif verdict.decided:
        badge = level_label(verdict.level)
        kelas = "ok"
    else:
        badge = "Données insuffisantes : refus de trancher"
        kelas = "ko"
    limiting = (
        f"<p>Axe plancher / faible : <strong>{escape(verdict.limiting_axis)}</strong></p>"
        if verdict.limiting_axis
        else ""
    )
    errors_html = "".join(f'<div class="flag">{escape(e)}</div>' for e in verdict.data_errors)
    errors_section = f"<h2>Données invalides</h2>{errors_html}" if verdict.data_errors else ""
    rows = []
    for a in verdict.axis_scores:
        label = level_label(a.level)
        conf = f"{a.confidence:.0%}" if a.level is not None else "—"
        ev = escape(", ".join(a.evidence))
        if a.variance:
            ev = f"{ev} · variance : {escape(a.variance)}"
        rows.append(
            f"<tr><td>{escape(axis_label(a.axe))}</td><td>{label}</td>"
            f"<td>{conf}</td><td>{ev}</td></tr>"
        )
    flags_html = "".join(
        f'<div class="flag"><strong>{escape(f.titre)}</strong> · {escape(f.constat)} '
        f"<em>({escape(f.source)})</em>"
        + (f"<div><em>Question : {escape(f.question)}</em></div>" if f.question else "")
        + "</div>"
        for f in verdict.red_flags
    )
    flags_section = f"<h2>Red flags (hypothèses à vérifier)</h2>{flags_html}" if verdict.red_flags else ""
    next_html = "".join(f'<div class="next">{escape(n)}</div>' for n in verdict.next_steps)
    next_section = f"<h2>Monter d'un cran / levée d'incertitude</h2>{next_html}" if verdict.next_steps else ""
    transparency = (
        "<h2>Transparence</h2>"
        "<p><strong>Données utilisées :</strong> traces techniques déclarées (commits, PR, "
        "contexte). Aucune donnée personnelle, aucun neurotype demandé ni inféré.</p>"
        "<p><strong>Méthode :</strong> score discret par axe puis règle « tous les axes le sont » "
        "(<code>min()</code>) avec une confiance par axe. Données faibles ou contradictoires "
        "&rarr; refus de trancher.</p>"
        "<p><strong>Limites :</strong> séniorité, qualité de code et neurotype non mesurés. "
        "Un niveau reflète une adoption, jamais une valeur humaine.</p>"
    )

    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Verdict AIDD · {escape(verdict.name)}</title>
<style>
  body {{ font-family: system-ui, sans-serif; max-width: 720px; margin: 3rem auto; padding: 0 1rem; color: #1a1a1a; }}
  h1 {{ font-size: 1.5rem; }}
  .badge {{ display: inline-block; padding: .3rem .7rem; border-radius: 999px; font-weight: 700; }}
  .ok {{ background: #d1f5d8; color: #0b5b23; }}
  .ko {{ background: #ffe3e3; color: #8b1a1a; }}
  table {{ border-collapse: collapse; width: 100%; margin-top: 1rem; }}
  th, td {{ text-align: left; padding: .5rem; border-bottom: 1px solid #ddd; vertical-align: top; }}
  th {{ background: #f6f6f6; }}
  .flag {{ border-left: 4px solid #c0392b; padding: .5rem .8rem; margin-top: .5rem; background: #fdf3f3; }}
  .next {{ border-left: 4px solid #2980b9; padding: .5rem .8rem; margin-top: .5rem; background: #f4f9fd; }}
  code {{ background: #eee; padding: .1rem .3rem; border-radius: 3px; }}
</style>
</head>
<body>
<main>
  <h1>Verdict AIDD · {escape(verdict.name)}</h1>
  <p><span class="badge {kelas}">{badge}</span></p>
  {limiting}
  {errors_section}
  <table>
    <tr><th>Axe</th><th>Niveau</th><th>Confiance</th><th>Éléments observés</th></tr>
    {''.join(rows)}
  </table>
  {flags_section}
  {next_section}
  {transparency}
</main>
</body>
</html>
"""


def write_reports(verdict: Verdict, out_dir: Path, with_html: bool = True) -> tuple[Path, Path | None]:
    out_dir.mkdir(parents=True, exist_ok=True)
    safe = _slug(verdict.name)
    md = out_dir / f"{safe}.md"
    md.write_text(render_markdown(verdict), encoding="utf-8")
    html = None
    if with_html:
        html = out_dir / f"{safe}.html"
        html.write_text(render_html(verdict), encoding="utf-8")
    return md, html


def _slug(name: str) -> str:
    # Slug court et stable, sans conserver de nom humain lisible (prudence RGPD).
    digest = hashlib.sha256(name.encode("utf-8")).hexdigest()[:8]
    cleaned = "".join(c if c.isalnum() else "-" for c in name.lower()).strip("-") or "profil"
    return f"{cleaned[:32]}-{digest}"
