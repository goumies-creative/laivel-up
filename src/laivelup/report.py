# Copyright 2026 Romy Alula — MIT License
"""Rapports LAIVEL-UP : Markdown (source de vérité) + HTML (relecture humaine).

Le moteur de scoring n'est jamais dupliqué ici.

Ce module est uniquement responsable de :
- sérialiser un Verdict en Markdown ;
- présenter un Verdict en HTML ;
- écrire les artefacts de rapport ;
- fournir une sérialisation JSON-compatible.

Principes de rendu :
- pas de progression artificielle ;
- un niveau n'est jamais transformé en score ou pourcentage ;
- seule la confiance réelle peut être affichée en pourcentage ;
- Refus est un état distinct d'un niveau ;
- les quatre axes et leur vocabulaire métier restent inchangés ;
- les Red Flags et Next Steps sont présentés tels que fournis par le moteur ;
- aucune donnée personnelle ou donnée de neurotype n'est introduite.
"""

from __future__ import annotations

import os
import tempfile
from datetime import datetime
from html import escape
from pathlib import Path

from .model import Level, Verdict, axis_label, level_label
from .report_css import CSS_STYLES
from .utils import slug

# ---------------------------------------------------------------------------
# ÉCRITURE ATOMIQUE
# ---------------------------------------------------------------------------


def _atomic_write(path: Path, content: str) -> None:
    """Écriture atomique via tempfile + os.replace."""
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix='.tmp')
    try:
        os.write(fd, content.encode('utf-8'))
        os.close(fd)
        os.replace(tmp, path)
    except BaseException:
        os.close(fd) if not os.get_inheritable(fd) else None
        os.unlink(tmp)
        raise


# ---------------------------------------------------------------------------
# GLOSSAIRE LAIVEL-UP
# ---------------------------------------------------------------------------

GLOSSARY: dict[str, str] = {
    'Context Engineering': (
        "La mémoire que l'IA lit avant de coder : conventions, architecture, "
        "décisions passées. C'est le minimum syndical pour que l'IA produise "
        'du code cohérent.'
    ),
    'Behavior': (
        "Les règles et agents qui contrôlent comment l'IA agit : code review, "
        "hooks, guardrails. C'est le « comment » au lieu du « quoi »."
    ),
    'Retry Loops': (
        "Un script relance l'IA tant qu'une commande du projet échoue. "
        "L'IA corrige elle-même ses erreurs sans intervention humaine."
    ),
    'Harness': (
        "L'ensemble du harnais autour du modèle : Context Engineering + "
        "Behavior + Retry Loops. Plus le harnais est complet, moins l'humain "
        'doit intervenir.'
    ),
    'Intervention': (
        "Quand l'humain intervient dans le travail de l'IA. Cadrer = choisir "
        "la tâche et dire ce qui est attendu. Monter d'un niveau = reprendre "
        'moins pour atteindre la qualité.'
    ),
    'Reprise (proportion de)': (
        "La part de PR livrées avec l'IA que l'humain a dû reprendre après coup : "
        'corriger, retoucher, refaire. La grille officielle dit « commits '
        "correctifs ». 70 % : sur 10 PR, 7 reprises · cellule Red de l'axe "
        "Intervention. La valeur vient des traces du profil, jamais d'une "
        'réponse au questionnaire seule.'
    ),
    'Taille (Size)': (
        "La taille habituelle des features livrées avec l'IA : S (petite), "
        'M (moyenne), L (multi-étapes), XL (multi-modules). Pas la plus grosse '
        "jamais faite, l'habituel."
    ),
    'En parallèle': (
        'Combien de chantiers avancent en même temps, habituellement. '
        "Un pic isolé ne compte pas : c'est la pratique régulière."
    ),
    'Règle AND': (
        "Un niveau n'est atteint que si TOUTES ses cellules sont satisfaites. "
        "L'axe le plus faible (« axe plancher ») détermine le niveau global."
    ),
    'Refus de deviner': (
        "Quand les données manquent ou se contredisent, l'outil refuse de "
        'trancher et pose des questions ciblées plutôt que de deviner. '
        'Équité structurelle.'
    ),
}


# ---------------------------------------------------------------------------
# RÉFÉRENCES
# ---------------------------------------------------------------------------

