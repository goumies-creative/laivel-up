#!/usr/bin/env python3
# Copyright 2026 Romy Alula — MIT License
"""Extracteur profils officiels → ProfileData format.

Convertit les dossiers de profils officiels (perceval, bohort, leodagan, arthur)
en JSON normalisé attendu par laivelup evaluate.

Usage:
  python scripts/extract_official_profile.py --source ../laivel-up/profiles
  python scripts/extract_official_profile.py --source ../laivel-up/profiles --output grille/profils-officiels

Historique des correctifs (28/08) :
- `pr_sizes` reconstruisait une simple liste de présence par taille
  (["S","M","L"] quel que soit le nombre réel de PR par taille), ce qui
  aplatissait totalement la distribution réelle : bohort/leodagan/arthur
  produisaient tous les trois exactement ["S","S","M","L","XL"]. Corrigé en
  dupliquant chaque taille par son compte réel (`size_distribution`), qui
  couvre l'intégralité de la période — `pull-requests.json`, quand présent,
  n'est qu'une page (~12 PR) et n'est pas utilisé ici pour ne pas
  sous-échantillonner un signal déjà complet ailleurs.
- Le signal `prompts` (un des 4 signaux d'adoption attendus par
  `harness_max()`) n'était jamais renseigné : un profil avec `context_files`
  entièrement à false (ex. perceval) était refusé (aucun axe harness décidé)
  au lieu d'obtenir RED (« prompts directs, pas de contexte »). Corrigé en
  dérivant `prompts` depuis `assistant_usage` (outils déclarés ou sessions
  hebdomadaires > 0).
- `agent_rules_versioned` ne regardait que `rules_count`, alors que
  `context_files` distingue `rules_count` (règles génériques) et
  `agents_count` (agents personnalisés versionnés). Cas réel : arthur a
  `rules_count=0` mais `agents_count=2` (2 fichiers réels dans
  `repo-context/.claude/agents/`) — sans correctif, son harness plafonnait à
  BLUE au lieu de COPPER. Corrigé en combinant les deux compteurs.
- `retries_triangulated` se basait sur `reverted > 0`, un mauvais proxy : ça
  refusait leodagan (0 revert) alors que son `retries_after_fact` vient de
  métriques git objectives (`median_correction_commits_after_open`,
  `merged_without_human_edit_after_open`), pas d'un déclaratif. Par
  définition, `declaratif.md` est une donnée suggestive fournie par la
  personne évaluée, jamais une mesure — la distinction pertinente est donc
  « donnée mesurée en dur (git-activity.json) » vs « donnée déclarée
  (declaratif.md) », pas « PR revertée ou non ». Corrigé : triangulé dès que
  `retries_after_fact` est calculable depuis git-activity.json.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Force UTF-8 for emoji output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')  # type: ignore[attr-defined]
    sys.stderr.reconfigure(encoding='utf-8')  # type: ignore[attr-defined]

# Ajouter le src au path pour importer laivelup
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from laivelup.model import Level, ProfileData


def _extract_pr_sizes(git_activity: dict) -> list[str] | None:
    """Extrait les tailles de PR depuis git-activity.json (XS → S), pondérées
    par le nombre réel de PR par taille (pas juste leur présence)."""
    pr_data = git_activity.get('pull_requests', {})
    size_dist = pr_data.get('size_distribution', {})
    sizes: list[str] = []
    for size, count in size_dist.items():
        if not count:
            continue
        # Map XS to S (schema expects ['S', 'M', 'L', 'XL'])
        normalized = 'S' if size.upper() == 'XS' else size.upper()
        sizes.extend([normalized] * int(count))
    return sizes if sizes else None


def _extract_parallel_projects(git_activity: dict) -> int | None:
    """Extrait le nombre de projets parallèles max."""
    parallelism = git_activity.get('parallelism', {})
    return parallelism.get('max_concurrent_branches')


def _extract_projects_completed(git_activity: dict) -> int | None:
    """Estime les projets menés jusqu'au bout (repos count)."""
    return git_activity.get('repositories')


