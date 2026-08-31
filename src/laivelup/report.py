# Copyright 2026 Romy Alula — MIT License
"""Rapport de verdict : Markdown (source de vérité) + HTML (relecture humaine).

Transparence : chaque rapport documente les données utilisées, la méthode
(min() sur 4 axes), les sources des preuves et les limites de l'évaluation.
Aucun neurotype n'est mesuré, demandé ni inféré.
"""

from __future__ import annotations

from html import escape
from pathlib import Path

from .model import Level, Verdict, axis_label, level_label
from .utils import slug

# --- Glossaire pédagogique (termes AIDD → définitions accessibles) --------
GLOSSARY: dict[str, str] = {
    'Context Engineering': (
        "La mémoire que l'IA lit avant de coder : conventions, architecture, "
        "décisions passées. C'est le minimum syndical pour que l'IA produise du code cohérent."
    ),
    'Behavior': (
        "Les règles et agents qui contrôlent comment l'IA agit : "
        "code review, hooks, guardrails. C'est le 'comment' au lieu du 'quoi'."
    ),
    'Retry Loops': (
        "Un script relance l'IA tant qu'une commande du projet échoue. "
        "L'IA corrige elle-même ses erreurs sans intervention humaine."
    ),
    'Harness': (
        "L'ensemble du harnais autour du modèle : Context Engineering + Behavior + Retry Loops. "
        "Plus le harnais est complet, moins l'humain doit intervenir."
    ),
    'Intervention': (
        "Quand l'humain intervient dans le travail de l'IA. Cadrer = choisir la tâche et "
        "dire ce qui est attendu. Monter d'un niveau = reprendre moins pour atteindre la qualité."
    ),
    'Reprise (proportion de)': (
        "La part de PR livrées avec l'IA que l'humain a dû reprendre après coup : "
        'corriger, retoucher, refaire. La grille officielle dit « commits correctifs ». '
        "70 % : sur 10 PR, 7 reprises · cellule Red de l'axe Intervention. "
        "La valeur vient des traces du profil, jamais d'une réponse au questionnaire seule."
    ),
    'Taille (Size)': (
        "La taille habituelle des features livrées avec l'IA : S (petite), M (moyenne), "
        "L (multi-étapes), XL (multi-modules). Pas la plus grosse jamais faite, l'habituel."
    ),
    'En parallèle': (
        'Combien de chantiers avancent en même temps, habituellement. '
        "Un pic isolé ne compte pas : c'est la pratique régulière."
    ),
    'Règle AND': (
        "Un niveau n'est atteint que si TOUTES ses cellules sont satisfaites. "
        "L'axe le plus faible ('axe plancher') détermine le niveau global."
    ),
    'Refus de deviner': (
        "Quand les données manquent ou se contredisent, l'outil refuse de trancher "
        'et pose des questions ciblées plutôt que de deviner. Équité structurelle.'
    ),
}

# --- Références curatées (articles AIDD, manifesto, ressources) ----------
REFERENCES: list[dict[str, str]] = [
    {
        'url': 'https://ai-driven-development.org',
        'title': 'Manifesto for AI-Driven Development',
        'desc': "Le manifeste fondateur — principes et niveaux d'adoption AIDD.",
    },
    {
        'url': 'https://github.com/ai-driven-dev/laivel-up/blob/main/levels/aidd.md',
        'title': 'Référentiel AIDD officiel',
        'desc': 'La grille complète : 4 axes × 7 niveaux, règles et exemples.',  # noqa: RUF001
    },
    {
        'url': 'https://github.com/EveryInc/compound-engineering',
        'title': 'Compound Engineering',
        'desc': 'Le framework de skills qui structure le développement assisté par IA.',
    },
]

# --- Couleurs par niveau (Patapon-inspired palette) ----------
LEVEL_COLORS: dict[Level, dict[str, str]] = {
    Level.WHITE: {'bg': '#e8e8e8', 'fg': '#666', 'accent': '#999', 'icon': '❖'},
    Level.RED: {'bg': '#fde8e8', 'fg': '#c0392b', 'accent': '#e74c3c', 'icon': '🔺'},
    Level.BLUE: {'bg': '#e8f0fd', 'fg': '#2471a3', 'accent': '#3498db', 'icon': '🔹'},
    Level.GREEN: {'bg': '#e8fde8', 'fg': '#1e8449', 'accent': '#27ae60', 'icon': '🟢'},
    Level.COPPER: {'bg': '#fdf2e8', 'fg': '#b7950b', 'accent': '#d4ac0d', 'icon': '🥉'},
    Level.SILVER: {'bg': '#f0f0f8', 'fg': '#7f8c8d', 'accent': '#95a5a6', 'icon': '🥈'},
    Level.GOLD: {'bg': '#fdf8e8', 'fg': '#b7950b', 'accent': '#f1c40f', 'icon': '🥇'},
}


