# Copyright 2026 Romy Alula — MIT License
"""Générateur de profil AIDD depuis un clone local (zéro réseau).

Analyse un dépôt git pour extraire les traces AIDD et générer un profil.json
valide. Pas besoin d'API, pas besoin de token : tout est dans le repo cloné.

Usage :
  python scripts/generate_profile.py /chemin/vers/repo --user alice
  python scripts/generate_profile.py /chemin/vers/repo --user bob --out profil.json
  python scripts/generate_profile.py /chemin/vers/repo --user alice --verbose
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


def _git(repo: Path, args: list[str]) -> str:
    """Exécute une commande git dans le repo et retourne la sortie."""
    result = subprocess.run(
        ['git', '-C', str(repo), *args],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        return ''
    return result.stdout.strip()


def _detect_pr_sizes(repo: Path, user: str) -> list[str]:
    """Classe les PRs de l'utilisateur par taille (S/M/L/XL) via un seul appel git."""
    log = _git(
        repo,
        [
            'log',
            '--author=' + user,
            '--merges',
            '--since=1 year ago',
            '-m',
            '--first-parent',
            '--format=@@%H',
            '--shortstat',
        ],
    )
    if not log:
        return []

    sizes: list[str] = []
    current_files = 0
    for line in log.splitlines():
        if line.startswith('@@'):
            if current_files:
                sizes.append(_bucket_size(current_files))
            current_files = 0
        else:
            match = re.search(r'(\d+) files? changed', line)
            if match:
                current_files = int(match.group(1))
    if current_files:
        sizes.append(_bucket_size(current_files))

    return sizes[:50] if sizes else ['M']


def _bucket_size(total: int) -> str:
    """Convertit un nombre de fichiers modifiés en taille de PR (S/M/L/XL)."""
    if total <= 3:
        return 'S'
    if total <= 10:
        return 'M'
    if total <= 30:
        return 'L'
    return 'XL'


def _detect_context_versioned(repo: Path) -> bool:
    """Vérifie la présence de fichiers de contexte projet."""
    context_files = [
        'CLAUDE.md',
        'AGENTS.md',
        '.cursorrules',
        '.github/instructions/',
        'docs/CONCEPTS.md',
        'docs/ARCHITECTURE.md',
        '.copilot/',
        'CLAUDE.local.md',
        'CONVENTIONS.md',
    ]
    return any((repo / f).exists() for f in context_files)


def _detect_agent_rules_versioned(repo: Path) -> bool:
    """Vérifie la présence de règles/agents versionnés."""
    rules_paths = [
        '.github/workflows/',
        '.gitlab-ci.yml',
        '.agents/',
        '.claude/',
        '.opencode/',
        'skills/',
        'prompts/',
        '.aidd/',
    ]
    for p in rules_paths:
        path = repo / p
        if path.is_dir() and any(path.iterdir()):
            return True
    return False


def _detect_retry_loops(repo: Path) -> bool:
    """Détecte les boucles de relance (CI re-runs, retry patterns)."""
    ci_files = [
        '.github/workflows/',
        '.gitlab-ci.yml',
        'Makefile',
        'justfile',
        'Taskfile.yml',
    ]
    for f in ci_files:
        path = repo / f
        if path.is_dir():
            for workflow in path.glob('*.yml'):
                content = workflow.read_text(encoding='utf-8', errors='ignore')
                if re.search(
                    r'retry|rerun|re-run|continue-on-error|timeout-minutes', content, re.I
                ):
                    return True
        elif path.is_file():
            content = path.read_text(encoding='utf-8', errors='ignore')
            if re.search(r'retry|rerun|re-run', content, re.I):
                return True
    return False


def _detect_retries_after_fact(repo: Path, user: str) -> tuple[float | None, bool]:
    """Estime le ratio de reprise post-merge via commits de fix après merge."""
    log = _git(
        repo,
        [
            'log',
            '--author=' + user,
            '--format=%H %s',
            '--since=1 year ago',
            '--all',
            '-n',
            '100',
        ],
    )
    if not log:
        return None, False

    lines = log.splitlines()
    fix_patterns = re.compile(r'\b(fix|correct|amend|revert|patch|oops)\b', re.I)
    total = 0
    fixes = 0
    for line in lines:
        parts = line.split(' ', 1)
        if len(parts) < 2:
            continue
        msg = parts[1]
        total += 1
        if fix_patterns.search(msg):
            fixes += 1

    if total < 5:
        return None, False

    ratio = min(fixes / total, 1.0)
    return round(ratio, 2), True