REFERENCES: list[dict[str, str]] = [
    {
        'url': 'https://ai-driven-development.org',
        'title': 'Manifesto for AI-Driven Development',
        'desc': ("Le manifeste fondateur — principes et niveaux d'adoption AIDD."),
    },
    {
        'url': ('https://github.com/ai-driven-dev/laivel-up/blob/main/levels/aidd.md'),
        'title': 'Référentiel AIDD officiel',
        'desc': ('La grille complète : 4 axes × 7 niveaux, règles et exemples.'),
    },
    {
        'url': 'https://github.com/EveryInc/compound-engineering',
        'title': 'Compound Engineering',
        'desc': ('Le framework de skills qui structure le développement assisté par IA.'),
    },
]


# ---------------------------------------------------------------------------
# PALETTE SÉMANTIQUE LAIVEL-UP
# ---------------------------------------------------------------------------

SYSTEM_COLORS: dict[str, str] = {
    'background': '#0b0d12',
    'surface': '#11151d',
    'surface_2': '#171c25',
    'border': '#2b3442',
    'border_active': '#56657a',
    'text': '#e7ebf0',
    'text_secondary': '#a7b0bd',
    'muted': '#697586',
    'info': '#4db8ff',
    'ok': '#39d98a',
    'warn': '#e3b341',
    'danger': '#ef6262',
    'white': '#d9dee7',
    'red': '#ef6262',
    'blue': '#4d8dff',
    'green': '#39c879',
    'copper': '#c58b52',
    'silver': '#aeb7c4',
    'gold': '#f0c75e',
}


LEVEL_COLORS_HTML: dict[Level, dict[str, str]] = {
    Level.WHITE: {
        'fg': SYSTEM_COLORS['white'],
        'accent': SYSTEM_COLORS['white'],
    },
    Level.RED: {
        'fg': SYSTEM_COLORS['red'],
        'accent': SYSTEM_COLORS['red'],
    },
    Level.BLUE: {
        'fg': SYSTEM_COLORS['blue'],
        'accent': SYSTEM_COLORS['blue'],
    },
    Level.GREEN: {
        'fg': SYSTEM_COLORS['green'],
        'accent': SYSTEM_COLORS['green'],
    },
    Level.COPPER: {
        'fg': SYSTEM_COLORS['copper'],
        'accent': SYSTEM_COLORS['copper'],
    },
    Level.SILVER: {
        'fg': SYSTEM_COLORS['silver'],
        'accent': SYSTEM_COLORS['silver'],
    },
    Level.GOLD: {
        'fg': SYSTEM_COLORS['gold'],
        'accent': SYSTEM_COLORS['gold'],
    },
}


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------


def _level_name(level: Level | None) -> str:
    """Nom textuel du niveau, sans emoji.

    model.level_label() reste la source de vérité pour le vocabulaire.
    Le HTML utilise toutefois une représentation sans emoji afin de garder
    une identité visuelle sobre et compatible terminal.
    """
    if level is None:
        return 'Refus'

    label = level_label(level)

    # LEVEL_LABELS du modèle contiennent actuellement des symboles.
    # On conserve uniquement le nom final.
    return label.split()[-1]


def _level_color(level: Level | None) -> str:
    """Retourne la couleur sémantique associée à un niveau."""
    if level is None:
        return SYSTEM_COLORS['muted']

    return LEVEL_COLORS_HTML[level]['accent']


def _confidence_text(confidence: float | None) -> str:
    """Formate une confiance réelle sans créer de métrique dérivée."""
    if confidence is None:
        return '—'

    return f'{confidence:.0%}'


def _glossary_tooltip(term: str) -> str:
    """Retourne un span HTML avec le terme et sa définition."""
    definition = GLOSSARY.get(term)

    if not definition:
        return escape(term)

    return (
        f'<span class="glossary-term" '
        f'data-tooltip="{escape(definition)}">'
        f'{escape(term)}'
        f'<span class="glossary-icon">?</span>'
        '</span>'
    )


# ---------------------------------------------------------------------------
# MARKDOWN — SOURCE DE VÉRITÉ
# ---------------------------------------------------------------------------