def _glossary_tooltip(term: str) -> str:
    """Renvoie un <span> avec tooltip pour un terme du glossaire."""
    defn = GLOSSARY.get(term)
    if not defn:
        return escape(term)
    return (
        f'<span class="glossary-term" data-tooltip="{escape(defn)}">'
        f'{escape(term)}<span class="glossary-icon">?</span></span>'
    )


def render_markdown(verdict: Verdict) -> str:
    lines = [f'# Verdict AIDD · {verdict.name}']
    if verdict.data_errors:
        lines.append("\n**Données invalides :** l'évaluation refuse de trancher.")
        for e in verdict.data_errors:
            lines.append(f'\n- {e}')
    elif verdict.decided:
        lines.append(f'\n**Niveau :** {level_label(verdict.level)}')
    else:
        lines.append('\n**Niveau :** non déterminable · données insuffisantes ou contradictoires')
    if verdict.limiting_axis:
        lines.append(f'\n**Axe plancher / faible :** {axis_label(verdict.limiting_axis)}')
    if verdict.axis_scores:
        lines.append('\n## Axes')
        lines.append('\n| Axe | Niveau | Confiance | Éléments observés |')
        lines.append('|---|---|---|---|')
        for a in verdict.axis_scores:
            label = level_label(a.level)
            conf = f'{a.confidence:.0%}' if a.level is not None else '—'
            ev = ', '.join(a.evidence)
            if a.variance:
                ev = f'{ev} · variance : {a.variance}'
            lines.append(f'| {axis_label(a.axe)} | {label} | {conf} | {ev} |')
    if verdict.red_flags:
        lines.append('\n## Alertes (hypothèses à vérifier)')
        for f in verdict.red_flags:
            lines.append(f'\n- **{f.titre}** ({"⚠" * f.severite}) · {f.constat} _({f.source})_')
            if f.question:
                lines.append(f'  → Question : {f.question}')
    if verdict.next_steps:
        lines.append("\n## Comment monter d'un cran / point de levée d'incertitude")
        for n in verdict.next_steps:
            lines.append(f'\n- {n}')
    lines.append(
        '\n## Transparence\n'
        '\n- **Données utilisées :** traces techniques déclarées seulement (commits, PR, '
        'contexte). Aucune donnée personnelle, aucun neurotype demandé ni inféré.\n'
        '- **Méthode :** score discret par axe puis règle officielle « tous les axes le '
        'sont » (`min()`), avec une confiance par axe. Une confiance faible ou des '
        "données contradictoires conduisent au refus de trancher plutôt qu'à un verdict "
        'arbitraire.\n'
        '- **Limites :** la séniorité, la qualité de code et le neurotype ne sont pas '
        'mesurés. Un niveau reflète une adoption observée, pas une valeur humaine.\n'
        '- **Sources :** référentiel AIDD officiel '
        '(https://github.com/ai-driven-dev/laivel-up).'
    )
    return '\n'.join(lines) + '\n'


def _render_world_map(verdict: Verdict) -> str:
    """Carte du monde Patapon-style : chaque niveau = un nœud, axes = étapes internes."""
    current = verdict.level
    nodes = []
    for lvl in Level:
        color = LEVEL_COLORS[lvl]
        is_current = current is not None and lvl == current
        is_unlocked = current is not None and lvl.value <= current.value

        state = 'locked'
        if is_unlocked:
            state = 'unlocked'
        if is_current:
            state = 'current'

        badge_html = ''
        if is_current:
            badge_html = (
                f'<span class="achievement-badge" style="background:{color["accent"]};'
                f'color:#fff;">NIVEAU DÉBLOQUÉ</span>'
            )

        # Sous-nœuds : les 4 axes comme étapes internes du monde
        axis_stages = ''
        if is_unlocked or is_current:
            for a in verdict.axis_scores:
                if a.axe:
                    ax_color = (
                        color['accent']
                        if a.level is not None and a.level.value >= lvl.value
                        else '#ddd'
                    )
                    ax_label = axis_label(a.axe)
                    ax_check = '✓' if a.level is not None and a.level.value >= lvl.value else '○'
                    axis_stages += (
                        f'<span class="axis-stage" style="border-color:{ax_color};'
                        f'color:{ax_color};">{ax_check} {ax_label}</span>'
                    )

        nodes.append(
            f'<div class="world-node {state}" data-level="{lvl.name}">'
            f'<div class="node-icon" style="background:{color["bg"]};'
            f'border-color:{color["accent"]};color:{color["fg"]};">'
            f'{color["icon"]}</div>'
            f'<div class="node-label">{lvl.name}</div>'
            f'{axis_stages}'
            f'{badge_html}'
            f'</div>'
        )

    # Connexions entre les nœuds
    connectors = '<div class="world-connector"></div>'.join(
        ['<div class="world-connector-line"></div>' for _ in range(len(Level) - 1)]
    )

    return (
        '<div class="patapon-world">'
        '<h2 class="world-title">Carte de progression AIDD</h2>'
        '<div class="world-map">'
        + f'<div class="connector">{connectors}</div>'.join(nodes)  # simplify: join with empty
        + '</div>'
        '</div>'
    )


