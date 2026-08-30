# Copyright 2026 Romy Alula — MIT License
"""Dashboard HTML de calibration : visualisation Patapon des verdicts vs attendus.

Génère un dashboard avec :
- Carte du monde (nœuds par profil)
- Tableau de preuve verdicts vs attendus
- Badge de calibration
- Détail par axe
"""

from __future__ import annotations

from html import escape

from .calibrate_core import CalibrationResult
from .model import Level, axis_label, level_label


LEVEL_COLORS: dict[Level, dict[str, str]] = {
    Level.WHITE: {'bg': '#e8e8e8', 'fg': '#666', 'accent': '#999', 'icon': '❖'},
    Level.RED: {'bg': '#fde8e8', 'fg': '#c0392b', 'accent': '#e74c3c', 'icon': '🔺'},
    Level.BLUE: {'bg': '#e8f0fd', 'fg': '#2471a3', 'accent': '#3498db', 'icon': '🔹'},
    Level.GREEN: {'bg': '#e8fde8', 'fg': '#1e8449', 'accent': '#27ae60', 'icon': '🟢'},
    Level.COPPER: {'bg': '#fdf2e8', 'fg': '#b7950b', 'accent': '#d4ac0d', 'icon': '🥉'},
    Level.SILVER: {'bg': '#f0f0f8', 'fg': '#7f8c8d', 'accent': '#95a5a6', 'icon': '🥈'},
    Level.GOLD: {'bg': '#fdf8e8', 'fg': '#b7950b', 'accent': '#f1c40f', 'icon': '🥇'},
}

LEVEL_BY_NAME: dict[str, Level] = {l.name: l for l in Level}


def _render_profile_node(name: str, obtained: str | None, expected: str | None, status: str) -> str:
    """Nœud Patapon pour un profil."""
    is_ok = status == 'OK'
    color = '#3fb950' if is_ok else '#f85149'
    icon = '✅' if is_ok else '❌'

    obtained_level = LEVEL_BY_NAME.get(obtained) if obtained and obtained != 'UNDECIDED' else None
    expected_level = LEVEL_BY_NAME.get(expected) if expected and expected != 'UNDECIDED' else None

    node_color = LEVEL_COLORS.get(obtained_level, LEVEL_COLORS[Level.WHITE])['accent'] if obtained_level else '#ccc'

    return (
        f'<div class="cal-node {"ok" if is_ok else "fail"}">'
        f'<div class="cal-node-icon" style="border-color:{node_color};">'
        f'{icon}</div>'
        f'<div class="cal-node-name">{escape(name)}</div>'
        f'<div class="cal-node-obtained" style="color:{node_color};">{escape(obtained or "UNDECIDED")}</div>'
        f'<div class="cal-node-expected">→ {escape(expected or "—")}</div>'
        f'</div>'
    )


def generate_calibrate_html(result: CalibrationResult) -> str:
    """Génère le dashboard HTML complet de calibration."""
    success_rate = ((result.total - result.errors) / result.total * 100) if result.total > 0 else 0
    is_perfect = result.errors == 0

    badge_cls = 'cal-badge ok' if is_perfect else 'cal-badge ko'
    badge_text = f'{result.total}/{result.total} · CALIBRÉ ✅' if is_perfect else f'{result.total - result.errors}/{result.total} · {result.errors} erreur(s)'

    profile_nodes = ''.join(
        _render_profile_node(r.name, r.obtained, r.expected, r.status)
        for r in result.rows
    )

    # Table rows
    table_rows = []
    for r in result.rows:
        icon = '✅' if r.status == 'OK' else '❌' if r.status == 'FAIL' else '⏭️'
        table_rows.append(
            f'<tr>'
            f'<td>{escape(r.name)}</td>'
            f'<td><span class="level-pill" style="background:{_level_bg(r.obtained)};color:{_level_fg(r.obtained)};">'
            f'{escape(r.obtained or "—")}</span></td>'
            f'<td><span class="level-pill" style="background:{_level_bg(r.expected)};color:{_level_fg(r.expected)};">'
            f'{escape(r.expected or "—")}</span></td>'
            f'<td>{icon} {escape(r.detail)}</td>'
            f'</tr>'
        )

    # Axis detail for each profile
    axis_cards = []
    for r in result.rows:
        if r.axis_scores:
            ax_rows = []
            for a in r.axis_scores:
                label = axis_label(a.axe)
                lvl = level_label(a.level)
                conf = f'{a.confidence:.0%}' if a.level is not None else '—'
                ax_rows.append(
                    f'<tr><td>{escape(label)}</td><td>{lvl}</td><td>{conf}</td></tr>'
                )
            axis_cards.append(
                f'<div class="axis-card">'
                f'<h4>{escape(r.name)}</h4>'
                f'<table><tr><th>Axe</th><th>Niveau</th><th>Confiance</th></tr>'
                + ''.join(ax_rows) +
                f'</table></div>'
            )

    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Calibration AIDD · LAIVEL UP</title>