def render_markdown(verdict: Verdict) -> str:
    """Rend un Verdict en Markdown.

    Le Markdown reste volontairement factuel et indépendant du design HTML.
    """

    lines = [f'# Verdict AIDD · {verdict.name}']

    if verdict.data_errors:
        lines.append("\n**Données invalides :** l'évaluation refuse de trancher.")

        for error in verdict.data_errors:
            lines.append(f'\n- {error}')

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

        for axis_score in verdict.axis_scores:
            label = level_label(axis_score.level)
            confidence = _confidence_text(
                axis_score.confidence if axis_score.level is not None else None
            )

            evidence = ', '.join(axis_score.evidence)

            if axis_score.variance:
                evidence = f'{evidence} · variance : {axis_score.variance}'

            lines.append(f'| {axis_label(axis_score.axe)} | {label} | {confidence} | {evidence} |')

    if verdict.red_flags:
        lines.append('\n## Alertes (hypothèses à vérifier)')

        for flag in verdict.red_flags:
            severity = '⚠' * max(0, flag.severite)

            lines.append(f'\n- **{flag.titre}** ({severity}) · {flag.constat} _({flag.source})_')

            if flag.question:
                lines.append(f'  → Question : {flag.question}')

    if verdict.next_steps:
        lines.append("\n## Comment monter d'un cran / point de levée d'incertitude")

        for next_step in verdict.next_steps:
            lines.append(f'\n- {next_step}')

    lines.append(
        '\n## Transparence\n'
        '\n- **Données utilisées :** traces techniques déclarées seulement '
        '(commits, PR, contexte). Aucune donnée personnelle, aucun neurotype '
        'demandé ni inféré.\n'
        '- **Méthode :** score discret par axe puis règle officielle '
        '« tous les axes le sont » (`min()`), avec une confiance par axe. '
        'Une confiance faible ou des données contradictoires conduisent au '
        "refus de trancher plutôt qu'à un verdict arbitraire.\n"
        '- **Limites :** la séniorité, la qualité de code et le neurotype ne '
        'sont pas mesurés. Un niveau reflète une adoption observée, pas une '
        'valeur humaine.\n'
        '- **Sources :** référentiel AIDD officiel '
        '(https://github.com/ai-driven-dev/laivel-up).'
    )

    return '\n'.join(lines) + '\n'


# ---------------------------------------------------------------------------
# AVATAR MONITEUR
# ---------------------------------------------------------------------------


def _render_monitor_avatar(
    state: str = 'idle',
    level: Level | None = None,
) -> str:
    """Avatar LAIVEL-UP : uniquement un moniteur.

    Aucun corps, aucune antenne, aucun personnage.
    Les expressions sont rendues par les éléments internes de l'écran.
    """

    expressions: dict[str, tuple[str, str, str]] = {
        'idle': ('·', '·', 'idle'),
        'analyzing': ('◉', '◉', 'analyzing'),
        'questioning': ('?', '?', 'questioning'),
        'success': ('•', '•', 'success'),
        'warning': ('!', '!', 'warning'),
        'error': ('×', '×', 'error'),
        'refusal': ('—', '—', 'refusal'),
    }

    left_eye, right_eye, expression_class = expressions.get(
        state.lower(),
        expressions['idle'],
    )

    accent = _level_color(level) if level is not None else SYSTEM_COLORS['info']

    return f"""
<div class="monitor-avatar {expression_class}"
     style="--avatar-accent:{accent};"
     role="img"
     aria-label="Avatar moniteur LAIVEL-UP, état {escape(state)}">

    <div class="monitor-shell">

        <div class="monitor-screen">

            <div class="monitor-eyes"
                 aria-hidden="true">
                <span>{escape(left_eye)}</span>
                <span>{escape(right_eye)}</span>
            </div>

            <div class="monitor-mouth"
                 aria-hidden="true">
            </div>

        </div>

    </div>

</div>
"""


# ---------------------------------------------------------------------------
# AXES
# ---------------------------------------------------------------------------