def _render_progress_bar(verdict: Verdict) -> str:
    """Barre de progression stylisée avec paliers White→Gold."""
    current = verdict.level
    if current is None:
        pct = 0
        current_name = 'Undécis'
    else:
        pct = int((current.value / 6) * 100)
        current_name = current.name

    steps = []
    for lvl in Level:
        color = LEVEL_COLORS[lvl]
        is_unlocked = current is not None and lvl.value <= current.value
        cls = 'step unlocked' if is_unlocked else 'step locked'
        steps.append(
            f'<div class="{cls}" style="flex:1; text-align:center;">'
            f'<div class="step-dot" style="background:{color["accent"] if is_unlocked else "#ccc"};'
            f'width:12px;height:12px;border-radius:50%;margin:0 auto;"></div>'
            f'<div class="step-label" style="font-size:.7rem;color:{color["fg"] if is_unlocked else "#999"};">'
            f'{color["icon"]} {lvl.name}</div>'
            f'</div>'
        )

    return (
        '<div class="progress-bar-container">'
        f'<h2 class="progress-title">Progression · {current_name}</h2>'
        '<div class="progress-track">'
        f'<div class="progress-fill" style="width:{pct}%;"></div>'
        '</div>'
        '<div class="progress-steps">' + ''.join(steps) + '</div>'
        '</div>'
    )


def _render_axis_detail(verdict: Verdict) -> str:
    """Détail par axe avec encadré pédagogique 'Pourquoi ce niveau ?'."""
    if not verdict.axis_scores:
        return ''

    rows = []
    for a in verdict.axis_scores:
        label = axis_label(a.axe)
        lvl = level_label(a.level)
        conf = f'{a.confidence:.0%}' if a.level is not None else '—'
        ev = ', '.join(a.evidence) if a.evidence else 'Aucune trace'
        if a.variance:
            ev = f'{ev} · variance : {escape(a.variance)}'

        # Encadré "Pourquoi ce niveau ?" pour chaque axe
        why = _why_this_level(a.axe, a.level, a.evidence)

        # 10.1.b (adapté) : la demande initiale visait une <table> avec
        # <caption>/scope="col", mais ce rendu n'utilise plus de table —
        # remplacée par ces cartes par axe. L'équivalent d'accessibilité pour
        # une carte est un rôle ARIA list/listitem + un aria-label résumant
        # la carte entière, plutôt que des en-têtes de colonnes qui n'existent
        # plus.
        card_label = escape(f'{label} : {lvl}, confiance {conf}')
        rows.append(
            f'<div class="axis-card" role="listitem" aria-label="{card_label}">'
            f'<div class="axis-card-header">'
            f'<span class="axis-name">{label}</span>'
            f'<span class="axis-level" style="color:{_level_color(a.level)};">{lvl}</span>'
            f'</div>'
            f'<div class="axis-confidence">Confiance : {conf}</div>'
            f'<div class="axis-evidence">{escape(ev)}</div>'
            f'<div class="axis-why"><strong>Pourquoi ce niveau ?</strong> {why}</div>'
            f'</div>'
        )

    return (
        '<div class="axis-details" role="list" aria-label="D\u00e9tail par axe d\u0027\u00e9valuation">'
        '<h2>Détail par axe</h2>' + ''.join(rows) + '</div>'
    )