<link rel="stylesheet" href="https://fonts.bunny.net/css?family=Inter:400,500,600,700&display=swap">
<style>
  :root {{
    --bg: #0d1117;
    --surface: #161b22;
    --surface-2: #1c2333;
    --border: #30363d;
    --text: #e6edf3;
    --text-dim: #8b949e;
    --accent: #58a6ff;
    --success: #3fb950;
    --danger: #f85149;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Inter', system-ui, sans-serif;
    background: var(--bg);
    color: var(--text);
    max-width: 900px;
    margin: 0 auto;
    padding: 2rem 1.5rem;
    line-height: 1.6;
  }}
  h1 {{ font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem; }}
  h2 {{ font-size: 1.3rem; font-weight: 600; margin: 2rem 0 1rem; color: var(--accent); }}
  h4 {{ font-size: 0.95rem; font-weight: 600; margin-bottom: 0.5rem; }}

  .cal-badge {{
    display: inline-block;
    padding: 0.4rem 1rem;
    border-radius: 999px;
    font-weight: 700;
    font-size: 1.1rem;
    margin: 1rem 0;
  }}
  .cal-badge.ok {{ background: rgba(63,185,80,0.15); color: var(--success); border: 1px solid var(--success); }}
  .cal-badge.ko {{ background: rgba(248,81,73,0.15); color: var(--danger); border: 1px solid var(--danger); }}

  .success-bar {{
    height: 8px;
    background: var(--surface-2);
    border-radius: 4px;
    overflow: hidden;
    margin: 1rem 0;
  }}
  .success-fill {{
    height: 100%;
    background: linear-gradient(90deg, var(--success), var(--accent));
    border-radius: 4px;
    transition: width 0.8s ease;
  }}

  /* World map */
  .cal-world {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1.5rem 0;
  }}
  .cal-world-title {{
    font-size: 1rem;
    color: var(--text-dim);
    margin-bottom: 1rem;
    text-align: center;
  }}
  .cal-world-map {{
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    overflow-x: auto;
    padding: 1rem 0;
    justify-content: center;
    flex-wrap: wrap;
  }}
  .cal-node {{
    display: flex;
    flex-direction: column;
    align-items: center;
    min-width: 80px;
    padding: 0.5rem;
    border-radius: 8px;
    border: 1px solid var(--border);
    background: var(--surface-2);
    transition: all 0.3s ease;
  }}
  .cal-node.ok {{ border-color: var(--success); }}
  .cal-node.fail {{ border-color: var(--danger); }}
  .cal-node-icon {{
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    border: 2px solid;
    margin-bottom: 0.4rem;
  }}
  .cal-node-name {{ font-size: 0.8rem; font-weight: 600; margin-bottom: 0.2rem; }}
  .cal-node-obtained {{ font-size: 0.75rem; font-weight: 700; }}
  .cal-node-expected {{ font-size: 0.7rem; color: var(--text-dim); }}

  /* Table */
  .cal-table {{
    width: 100%;
    border-collapse: collapse;
    margin: 1rem 0;
  }}
  .cal-table th, .cal-table td {{
    padding: 0.6rem 0.8rem;
    text-align: left;
    border-bottom: 1px solid var(--border);
  }}
  .cal-table th {{
    background: var(--surface-2);
    font-weight: 600;
    font-size: 0.85rem;
    color: var(--text-dim);
  }}
  .cal-table tr:hover {{ background: var(--surface); }}

  .level-pill {{
    display: inline-block;
    padding: 0.15rem 0.5rem;
    border-radius: 4px;
    font-size: 0.8rem;
    font-weight: 600;
  }}

  .axis-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin: 0.6rem 0;
  }}
  .axis-card table {{ width: 100%; }}
  .axis-card th, .axis-card td {{
    padding: 0.3rem 0.5rem;
    font-size: 0.85rem;
  }}

  .report-footer {{
    margin-top: 3rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border);
    text-align: center;
    font-size: 0.8rem;
    color: var(--text-dim);
  }}
  .report-footer a {{ color: var(--accent); text-decoration: none; }}

  @media (max-width: 600px) {{
    body {{ padding: 1rem; }}
    .cal-world-map {{ flex-direction: column; align-items: center; }}
  }}
</style>
</head>
<body>
<main>
  <h1>Calibration AIDD</h1>
  <p style="color:var(--text-dim);">LAIVEL UP · Comparaison des verdicts aux niveaux attendus</p>

  <div class="{badge_cls}">{badge_text}</div>

  <div class="success-bar">
    <div class="success-fill" style="width:{success_rate:.0f}%;"></div>
  </div>

  <div class="cal-world">
    <h2 class="cal-world-title">Profils calibrés</h2>
    <div class="cal-world-map">
      {profile_nodes}
    </div>
  </div>

  <h2>Tableau de preuve</h2>
  <table class="cal-table">
    <tr><th>Profil</th><th>Obtenu</th><th>Attendu</th><th>Statut</th></tr>
    {''.join(table_rows)}
  </table>

  <h2>Détail par axe et par profil</h2>
  {''.join(axis_cards)}

  <div class="report-footer">
    Généré par <strong>LAIVEL UP</strong> · Calibration
    <a href="https://github.com/ai-driven-dev/laivel-up" target="_blank" rel="noopener">référentiel AIDD</a>
  </div>
</main>
</body>
</html>
"""


def _level_bg(name: str | None) -> str:
    lvl = LEVEL_BY_NAME.get(name) if name else None
    return LEVEL_COLORS.get(lvl, LEVEL_COLORS[Level.WHITE])['bg'] if lvl else '#1c2333'


def _level_fg(name: str | None) -> str:
    lvl = LEVEL_BY_NAME.get(name) if name else None
    return LEVEL_COLORS.get(lvl, LEVEL_COLORS[Level.WHITE])['fg'] if lvl else '#8b949e'