def _render_axis_detail(verdict: Verdict) -> str:
    """Rend les quatre axes sous forme de cartes.

    Les données affichées sont directement issues du Verdict.
    Aucune valeur qualitative n'est recalculée.
    """

    if not verdict.axis_scores:
        return ''

    cards: list[str] = []

    for axis_score in verdict.axis_scores:
        label = axis_label(axis_score.axe)
        level_name = _level_name(axis_score.level)
        confidence = _confidence_text(
            axis_score.confidence if axis_score.level is not None else None
        )

        evidence = ', '.join(axis_score.evidence) if axis_score.evidence else 'Aucune trace'

        if axis_score.variance:
            evidence = f'{evidence} · variance : {escape(axis_score.variance)}'

        is_limiting = verdict.limiting_axis == axis_score.axe

        accent = _level_color(axis_score.level)

        limiting_html = '<span class="axis-limiting">AXE PLANCHER</span>' if is_limiting else ''

        cards.append(
            f"""
<article class="axis-card"
         {'axis-card-limiting' if is_limiting else ''}
         style="--axis-accent:{accent};"
         role="listitem"
         aria-label="{escape(label)} : "
                    f"{escape(level_name)}, "
                    f"confiance {escape(confidence)}">

    <header class="axis-card-header">

        <div>
            <span class="axis-index">
                AXE
            </span>

            <h3>
                {escape(label)}
            </h3>
        </div>

        <div class="axis-meta">
            {limiting_html}

            <span class="axis-level">
                {escape(level_name)}
            </span>
        </div>

    </header>

    <div class="axis-card-body">

        <div class="axis-confidence">
            <span>CONFIANCE</span>
            <strong>{escape(confidence)}</strong>
        </div>

        <div class="axis-evidence">

            <span class="field-label">
                OBSERVATIONS
            </span>

            <p>
                {escape(evidence)}
            </p>

        </div>

    </div>

</article>
"""
        )

    return f"""
<section class="section axis-section"
         aria-labelledby="axes-title">

    <div class="section-heading">

        <span class="section-index">
            01
        </span>

        <div>
            <span class="eyebrow">
                MATRICE D'ÉVALUATION
            </span>

            <h2 id="axes-title">
                Axes
            </h2>
        </div>

    </div>

    <div class="axis-grid"
         role="list"
         aria-label="Quatre axes d'évaluation">

        {''.join(cards)}

    </div>

</section>
"""


# ---------------------------------------------------------------------------
# RED FLAGS
# ---------------------------------------------------------------------------


def _render_red_flags(verdict: Verdict) -> str:
    """Rend les Red Flags sans les recalculer ni les reformuler."""

    if not verdict.red_flags:
        return """
<section class="section diagnostic-section diagnostic-clear"
         aria-label="Red Flags">

    <div class="diagnostic-status">
        <span class="status-symbol"
              aria-hidden="true">
            OK
        </span>

        <span>
            AUCUNE ALERTE
        </span>
    </div>

</section>
"""

    items: list[str] = []

    for flag in verdict.red_flags:
        severity = max(1, flag.severite)
        marker = '!' * min(severity, 3)

        question_html = ''

        if flag.question:
            question_html = f"""
<div class="flag-question">

    <span>
        LA DÉCODEUSE
    </span>

    <p>
        {escape(flag.question)}
    </p>

</div>
"""

        items.append(
            f"""
<article class="red-flag">

    <div class="red-flag-marker"
         aria-label="Sévérité {severity}">

        [{marker}]

    </div>

    <div class="red-flag-content">

        <h3>
            {escape(flag.titre)}
        </h3>

        <p class="flag-finding">
            {escape(flag.constat)}
        </p>

        <div class="flag-source">
            SOURCE · {escape(flag.source)}
        </div>

        {question_html}

    </div>

</article>
"""
        )

    return f"""
<section class="section diagnostic-section"
         aria-labelledby="red-flags-title">

    <div class="section-heading">

        <span class="section-index">
            02
        </span>

        <div>
            <span class="eyebrow">
                DIAGNOSTICS
            </span>

            <h2 id="red-flags-title">
                Red Flags
            </h2>
        </div>

    </div>

    <div class="red-flags">
        {''.join(items)}
    </div>

</section>
"""


# ---------------------------------------------------------------------------
# NEXT STEPS
# ---------------------------------------------------------------------------


def _render_next_steps(verdict: Verdict) -> str:
    """Rend les Next Steps tels que fournis par le moteur."""

    if not verdict.next_steps:
        return ''

    items: list[str] = []

    for index, step in enumerate(verdict.next_steps, start=1):
        items.append(
            f"""
<li class="next-step">

    <span class="next-step-index">
        {index:02d}
    </span>

    <div class="next-step-content">
        {escape(step)}
    </div>

</li>
"""
        )

    return f"""
<section class="section next-steps-section"
         aria-labelledby="next-steps-title">

    <div class="section-heading">

        <span class="section-index">
            03
        </span>

        <div>
            <span class="eyebrow">
                ACTION
            </span>

            <h2 id="next-steps-title">
                Next Steps
            </h2>
        </div>

    </div>

    <ol class="next-steps">
        {''.join(items)}
    </ol>

</section>
"""