def _why_this_level(axe: str, level: Level | None, _evidence: list[str]) -> str:
    """Génère une explication pédagogique du niveau pour un axe donné."""
    if level is None:
        return 'Données insuffisantes pour trancher sur cet axe.'

    explanations = {
        'size': {
            Level.RED: "Les PR observées sont de taille S. C'est le niveau d'entrée : l'IA aide sur des features simples.",
            Level.BLUE: "Les PR sont de taille M : l'IA gère des features de complexité moyenne. Bonne base.",
            Level.GREEN: "Les PR sont de taille L : l'IA enchaîne plusieurs étapes dans une même feature.",
            Level.COPPER: "Les PR alternent L et XL. L'IA produit des features multi-modules régulièrement.",
            Level.SILVER: "L'IA livre des features L-XL sans intervention humaine sur le contenu.",
            Level.GOLD: "L'IA livre des features XL autonomement, plusieurs fois par jour.",
        },
        'harness': {
            Level.RED: "Pas de contexte versionné. L'IA repart de zéro à chaque session.",
            Level.BLUE: "Une mémoire projet existe et est maintenue. L'IA lit le contexte avant de coder.",
            Level.GREEN: "Règles et agents sont versionnés. L'IA suit des conventions explicites.",
            Level.COPPER: "Le harnais est complet : contexte + behavior. L'IA est encadrée.",
            Level.SILVER: "Des retry loops relancent l'IA automatiquement en cas d'échec.",
            Level.GOLD: "Le harnais maximal : contexte + behavior + retry loops. L'IA est autonome.",
        },
        'intervention': {
            Level.RED: "Reprise sur la majorité des PR. L'humain corrige beaucoup après l'IA.",
            Level.BLUE: "Reprise sur une partie des PR. L'humain intervient moins souvent.",
            Level.GREEN: "Intervention aux étapes clés seulement. L'humain cadre, l'IA exécute.",
            Level.COPPER: "Intervention ponctuelle. L'humain ne reprend presque jamais.",
            Level.SILVER: "Aucune intervention une fois la tâche cadrée. L'IA gère tout.",
            Level.GOLD: 'Même le cadrage est compris. Les agents prennent les tâches en autonomie.',
        },
        'parallel': {
            Level.WHITE: "Aucun projet en parallèle. Pas d'activité AIDD observée.",
            Level.RED: "Un seul projet. L'IA aide sur un chantier à la fois.",
            Level.BLUE: 'Un seul projet, mais avec plus de complexité.',
            Level.GREEN: "Deux à trois chantiers en parallèle. L'IA suit plusieurs lignes.",
            Level.COPPER: "Trois chantiers ou plus, tous menés au bout. L'IA gère la charge.",
            Level.SILVER: "Trois chantiers ou plus, tous menés au bout. L'IA gère la charge.",
            Level.GOLD: "Trois chantiers ou plus, tous menés au bout. L'IA gère la charge.",
        },
    }

    base = explanations.get(axe, {}).get(level, 'Niveau maintenu.')
    return f'<em>{escape(base)}</em>'


def _level_color(level: Level | None) -> str:
    """Couleur CSS d'un niveau."""
    if level is None:
        return '#999'
    return LEVEL_COLORS[level]['accent']


def _render_pedagogical_section(verdict: Verdict) -> str:
    """Section pédagogique : mini-guide 'Comment progresser' + glossaire + références."""
    # Mini-guide personnalisé
    guide_items = []
    if verdict.limiting_axis:
        axe = verdict.limiting_axis
        level = verdict.level
        if level is not None:
            steps = {
                'size': {
                    Level.RED: 'Passe de features S à M : livre des PR multi-étapes.',
                    Level.BLUE: 'Passe à des features L : enchaîne plusieurs étapes dans une PR.',
                    Level.GREEN: 'Pousse à des features XL multi-modules régulières.',
                    Level.COPPER: 'Maintiens un habituel L-XL, pas seulement un pic.',
                },
                'harness': {
                    Level.WHITE: 'Crée une mémoire projet (contexte) et maintiens-la.',
                    Level.RED: 'Crée une mémoire projet et maintiens-la.',
                    Level.BLUE: 'Versionne règles et agents dans le dépôt.',
                    Level.GREEN: 'Ajoute une boucle de relance automatique.',
                    Level.COPPER: 'Ajoute une boucle de relance automatique.',
                    Level.SILVER: 'Passe la relance en autonomie des agents.',
                },
                'intervention': {
                    Level.RED: 'Réduis la reprise après coup : cadrer avant, corriger moins.',
                    Level.BLUE: 'Interviens seulement aux étapes clés.',
                    Level.GREEN: 'Vise zéro reprise, intervention ponctuelle uniquement.',
                    Level.COPPER: 'Confirme que les agents prennent les tâches en autonomie.',
                    Level.SILVER: 'Confirme que les agents prennent les tâches en autonomie.',
                },
                'parallel': {
                    Level.RED: "Mène 2 chantiers de front et les mène jusqu'au bout.",
                    Level.BLUE: 'Mène 3 chantiers en parallèle, menés au bout.',
                    Level.GREEN: 'Confirme la complétude des 3 chantiers.',
                    Level.COPPER: 'Maintiens 3 chantiers en parallèle, tous menés au bout.',
                    Level.SILVER: 'Maintiens 3 chantiers en parallèle, tous menés au bout.',
                },
            }
            step = steps.get(axe, {}).get(level, 'Maintiens le niveau actuel.')
            guide_items.append(
                f'<div class="guide-item">'
                f'<span class="guide-axe">{escape(axis_label(axe))}</span>'
                f'<span class="guide-step">{escape(step)}</span>'
                f'</div>'
            )

    guide_html = ''
    if guide_items:
        guide_html = (
            '<div class="guide-section">'
            '<h3>Comment progresser vers le niveau suivant</h3>' + ''.join(guide_items) + '</div>'
        )

    # Glossaire
    glossary_items = []
    for term in GLOSSARY:
        defn = GLOSSARY.get(term, '')
        glossary_items.append(
            f'<div class="glossary-item">'
            f'<span class="glossary-term-inline">{escape(term)}</span>'
            f'<span class="glossary-def">{escape(defn)}</span>'
            f'</div>'
        )

    # Références
    ref_items = []
    for ref in REFERENCES:
        ref_items.append(
            f'<div class="ref-item">'
            f'<a href="{escape(ref["url"])}" target="_blank" rel="noopener">{escape(ref["title"])}</a>'
            f'<span class="ref-desc">{escape(ref["desc"])}</span>'
            f'</div>'
        )

    return (
        '<div class="pedagogy">'
        '<h2>Pour aller plus loin</h2>' + guide_html + '<h3>Glossaire AIDD</h3>'
        '<div class="glossary-grid">' + ''.join(glossary_items) + '</div>'
        '<h3>Références curatées</h3>'
        '<div class="ref-grid">' + ''.join(ref_items) + '</div>'
        '</div>'
    )


