#!/usr/bin/env python3
# Copyright 2026 Romy Alula — MIT License
"""Script de démo LAIVEL UP — scénario 2 min pour enregistrement asciinema.

Usage:
    asciinema rec demo.cast -c "python scripts/demo.py"
    agg demo.cast demo.gif --theme monokai --speed 2
    agg demo.cast demo.mp4 --theme monokai --speed 1.5
    ffmpeg -i demo.mp4 -vf "subtitles=demo.srt" demo-final.mp4
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

DEMO_DIR = Path(__file__).resolve().parent.parent
PROFILS = [
    (
        'profil-maison-1.json',
        'Profil 1 : contexte + règles',
        'Contexte versionné, règles agents : des fondations solides.',
    ),
    (
        'profil-maison-2.json',
        'Profil 2 : boucles de relance',
        'Reprises après coup : le moteur ne croit pas le déclaratif.',
    ),
]

PAUSE_SHORT = 2
PAUSE_MEDIUM = 4
PAUSE_LONG = 6


def _run(cmd: str, label: str, comment: str = '', pause: int = PAUSE_MEDIUM) -> None:
    """Affiche un commentaire explicatif, exécute une commande CLI, affiche un séparateur."""
    if comment:
        print('#')
        print(f'# {comment}')
    print(f'\n{"=" * 60}')
    print(f'  {label}')
    print(f'{"=" * 60}\n')
    result = subprocess.run(
        cmd.split(),
        capture_output=False,
        text=True,
        cwd=str(DEMO_DIR),
        timeout=30,
    )
    if result.returncode != 0:
        print(f'\n[ERREUR] Commande échouée : {cmd}', file=sys.stderr)
    time.sleep(pause)


def main() -> None:
    """Scénario démo complet 5 étapes (~50s + pauses)."""
    print("LAIVEL UP · Démo CLI d'évaluation AIDD\n")
    print('Refus de deviner : des questions, jamais de verdicts arrachés.')
    time.sleep(PAUSE_SHORT)

    # Étape 1 : Aide
    _run(
        'laivelup --help',
        "Étape 1 · Découvrir l'outil",
        'Toutes les commandes, en un écran.',
        PAUSE_SHORT,
    )

    # Étape 2 : Évaluation profil 1
    for profil, description, comment in PROFILS:
        profil_path = DEMO_DIR / 'exemples' / profil
        if profil_path.exists():
            _run(
                f'laivelup evaluate {profil_path} --no-html',
                'Étape 2 · Évaluer les profils',
                f'{description} · {comment}',
                PAUSE_LONG,
            )
        else:
            print(f'  [IGNORÉ] Profil absent : {profil}')

    # Étape 3 : Création équipe
    _run(
        'laivelup team create DemoEquipe Alice,Bob,Charlie',
        'Étape 3 · Créer une équipe',
        'Pseudo-anonymisation RGPD : les noms ne sortent jamais en clair.',
        PAUSE_MEDIUM,
    )

    # Étape 4 : Évaluation membre
    # Note fonctionnelle (audit copy-francaise-integrale.md) : le slug reel
    # d'Alice est pseudo-anonymise (alice-xxxxxxxx), pas le litteral 'alice'.
    # On le relit depuis le fichier d'equipe genere a l'etape 3 pour eviter
    # un echec de commande pendant la demo.
    profil_path = DEMO_DIR / 'exemples' / PROFILS[0][0]
    team_file = DEMO_DIR / '.laivelup' / 'teams' / 'DemoEquipe.json'
    alice_slug = 'alice'
    if team_file.exists():
        team_data = json.loads(team_file.read_text(encoding='utf-8'))
        for slug_key, member in team_data.get('members', {}).items():
            if member.get('name') == 'Alice':
                alice_slug = slug_key
                break
    if profil_path.exists():
        _run(
            f'laivelup team evaluate DemoEquipe {alice_slug} {profil_path}',
            'Étape 4 · Évaluer un membre',
            "Même moteur, au service de l'équipe.",
            PAUSE_MEDIUM,
        )

    # Étape 5 : Export
    rapport_dir = DEMO_DIR / 'rapports'
    rapport_dir.mkdir(exist_ok=True)
    _run(
        f'laivelup team export DemoEquipe --format md --out {rapport_dir}',
        'Étape 5 · Exporter',
        'Un rapport prêt à partager.',
        PAUSE_SHORT,
    )

    print(f'\n{"=" * 60}')
    print('  FIN DE LA DÉMO')
    print(f'{"=" * 60}')
    print(f'\nRapports générés dans : {rapport_dir}')


if __name__ == '__main__':
    main()