# ---------------------------------------------------------------------------
# REFUS
# ---------------------------------------------------------------------------


def _render_refusal(verdict: Verdict) -> str:
    """Rend le refus comme un état distinct d'un niveau."""

    errors_html = ''

    if verdict.data_errors:
        errors_html = f"""
<div class="refusal-errors">

    <span class="field-label">
        DIAGNOSTIC DE DONNÉES
    </span>

    <ul>
        {''.join(f'<li>{escape(error)}</li>' for error in verdict.data_errors)}
    </ul>

</div>
"""

    return f"""
<section class="refusal-screen"
         aria-labelledby="refusal-title">

    <div class="refusal-monitor">

        {_render_monitor_avatar('refusal')}

    </div>

    <div class="refusal-content">

        <span class="eyebrow">
            STATUT D'ÉVALUATION
        </span>

        <h1 id="refusal-title">
            REFUS
        </h1>

        <p class="refusal-lead">
            Le moteur ne tranche pas.
        </p>

        <p>
            Les données disponibles sont insuffisantes ou contradictoires
            pour produire un Verdict fiable.
        </p>

        {errors_html}

        <div class="refusal-action">
            <span class="action-key">
                I
            </span>

            <span>
                LA DÉCODEUSE
            </span>
        </div>

    </div>

</section>
"""


# ---------------------------------------------------------------------------
# PÉDAGOGIE
# ---------------------------------------------------------------------------


def _why_this_level(
    axe: str,
    level: Level | None,
    _evidence: list[str],
) -> str:
    """Explication pédagogique statique du référentiel.

    Cette fonction ne participe jamais au scoring.
    """

    if level is None:
        return 'Données insuffisantes pour trancher sur cet axe.'

    explanations: dict[str, dict[Level, str]] = {
        'size': {
            Level.WHITE: ('Aucune adoption AIDD suffisamment établie sur cet axe.'),
            Level.RED: ('Les PR observées sont principalement de taille S.'),
            Level.BLUE: ('Les PR observées sont principalement de taille M.'),
            Level.GREEN: ('Les PR observées couvrent régulièrement des features L.'),
            Level.COPPER: ('Les PR observées couvrent régulièrement des features L et XL.'),
            Level.SILVER: (
                'Les traces montrent des features L-XL livrées avec '
                'une intervention humaine réduite.'
            ),
            Level.GOLD: (
                'Les traces montrent des features XL livrées de façon autonome et régulière.'
            ),
        },
        'harness': {
            Level.WHITE: ("Aucun harnais AIDD suffisamment établi n'est observé."),
            Level.RED: ("Le contexte projet versionné n'est pas suffisamment établi."),
            Level.BLUE: ('Une mémoire projet existe et est maintenue.'),
            Level.GREEN: ('Des règles ou agents versionnés encadrent le comportement.'),
            Level.COPPER: ('Le harnais combine contexte et comportement versionnés.'),
            Level.SILVER: ('Des retry loops permettent une correction automatisée.'),
            Level.GOLD: ('Le harnais combine contexte, comportement et retry loops.'),
        },
        'intervention': {
            Level.WHITE: ('Aucune adoption AIDD suffisamment établie sur cet axe.'),
            Level.RED: ('La reprise humaine après génération reste importante.'),
            Level.BLUE: ('La reprise humaine existe mais devient moins fréquente.'),
            Level.GREEN: ("L'humain intervient principalement aux étapes clés."),
            Level.COPPER: ("L'intervention humaine devient ponctuelle."),
            Level.SILVER: ('La tâche peut être exécutée sans reprise humaine après cadrage.'),
            Level.GOLD: ('Les agents prennent également en charge une partie du cadrage.'),
        },
        'parallel': {
            Level.WHITE: ('Aucune activité AIDD parallèle suffisamment établie.'),
            Level.RED: ('Un chantier est principalement mené à la fois.'),
            Level.BLUE: ('Un chantier reste principal avec une complexité accrue.'),
            Level.GREEN: ('Plusieurs chantiers sont menés régulièrement en parallèle.'),
            Level.COPPER: ('Trois chantiers ou plus peuvent être menés en parallèle.'),
            Level.SILVER: ('Trois chantiers ou plus sont menés au bout en parallèle.'),
            Level.GOLD: (
                'Trois chantiers ou plus sont menés au bout en parallèle avec une forte autonomie.'
            ),
        },
    }

    text = explanations.get(axe, {}).get(
        level,
        'Niveau maintenu.',
    )

    return escape(text)