def render_html(verdict: Verdict) -> str:
    if verdict.data_errors:
        badge_text = 'Données invalides : refus de trancher'
        kelas = 'ko'
    elif verdict.decided:
        badge_text = escape(level_label(verdict.level))
        kelas = 'ok'
    else:
        badge_text = 'Données insuffisantes : refus de trancher'
        kelas = 'ko'

    limiting = (
        f'<p class="limiting-axis">Axe plancher / faible : <strong>{escape(axis_label(verdict.limiting_axis))}</strong></p>'
        if verdict.limiting_axis
        else ''
    )

    errors_html = ''.join(f'<div class="flag">{escape(e)}</div>' for e in verdict.data_errors)
    errors_section = f'<h2>Données invalides</h2>{errors_html}' if verdict.data_errors else ''

    flags_html = ''.join(
        f'<div class="flag">⚠ Vigilance · <strong>{escape(f.titre)}</strong> · {escape(f.constat)} '
        f'<em>({escape(f.source)})</em>'
        + (f'<div><em>Question : {escape(f.question)}</em></div>' if f.question else '')
        + '</div>'
        for f in verdict.red_flags
    )
    flags_section = (
        f'<h2>Alertes (hypothèses à vérifier)</h2>{flags_html}' if verdict.red_flags else ''
    )

    # Next steps section. Préfixe textuel — pas seulement la couleur de bordure
    # — pour rester lisible pour un daltonien ou un lecteur d'écran (10.1.c).
    next_html = ''.join(
        f'<div class="next">→ Piste · {escape(n)}</div>' for n in verdict.next_steps
    )
    next_section = (
        f"<h2>Monter d'un cran / levée d'incertitude</h2>{next_html}" if verdict.next_steps else ''
    )

    transparency = (
        '<h2>Transparence</h2>'
        '<div class="transparency-box">'
        '<p><strong>Données utilisées :</strong> traces techniques déclarées (commits, PR, '
        'contexte). Aucune donnée personnelle, aucun neurotype demandé ni inféré.</p>'
        '<p><strong>Méthode :</strong> score discret par axe puis règle « tous les axes le sont » '
        '(<code>min()</code>) avec une confiance par axe. Données faibles ou contradictoires '
        '&rarr; refus de trancher.</p>'
        '<p><strong>Limites :</strong> séniorité, qualité de code et neurotype non mesurés. '
        'Un niveau reflète une adoption, jamais une valeur humaine.</p>'
        '<p><strong>Sources :</strong> référentiel AIDD officiel '
        '(<a href="https://github.com/ai-driven-dev/laivel-up" target="_blank" '
        'rel="noopener">github.com/ai-driven-dev/laivel-up</a>).</p>'
        '</div>'
    )

    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Verdict AIDD · {escape(verdict.name)}</title>