def _extract_context_versioned(git_activity: dict) -> bool | None:
    """Vérifie si AGENTS.md ou équivalent existe."""
    context_files = git_activity.get('context_files', {})
    return context_files.get('agents_md')


def _extract_agent_rules_versioned(git_activity: dict) -> bool | None:
    """Vérifie si des règles ET/OU des agents personnalisés sont versionnés.

    `context_files` distingue deux compteurs : `rules_count` (fichiers de
    règles génériques) et `agents_count` (agents personnalisés, ex.
    `.claude/agents/*.md`). Les deux relèvent du même palier « comportement
    versionné » de la grille — se limiter à `rules_count` sous-évalue un
    profil qui a versionné des agents mais pas de règles génériques (cas réel
    du profil arthur : rules_count=0, agents_count=2, 2 fichiers d'agents
    présents dans repo-context/.claude/agents/)."""
    context_files = git_activity.get('context_files', {})
    rules_count = context_files.get('rules_count')
    agents_count = context_files.get('agents_count')
    if rules_count is None and agents_count is None:
        return None
    return (rules_count or 0) > 0 or (agents_count or 0) > 0


def _extract_retry_loops(git_activity: dict) -> bool | None:
    """Vérifie si des retry loops sont en place (hooks)."""
    context_files = git_activity.get('context_files', {})
    hooks_count = context_files.get('hooks_count', 0)
    return hooks_count > 0 if hooks_count is not None else None


def _extract_prompts(git_activity: dict) -> bool | None:
    """Signal plancher du harness : usage direct de prompts (assistant_usage),
    même sans contexte/règles/boucles versionnés. Sans ce signal, un profil
    sans aucun fichier de contexte est refusé au lieu d'obtenir RED."""
    usage = git_activity.get('assistant_usage', {})
    if not usage:
        return None
    declared_tools = usage.get('declared_tools') or []
    sessions = usage.get('sessions_per_week') or 0
    return bool(declared_tools) or sessions > 0


def _extract_retries_after_fact(git_activity: dict) -> float | None:
    """Estime le ratio de reprise après coup."""
    pr_data = git_activity.get('pull_requests', {})
    correction = pr_data.get('median_correction_commits_after_open', 0)
    merged_clean = pr_data.get('merged_without_human_edit_after_open', 0)
    total = pr_data.get('total', 0)
    if not total:
        return None
    # Ratio de PR nécessitant correction (clamp to 0-1 range)
    return min(max(correction / max(correction + merged_clean, 1), 0.0), 1.0)


def _extract_retries_triangulated(git_activity: dict) -> bool | None:
    """Triangulé dès que `retries_after_fact` est calculable depuis des
    métriques git objectives (git-activity.json), et non depuis un
    déclaratif. `declaratif.md` est par définition une donnée suggestive
    fournie par la personne évaluée — jamais une mesure — donc ne peut jamais
    à lui seul valoir triangulation. Ici, tant qu'on dispose d'un total de PR
    exploitable, le ratio est une mesure, pas une déclaration."""
    pr_data = git_activity.get('pull_requests', {})
    total = pr_data.get('total', 0)
    return True if total else None


def _extract_agents_autonomous(session_content: str | None) -> bool | None:
    """Vérifie si les agents semblent autonomes (heuristique sur session.md)."""
    if not session_content:
        return None
    # Heuristique : recherche de patterns d'autonomie
    autonomous_keywords = ['autonomous', 'autonome', 'automatisé', 'pipeline', 'ci/cd']
    return any(kw in session_content.lower() for kw in autonomous_keywords)


def _extract_declared_level(declaratif: str | None) -> Level | None:
    """Extrait le niveau déclaré depuis declaratif.md (heuristique)."""
    if not declaratif:
        return None
    level_map = {
        'white': Level.WHITE,
        'red': Level.RED,
        'blue': Level.BLUE,
        'green': Level.GREEN,
        'copper': Level.COPPER,
        'silver': Level.SILVER,
        'gold': Level.GOLD,
        'blanc': Level.WHITE,
        'rouge': Level.RED,
        'bleu': Level.BLUE,
        'vert': Level.GREEN,
        'cuivre': Level.COPPER,
    }
    for word, level in level_map.items():
        if word in declaratif.lower():
            return level
    return None