def _render_pedagogical_section(verdict: Verdict) -> str:
    """Rend glossaire, guide de lecture et références.

    Le contenu reste secondaire : le Verdict et les axes dominent toujours.
    """

    guide_html = ''

    if verdict.limiting_axis and verdict.level is not None:
        axe = verdict.limiting_axis
        level = verdict.level

        guide: dict[str, dict[Level, str]] = {
            'size': {
                Level.RED: 'Passe de features S à M.',
                Level.BLUE: 'Passe à des features L.',
                Level.GREEN: 'Rends les features XL multi-modules régulières.',
                Level.COPPER: 'Maintiens un habituel L-XL, pas seulement un pic.',
                Level.SILVER: "Maintiens l'autonomie sur les features L-XL.",
                Level.GOLD: 'Maintiens le niveau observé.',
            },
            'harness': {
                Level.WHITE: 'Crée et maintiens une mémoire projet.',
                Level.RED: 'Crée et maintiens une mémoire projet.',
                Level.BLUE: 'Versionne les règles et agents.',
                Level.GREEN: 'Ajoute une boucle de relance automatique.',
                Level.COPPER: 'Automatise davantage les boucles de correction.',
                Level.SILVER: "Renforce l'autonomie des agents.",
                Level.GOLD: 'Maintiens le niveau observé.',
            },
            'intervention': {
                Level.RED: 'Réduis la reprise après coup.',
                Level.BLUE: 'Interviens principalement aux étapes clés.',
                Level.GREEN: 'Vise une intervention ponctuelle.',
                Level.COPPER: 'Réduis encore la reprise humaine.',
                Level.SILVER: "Confirme l'autonomie après cadrage.",
                Level.GOLD: 'Maintiens le niveau observé.',
            },
            'parallel': {
                Level.RED: "Mène deux chantiers de front jusqu'au bout.",
                Level.BLUE: 'Mène trois chantiers en parallèle.',
                Level.GREEN: 'Confirme la complétude des chantiers.',
                Level.COPPER: 'Maintiens trois chantiers ou plus.',
                Level.SILVER: 'Maintiens trois chantiers ou plus.',
                Level.GOLD: 'Maintiens le niveau observé.',
            },
        }

        step = guide.get(axe, {}).get(
            level,
            'Maintiens le niveau actuel.',
        )

        guide_html = f"""
<div class="guide-section">

    <span class="eyebrow">
        AXE PLANCHER
    </span>

    <h3>
        Comment monter d'un cran
    </h3>

    <div class="guide-item">

        <span class="guide-axe">
            {escape(axis_label(axe))}
        </span>

        <span class="guide-step">
            {escape(step)}
        </span>

    </div>

</div>
"""

    glossary_items: list[str] = []

    for term, definition in GLOSSARY.items():
        glossary_items.append(
            f"""
<details class="glossary-item">

    <summary>
        {escape(term)}
    </summary>

    <p>
        {escape(definition)}
    </p>

</details>
"""
        )

    reference_items: list[str] = []

    for reference in REFERENCES:
        reference_items.append(
            f"""
<div class="reference-item">

    <a href="{escape(reference['url'], quote=True)}"
       target="_blank"
       rel="noopener noreferrer">
        {escape(reference['title'])}
    </a>

    <span>
        {escape(reference['desc'])}
    </span>

</div>
"""
        )

    return f"""
<section class="section pedagogy-section"
         aria-labelledby="language-title">

    <div class="section-heading">

        <span class="section-index">
            06
        </span>

        <div>
            <span class="eyebrow">
                LANGAGE LAIVEL-UP
            </span>

            <h2 id="language-title">
                Glossaire & ressources
            </h2>
        </div>

    </div>

    {guide_html}

    <div class="glossary-grid">
        {''.join(glossary_items)}
    </div>

    <div class="references">
        <span class="field-label">
            RÉFÉRENCES CURATÉES
        </span>

        {''.join(reference_items)}
    </div>

</section>
"""