def _detect_parallel_projects(repo: Path, user: str) -> tuple[int, int]:
    """Compte les projets parallèles et complétés via branches."""
    branches = _git(
        repo,
        [
            'branch',
            '--format=%(refname:short)',
            '--merged',
        ],
    )
    all_branches = _git(
        repo,
        [
            'branch',
            '--format=%(refname:short)',
        ],
    )

    active = [
        b
        for b in (all_branches or '').splitlines()
        if b and not b.startswith('main') and not b.startswith('master') and 'HEAD' not in b
    ]

    merged = set((branches or '').splitlines())

    parallel = max(len(active), 1)
    completed = len([b for b in active if b in merged])

    return parallel, completed


def _detect_agents_autonomous(repo: Path) -> bool:
    """Détecte les workflows autonomes (schedule, dispatch)."""
    workflows_dir = repo / '.github' / 'workflows'
    if not workflows_dir.is_dir():
        return False

    for workflow in workflows_dir.glob('*.yml'):
        content = workflow.read_text(encoding='utf-8', errors='ignore')
        if re.search(r'schedule|workflow_dispatch|repository_dispatch', content):
            return True
    return False


def _detect_prompts(repo: Path) -> bool:
    """Détecte l'utilisation de prompts structurés (fallback)."""
    prompts_files = [
        'prompts/',
        '.prompts/',
        'prompt.md',
        '.github/copilot-instructions.md',
        '.cursorrules',
        '.aiderignore',
    ]
    return any((repo / f).exists() for f in prompts_files)


def _sanitize_email(value: str) -> str:
    """Nettoie un email en le remplaçant par un slug anonyme."""
    if '@' in value:
        local = value.split('@')[0]
        return re.sub(r'[^a-z0-9]', '-', local.lower()).strip('-') or 'user'
    return value


def generate_profile(repo_path: Path, user: str, verbose: bool = False) -> dict:
    """Génère un profil AIDD complet depuis un repo local."""
    if verbose:
        print(f"[GENERATE] Analyse de {repo_path} pour l'utilisateur {user}")

    pr_sizes = _detect_pr_sizes(repo_path, user)
    context = _detect_context_versioned(repo_path)
    rules = _detect_agent_rules_versioned(repo_path)
    loops = _detect_retry_loops(repo_path)
    retries, triangulated = _detect_retries_after_fact(repo_path, user)
    parallel, completed = _detect_parallel_projects(repo_path, user)
    autonomous = _detect_agents_autonomous(repo_path)
    prompts = _detect_prompts(repo_path)

    traces = {}
    if pr_sizes:
        traces['pr_sizes'] = pr_sizes
    traces['context_versioned'] = context
    traces['agent_rules_versioned'] = rules
    traces['retry_loops'] = loops
    if retries is not None:
        traces['retries_after_fact'] = retries
    traces['retries_triangulated'] = triangulated
    traces['parallel_projects'] = parallel
    traces['projects_completed'] = completed
    traces['agents_autonomous'] = autonomous
    traces['prompts'] = prompts

    if verbose:
        print(f'[GENERATE] PR sizes: {pr_sizes}')
        print(f'[GENERATE] Context: {context}, Rules: {rules}, Loops: {loops}')
        print(f'[GENERATE] Retries: {retries} (triangulated: {triangulated})')
        print(f'[GENERATE] Parallel: {parallel}, Completed: {completed}')
        print(f'[GENERATE] Autonomous: {autonomous}, Prompts: {prompts}')

    clean_user = _sanitize_email(user)
    profile = {
        'name': f'{repo_path.name}-{clean_user}',
        'declared_level': None,
        'traces': traces,
        'answers': {},
        'meta': {
            'source': 'local_repo',
            'repo_path': repo_path.name,
            'user': clean_user,
            'generated_by': 'generate_profile.py',
        },
    }

    return profile


def main():
    # Encoding fix for Windows console
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(
        description='Génère un profil AIDD depuis un clone local (zéro réseau).'
    )
    parser.add_argument('repo', type=Path, help='Chemin vers le dépôt git cloné.')
    parser.add_argument('--user', '-u', required=True, help="Handle git de l'utilisateur.")
    parser.add_argument(
        '--out', '-o', type=Path, default=Path('profil.json'), help='Fichier de sortie.'
    )
    parser.add_argument('--verbose', '-v', action='store_true', help='Sortie détaillée.')
    args = parser.parse_args()

    if not args.repo.is_dir():
        print(f"Erreur : {args.repo} n'est pas un dossier.", file=sys.stderr)
        sys.exit(1)

    if not (args.repo / '.git').is_dir():
        print(f"Erreur : {args.repo} n'est pas un dépôt git.", file=sys.stderr)
        sys.exit(1)

    profile = generate_profile(args.repo, args.user, verbose=args.verbose)

    args.out.write_text(
        json.dumps(profile, indent=2, ensure_ascii=False),
        encoding='utf-8',
    )
    print(f'[OK] Profil genere : {args.out}')

    if args.verbose:
        print(json.dumps(profile, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