def extract_profile(profile_dir: Path) -> ProfileData:
    """Extrait un profil officiel en ProfileData."""
    profile_json_path = profile_dir / 'profile.json'
    if not profile_json_path.exists():
        raise ValueError(f'profile.json manquant dans {profile_dir}')

    profile_info = json.loads(profile_json_path.read_text(encoding='utf-8'))
    name = profile_info.get('profile_id', profile_dir.name)

    traces: dict = {}
    declared_level = None

    # git-activity.json
    git_activity_path = profile_dir / 'git-activity.json'
    if git_activity_path.exists():
        git_activity = json.loads(git_activity_path.read_text(encoding='utf-8'))
        traces['pr_sizes'] = _extract_pr_sizes(git_activity)
        traces['parallel_projects'] = _extract_parallel_projects(git_activity)
        traces['projects_completed'] = _extract_projects_completed(git_activity)
        traces['context_versioned'] = _extract_context_versioned(git_activity)
        traces['agent_rules_versioned'] = _extract_agent_rules_versioned(git_activity)
        traces['retry_loops'] = _extract_retry_loops(git_activity)
        traces['prompts'] = _extract_prompts(git_activity)
        traces['retries_after_fact'] = _extract_retries_after_fact(git_activity)
        traces['retries_triangulated'] = _extract_retries_triangulated(git_activity)

    # declaratif.md (pour le niveau déclaré seulement, pas dans traces)
    declaratif_path = profile_dir / 'declaratif.md'
    if declaratif_path.exists():
        declaratif = declaratif_path.read_text(encoding='utf-8')
        declared_level = _extract_declared_level(declaratif)

    # session.md (pour agents_autonomous)
    session_path = profile_dir / 'session.md'
    if session_path.exists():
        session = session_path.read_text(encoding='utf-8')
        traces['agents_autonomous'] = _extract_agents_autonomous(session)

    return ProfileData(
        name=name,
        declared_level=declared_level,
        traces=traces,
        answers={},
        meta={'source_dir': str(profile_dir)},
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Extrait les profils officiels en format normalisé.'
    )
    parser.add_argument(
        '--source',
        type=Path,
        default=Path('../laivel-up/profiles'),
        help='Chemin vers le dossier des profils officiels (défaut: ../laivel-up/profiles)',
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path('grille/profils-officiels'),
        help='Dossier de sortie (défaut: grille/profils-officiels)',
    )
    args = parser.parse_args()

    source = args.source
    output = args.output
    output.mkdir(parents=True, exist_ok=True)

    profiles = ['perceval', 'bohort', 'leodagan', 'arthur']
    results = {}

    for profile_name in profiles:
        profile_dir = source / profile_name
        if not profile_dir.exists():
            print(f'⚠️  Profil {profile_name} non trouvé dans {source}')
            continue

        try:
            profile = extract_profile(profile_dir)
            output_file = output / f'{profile_name}.json'
            output_file.write_text(
                json.dumps(
                    {
                        'name': profile.name,
                        'declared_level': profile.declared_level.name
                        if profile.declared_level
                        else None,
                        'traces': profile.traces,
                        'answers': profile.answers,
                        'meta': profile.meta,
                    },
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding='utf-8',
            )
            results[profile_name] = '✅'
            print(f'✅ {profile_name} → {output_file}')
        except Exception as e:
            results[profile_name] = f'❌ {e}'
            print(f'❌ {profile_name} : {e}')

    # Expected levels from official README
    expected = {
        'levels': {
            'perceval': 'RED',
            'bohort': 'BLUE',
            'leodagan': 'GREEN',
            'arthur': 'COPPER',
        }
    }
    expected_file = output / 'expected.json'
    expected_file.write_text(json.dumps(expected, indent=2), encoding='utf-8')
    print(f'\n📋 Expected levels → {expected_file}')

    print('\n📊 Résumé :')
    for name, status in results.items():
        print(f'  {name}: {status}')


if __name__ == '__main__':
    main()