# ---------------------------------------------------------------------------
# TRANSPARENCE
# ---------------------------------------------------------------------------


def _render_transparency() -> str:
    """Bloc de transparence commun aux rapports HTML."""

    return """
<section class="section transparency-section"
         aria-labelledby="transparency-title">

    <div class="section-heading">

        <span class="section-index">
            04
        </span>

        <div>
            <span class="eyebrow">
                INFORMATIONS SYSTÈME
            </span>

            <h2 id="transparency-title">
                Transparence
            </h2>
        </div>

    </div>

    <div class="transparency-grid">

        <article>

            <span class="field-label">
                DONNÉES UTILISÉES
            </span>

            <p>
                Traces techniques déclarées seulement :
                commits, PR, contexte.
                Aucune donnée personnelle.
                Aucun neurotype demandé ni inféré.
            </p>

        </article>

        <article>

            <span class="field-label">
                MÉTHODE
            </span>

            <p>
                Score discret par axe puis règle officielle
                « tous les axes le sont » (<code>min()</code>),
                avec une confiance par axe.
            </p>

        </article>

        <article>

            <span class="field-label">
                LIMITES
            </span>

            <p>
                La séniorité, la qualité de code et le neurotype
                ne sont pas mesurés.
                Un niveau reflète une adoption observée,
                pas une valeur humaine.
            </p>

        </article>

    </div>

</section>
"""


# ---------------------------------------------------------------------------
# CSS HTML
# ---------------------------------------------------------------------------


def _html_styles() -> str:
    """Styles embarqués du rapport HTML.

    Aucun framework CSS externe.
    Aucun asset distant.
    Le rapport reste autonome une fois généré.
    """

    return CSS_STYLES


# ---------------------------------------------------------------------------
# HTML — RELECTURE HUMAINE
# ---------------------------------------------------------------------------


def render_html(verdict: Verdict) -> str:
    """Rend un Verdict sous forme de rapport HTML autonome."""

    if verdict.data_errors:
        status_class = 'ko'
        status_text = 'Données invalides · refus de trancher'
        mascot_state = 'error'

    elif verdict.decided:
        status_class = 'ok'
        status_text = 'Engine ready · Verdict établi'
        mascot_state = 'warning' if verdict.red_flags else 'success'

    else:
        status_class = 'ko'
        status_text = 'Données insuffisantes · refus de trancher'
        mascot_state = 'refusal'

    level_name = _level_name(verdict.level)

    level_color = _level_color(verdict.level)

    limiting_html = ''

    if verdict.limiting_axis:
        limiting_html = f"""
<div class="hero-limiting">

    <span>
        AXE PLANCHER
    </span>

    <strong>
        {escape(axis_label(verdict.limiting_axis))}
    </strong>

</div>
"""

    confidence_values = [
        axis_score.confidence for axis_score in verdict.axis_scores if axis_score.level is not None
    ]

    global_confidence = min(confidence_values) if confidence_values else None

    if global_confidence is None:
        confidence_html = """
<div class="confidence">

    <div class="confidence-header">

        <span class="confidence-label">
            CONFIANCE
        </span>

        <strong class="confidence-value">
            —
        </strong>

    </div>

    <div class="confidence-bar"
         aria-hidden="true">
        <span class="confidence-empty">
            ░░░░░░░░░░░░░░░░░░░░
        </span>
    </div>

</div>
"""

    else:
        percentage = max(
            0,
            min(100, round(global_confidence * 100)),
        )

        filled = round(percentage / 5)
        empty = 20 - filled

        confidence_html = f"""
<div class="confidence">

    <div class="confidence-header">

        <span class="confidence-label">
            CONFIANCE
        </span>

        <strong class="confidence-value">
            {percentage}%
        </strong>

    </div>

    <div class="confidence-bar"
         role="progressbar"
         aria-valuenow="{percentage}"
         aria-valuemin="0"
         aria-valuemax="100"
         aria-label="Confiance {percentage}%">

        <span class="confidence-filled">
            {'█' * filled}
        </span><span class="confidence-empty">
            {'░' * empty}
        </span>

    </div>

</div>
"""

    if verdict.level is None:
        main_content = _render_refusal(verdict)

    else:
        main_content = f"""
<section class="verdict-hero"
         style="--verdict-accent:{level_color};"
         aria-labelledby="verdict-title">

    <div class="hero-monitor">

        {
            _render_monitor_avatar(
                mascot_state,
                verdict.level,
            )
        }

    </div>

    <div class="hero-verdict">

        <span class="eyebrow">
            LAIVEL-UP / VERDICT
        </span>

        <div class="verdict-status {status_class}">
            {escape(status_text)}
        </div>

        <h1 id="verdict-title">
            {escape(level_name)}
        </h1>

        {limiting_html}

        {confidence_html}

    </div>

</section>

{_render_axis_detail(verdict)}

{_render_red_flags(verdict)}

{_render_next_steps(verdict)}
"""

    return f"""<!doctype html>
<html lang="fr">

<head>

<meta charset="utf-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1">

<meta name="description"
      content="Rapport d'évaluation LAIVEL-UP">

<title>
LAIVEL-UP · Verdict · {escape(verdict.name)}
</title>

<style>
{_html_styles()}
</style>

</head>

<body>

<div class="app-shell">

    <header class="system-header">

        <div class="brand">

            <span class="brand-mark"
                  aria-hidden="true">
                ◆
            </span>

            <div>

                <strong>
                    LAIVEL-UP
                </strong>

                <span>
                    SYSTEM CONSOLE
                </span>

            </div>

        </div>

        <div class="profile-context">

            <span>
                PROFILE
            </span>

            <strong>
                {escape(verdict.name)}
            </strong>

        </div>

        <div class="system-status">

            <span class="status-dot"
                  aria-hidden="true">
            </span>

            MOTEUR PRÊT

        </div>

    </header>

    <main>

        {main_content}

        {_render_transparency()}

        {_render_pedagogical_section(verdict)}

    </main>

    <footer class="system-footer">

        <span>
            LAIVEL-UP
        </span>

        <span>
            SYSTÈME D'ÉVALUATION AIDD
        </span>

        <span>
            VRAI MOTEUR · VRAIES PREUVES · VRAI VERDICT
        </span>

    </footer>

</div>

</body>

</html>
"""