<link rel="stylesheet" href="https://fonts.bunny.net/css?family=Press+Start+2P|Share+Tech+Mono&display=swap">
<style>
  :root {{
    --bg: #0f0f23;
    --surface: #1a1a2e;
    --surface-2: #222244;
    --border: #3a3a5c;
    --text: #e0e0e0;
    --text-dim: #777799;
    --accent: #00aaff;
    --success: #00cc44;
    --warning: #ccaa00;
    --danger: #cc3333;
    --pixel: 2px;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Share Tech Mono', monospace;
    background: var(--bg);
    color: var(--text);
    max-width: 900px;
    margin: 0 auto;
    padding: 2rem 1.5rem;
    line-height: 1.8;
    position: relative;
  }}

  /* Scanlines overlay */
  body::after {{
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: repeating-linear-gradient(
      0deg,
      transparent,
      transparent 2px,
      rgba(0,0,0,0.08) 2px,
      rgba(0,0,0,0.08) 4px
    );
    pointer-events: none;
    z-index: 9999;
  }}

  h1 {{
    font-family: 'Press Start 2P', monospace;
    font-size: 1rem;
    font-weight: 400;
    margin-bottom: 1rem;
    color: var(--accent);
    text-shadow: 2px 2px 0px #003366;
    letter-spacing: 1px;
  }}
  h2 {{
    font-family: 'Press Start 2P', monospace;
    font-size: 0.7rem;
    font-weight: 400;
    margin: 2rem 0 1rem;
    color: var(--accent);
    text-shadow: 1px 1px 0px #003366;
    letter-spacing: 0.5px;
  }}
  h3 {{
    font-family: 'Press Start 2P', monospace;
    font-size: 0.6rem;
    font-weight: 400;
    margin: 1.5rem 0 0.8rem;
    color: var(--text);
  }}

  /* Badge verdict — pixel art style. Le verdict est ce que le jury doit
     comprendre « en un coup d'œil » (critère n°1) : sa taille doit largement
     dépasser celle du h1 (1rem) plutôt que rivaliser avec lui (10.1.e). */
  .badge {{
    display: inline-block;
    padding: 1.1rem 2rem;
    font-family: 'Press Start 2P', monospace;
    font-size: 1.6rem;
    line-height: 1.5;
    font-weight: 400;
    margin: 1.5rem 0;
    border: 3px solid;
    image-rendering: pixelated;
    text-shadow: 1px 1px 0px rgba(0,0,0,0.5);
    letter-spacing: 0.5px;
  }}
  .badge.ok {{
    background: #003311;
    color: var(--success);
    border-color: var(--success);
    box-shadow:
      inset 2px 2px 0px rgba(0,204,68,0.3),
      inset -2px -2px 0px rgba(0,0,0,0.3);
  }}
  /* Contraste WCAG vérifié le 30/08 (10.1.d) : #cc3333 (--danger) sur fond
     #330011 ne donne que 3.56:1, sous le seuil AA texte normal (4.5:1).
     #ff6b6b sur le même fond donne 6.59:1 — le bordé/box-shadow décoratifs
     restent en --danger (pas soumis à la contrainte de contraste texte). */
  .badge.ko {{
    background: #330011;
    color: #ff6b6b;
    border-color: var(--danger);
    box-shadow:
      inset 2px 2px 0px rgba(204,51,51,0.3),
      inset -2px -2px 0px rgba(0,0,0,0.3);
  }}

  .limiting-axis {{ color: var(--warning); font-weight: 500; margin: 0.5rem 0; }}

  /* World map — NES overworld style */
  .patapon-world {{
    background: var(--surface);
    border: 3px solid var(--border);
    padding: 1.5rem;
    margin: 1.5rem 0;
    position: relative;
  }}
  .patapon-world::before {{
    content: '>>> WORLD MAP <<<';
    position: absolute;
    top: -10px;
    left: 50%;
    transform: translateX(-50%);
    background: var(--bg);
    padding: 0 8px;
    font-family: 'Press Start 2P', monospace;
    font-size: 0.45rem;
    color: var(--text-dim);
    letter-spacing: 1px;
  }}
  .world-title {{
    font-size: 1rem;
    color: var(--text-dim);
    margin-bottom: 1rem;
    text-align: center;
  }}
  .world-map {{
    display: flex;
    align-items: flex-start;
    gap: 0;
    overflow-x: auto;
    padding: 1rem 0;
  }}
  .world-node {{
    display: flex;
    flex-direction: column;
    align-items: center;
    min-width: 90px;
    position: relative;
    opacity: 0.3;
    transition: opacity 0.2s steps(2);
  }}
  .world-node.unlocked {{
    opacity: 0.6;
  }}
  .world-node.current {{
    opacity: 1;
  }}
  .world-node.current .node-icon {{
    animation: nes-pulse 0.8s steps(4) infinite;
  }}
  @keyframes nes-pulse {{
    0%, 100% {{ box-shadow: 0 0 0 0px var(--accent); }}
    25% {{ box-shadow: 0 0 0 4px var(--accent); }}
    50% {{ box-shadow: 0 0 0 8px rgba(0,170,255,0.3); }}
    75% {{ box-shadow: 0 0 0 4px var(--accent); }}
  }}
  .node-icon {{
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    border: 3px solid;
    margin-bottom: 0.5rem;
    transition: border-color 0.2s steps(2);
    image-rendering: pixelated;
  }}
  .node-label {{
    font-family: 'Press Start 2P', monospace;
    font-size: 0.45rem;
    color: var(--text);
    margin-bottom: 0.3rem;
    text-align: center;
  }}
  .axis-stage {{
    font-family: 'Press Start 2P', monospace;
    font-size: 0.35rem;
    padding: 2px 4px;
    border: 1px solid;
    margin: 1px;
    display: inline-block;
    image-rendering: pixelated;
  }}
  .achievement-badge {{
    font-family: 'Press Start 2P', monospace;
    font-size: 0.35rem;
    font-weight: 400;
    padding: 2px 6px;
    border: 2px solid;
    margin-top: 0.4rem;
    letter-spacing: 0.5px;
    animation: badge-pop 0.4s steps(4) forwards;
  }}
  @keyframes badge-pop {{
    0% {{ transform: scale(0); opacity: 0; }}
    25% {{ transform: scale(0.5); opacity: 0.5; }}
    50% {{ transform: scale(1.1); opacity: 1; }}
    100% {{ transform: scale(1); opacity: 1; }}
  }}
  .connector {{
    display: flex;
    align-items: center;
    padding: 0 0.2rem;
    margin-top: 1rem;
  }}
  .connector-line {{
    width: 30px;
    height: 4px;
    background: repeating-linear-gradient(
      90deg,
      var(--border) 0px,
      var(--border) 4px,
      transparent 4px,
      transparent 8px
    );
    image-rendering: pixelated;
  }}

  /* Progress bar — pixel blocks */
  .progress-bar-container {{
    background: var(--surface);
    border: 3px solid var(--border);
    padding: 1.5rem;
    margin: 1.5rem 0;
    position: relative;
  }}
  .progress-bar-container::before {{
    content: '>>> PROGRESS <<<';
    position: absolute;
    top: -10px;
    left: 50%;
    transform: translateX(-50%);
    background: var(--bg);
    padding: 0 8px;
    font-family: 'Press Start 2P', monospace;
    font-size: 0.45rem;
    color: var(--text-dim);
    letter-spacing: 1px;
  }}
  .progress-title {{
    font-size: 1rem;
    color: var(--text-dim);
    margin-bottom: 1rem;
  }}
  .progress-track {{
    display: flex;
    gap: 4px;
    height: 24px;
    margin-bottom: 0.8rem;
  }}
  .progress-block {{
    flex: 1;
    height: 100%;
    border: 2px solid var(--border);
    background: var(--surface-2);
    image-rendering: pixelated;
  }}
  .progress-block.filled {{
    background: var(--success);
    border-color: var(--success);
    box-shadow: inset -2px -2px 0px rgba(0,0,0,0.3);
  }}
  .progress-block.current {{
    background: var(--accent);
    border-color: var(--accent);
    animation: block-blink 0.6s steps(2) infinite;
  }}
  @keyframes block-blink {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.5; }}
  }}
  .progress-steps {{
    display: flex;
    justify-content: space-between;
  }}
  .step {{ flex: 1; text-align: center; }}
  .step-dot {{
    width: 8px;
    height: 8px;
    margin: 0 auto 0.3rem;
    border: 2px solid;
  }}
  .step-label {{
    font-family: 'Press Start 2P', monospace;
    font-size: 0.35rem;
    color: var(--text-dim);
  }}

  /* Axis detail cards — pixel style */
  .axis-details {{
    margin: 1.5rem 0;
  }}
  .axis-card {{
    background: var(--surface);
    border: 2px solid var(--border);
    padding: 1rem 1.2rem;
    margin: 0.8rem 0;
    transition: border-color 0.2s steps(2);
  }}
  .axis-card:hover {{
    border-color: var(--accent);
  }}
  .axis-card-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.4rem;
  }}
  .axis-name {{
    font-family: 'Press Start 2P', monospace;
    font-size: 0.55rem;
    color: var(--accent);
  }}
  .axis-level {{
    font-family: 'Press Start 2P', monospace;
    font-size: 0.55rem;
  }}
  .axis-confidence {{
    font-size: 0.8rem;
    color: var(--text-dim);
    margin-bottom: 0.3rem;
  }}
  .axis-evidence {{
    font-size: 0.8rem;
    color: var(--text-dim);
    margin-bottom: 0.4rem;
  }}
  .axis-why {{
    font-size: 0.8rem;
    padding: 0.5rem 0.7rem;
    background: var(--surface-2);
    border-left: 4px solid var(--accent);
    line-height: 1.5;
  }}
  .axis-why em {{ font-style: normal; color: var(--text); }}

  /* Flags — pixel danger */
  .flag {{
    border-left: 4px solid var(--danger);
    padding: 0.6rem 0.8rem;
    margin: 0.5rem 0;
    background: rgba(204,51,51,0.1);
  }}

  /* Next steps — pixel accent */
  .next {{
    border-left: 4px solid var(--accent);
    padding: 0.6rem 0.8rem;
    margin: 0.5rem 0;
    background: rgba(0,170,255,0.08);
    font-size: 0.85rem;
  }}

  /* Pedagogy */
  .pedagogy {{
    margin: 2rem 0;
  }}
  .guide-section {{
    background: var(--surface);
    border: 2px solid var(--border);
    padding: 1rem 1.2rem;
    margin: 0.8rem 0;
  }}
  .guide-item {{
    display: flex;
    gap: 0.8rem;
    padding: 0.4rem 0;
    align-items: baseline;
  }}
  .guide-axe {{
    font-family: 'Press Start 2P', monospace;
    font-size: 0.45rem;
    color: var(--accent);
    min-width: 120px;
  }}
  .guide-step {{ color: var(--text); font-size: 0.85rem; }}
  .glossary-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 0.6rem;
  }}
  .glossary-item {{
    background: var(--surface);
    border: 2px solid var(--border);
    padding: 0.6rem 0.8rem;
  }}
  .glossary-term-inline {{
    font-family: 'Press Start 2P', monospace;
    font-size: 0.4rem;
    color: var(--accent);
    display: block;
    margin-bottom: 0.3rem;
  }}
  .glossary-def {{
    font-size: 0.75rem;
    color: var(--text-dim);
    display: block;
  }}
  .ref-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 0.6rem;
  }}
  .ref-item {{
    background: var(--surface);
    border: 2px solid var(--border);
    padding: 0.6rem 0.8rem;
  }}
  .ref-item a {{
    color: var(--accent);
    text-decoration: none;
    font-family: 'Press Start 2P', monospace;
    font-size: 0.4rem;
    display: block;
    margin-bottom: 0.3rem;
  }}
  .ref-item a:hover {{ text-decoration: underline; }}
  .ref-desc {{
    font-size: 0.75rem;
    color: var(--text-dim);
    display: block;
  }}

  /* Transparency — pixel box */
  .transparency-box {{
    background: var(--surface);
    border: 2px solid var(--border);
    padding: 1rem 1.2rem;
  }}
  .transparency-box p {{
    margin: 0.5rem 0;
    font-size: 0.85rem;
    color: var(--text-dim);
  }}
  code {{
    background: var(--surface-2);
    padding: 2px 4px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.8rem;
    border: 1px solid var(--border);
  }}

  /* Footer — pixel */
  .report-footer {{
    margin-top: 3rem;
    padding-top: 1rem;
    border-top: 3px solid var(--border);
    text-align: center;
    font-family: 'Press Start 2P', monospace;
    font-size: 0.45rem;
    color: var(--text-dim);
  }}
  .report-footer a {{ color: var(--accent); text-decoration: none; }}
  .report-footer a:hover {{ text-decoration: underline; }}

  /* Responsive */
  @media (max-width: 600px) {{
    body {{ padding: 1rem; }}
    .world-map {{ flex-direction: column; align-items: center; }}
    .glossary-grid, .ref-grid {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>
<main>
  <h1>Verdict AIDD · {escape(verdict.name)}</h1>

  <p><span class="badge {kelas}">{badge_text}</span></p>

  {limiting}
  {errors_section}

  {_render_progress_bar(verdict)}
  {_render_world_map(verdict)}
  {_render_axis_detail(verdict)}
  {flags_section}
  {next_section}
  {_render_pedagogical_section(verdict)}
  {transparency}

  <div class="report-footer">
    Généré par <strong>LAIVEL UP</strong> · Référentiel
    <a href="https://github.com/ai-driven-dev/laivel-up" target="_blank" rel="noopener">AIDD officiel</a>
  </div>
</main>
</body>
</html>
"""


def write_reports(
    verdict: Verdict, out_dir: Path, with_html: bool = True
) -> tuple[Path, Path | None]:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_dir_resolved = out_dir.resolve()
    safe = slug(verdict.name)
    md = out_dir / f'{safe}.md'
    # Security: ensure the generated path stays within out_dir
    if not md.resolve().is_relative_to(out_dir_resolved):
        raise ValueError(f'Generated path escapes output directory: {md}')
    md.write_text(render_markdown(verdict), encoding='utf-8')
    html = None
    if with_html:
        html = out_dir / f'{safe}.html'
        if not html.resolve().is_relative_to(out_dir_resolved):
            raise ValueError(f'Generated path escapes output directory: {html}')
        html.write_text(render_html(verdict), encoding='utf-8')
    return md, html


def verdict_to_dict(verdict: Verdict) -> dict:
    """Sérialisation canonique d'un Verdict en dict JSON-serialisable."""
    return {
        'name': verdict.name,
        'level': verdict.level.name if verdict.level else None,
        'limiting_axis': verdict.limiting_axis,
        'axes': [
            {
                'axe': a.axe,
                'level': a.level.name if a.level else None,
                'confidence': a.confidence,
                'evidence': a.evidence,
                'variance': a.variance,
            }
            for a in verdict.axis_scores
        ],
        'red_flags': [
            {
                'titre': f.titre,
                'constat': f.constat,
                'source': f.source,
                'question': f.question,
                'severite': f.severite,
            }
            for f in verdict.red_flags
        ],
        'next_steps': verdict.next_steps,
        'data_errors': verdict.data_errors,
    }