# ---------------------------------------------------------------------------
# ÉCRITURE DES RAPPORTS
# ---------------------------------------------------------------------------


def write_reports(
    verdict: Verdict,
    out_dir: Path,
    with_html: bool = True,
    stamp: str | None = None,
) -> tuple[Path, Path | None]:
    """Écrit les rapports Markdown et HTML.

    Les noms sont systématiquement horodatés afin de ne jamais écraser
    une évaluation précédente.

    Le slug est vérifié afin d'empêcher une sortie du dossier cible.
    """

    out_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    out_dir_resolved = out_dir.resolve()

    safe = slug(verdict.name)

    if stamp is None:
        stamp = datetime.now().strftime('%Y%m%d-%H%M%S')

    md = out_dir / f'{safe}-{stamp}.md'

    if not md.resolve().is_relative_to(out_dir_resolved):
        raise ValueError(f'Generated path escapes output directory: {md}')

    _atomic_write(md, render_markdown(verdict))

    html: Path | None = None

    if with_html:
        html = out_dir / f'{safe}-{stamp}.html'

        if not html.resolve().is_relative_to(out_dir_resolved):
            raise ValueError(f'Generated path escapes output directory: {html}')

        _atomic_write(html, render_html(verdict))

    return md, html


# ---------------------------------------------------------------------------
# SÉRIALISATION
# ---------------------------------------------------------------------------


def verdict_to_dict(verdict: Verdict) -> dict:
    """Sérialisation canonique d'un Verdict en dict JSON-compatible."""

    return {
        'name': verdict.name,
        'level': (verdict.level.name if verdict.level is not None else None),
        'limiting_axis': verdict.limiting_axis,
        'axes': [
            {
                'axe': axis_score.axe,
                'level': (axis_score.level.name if axis_score.level is not None else None),
                'confidence': axis_score.confidence,
                'evidence': axis_score.evidence,
                'variance': axis_score.variance,
            }
            for axis_score in verdict.axis_scores
        ],
        'red_flags': [
            {
                'titre': flag.titre,
                'constat': flag.constat,
                'source': flag.source,
                'question': flag.question,
                'severite': flag.severite,
            }
            for flag in verdict.red_flags
        ],
        'next_steps': verdict.next_steps,
        'data_errors': verdict.data_errors,
    }
