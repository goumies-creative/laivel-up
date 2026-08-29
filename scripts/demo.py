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

import subprocess
import sys
import time
from pathlib import Path

DEMO_DIR = Path(__file__).resolve().parent.parent
PROFILS = [
    (
        'profil-maison-1.json',
        'Profil 1 : contexte + rules',
        'Contexte versionné, règles agent : signal de rigueur',
    ),
    (
        'profil-maison-2.json',
        'Profil 2 : boucles de relance',
        'Retries après coup : le moteur ne triche pas la lecture',
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
    )
    if result.returncode != 0:
        print(f'\n[ERREUR] Commande échouée : {cmd}', file=sys.stderr)
    time.sleep(pause)


def main() -> None:
    """Scénario démo complet 5 étapes (~50s + pauses)."""
    print("LAIVEL UP — Démo CLI d'évaluation AIDD\n")
    print('Méthode : refus de deviner, questions au lieu de verdicts.')
    time.sleep(PAUSE_SHORT)

    # Étape 1 : Aide
    _run(
        'laivelup --help', 'Étape 1 : Aide CLI', 'Découvrir les commandes disponibles', PAUSE_SHORT
    )

    # Étape 2 : Évaluation profil 1
    for profil, description, comment in PROFILS:
        profil_path = DEMO_DIR / 'exemples' / profil
        if profil_path.exists():
            _run(
                f'laivelup evaluate {profil_path} --no-html',
                f'Étape 2 : {description}',
                comment,
                PAUSE_LONG,
            )
        else:
            print(f'  [SKIP] Profil absent : {profil}')

    # Étape 3 : Création équipe
    _run(
        'laivelup team create DemoEquipe Alice,Bob,Charlie',
        'Étape 3 : Création équipe (RGPD)',
        "Le nom n'apparaît jamais en clair dans les rapports",
        PAUSE_MEDIUM,
    )

    # Étape 4 : Évaluation membre
    profil_path = DEMO_DIR / 'exemples' / PROFILS[0][0]
    if profil_path.exists():
        _run(
            f'laivelup team evaluate DemoEquipe alice {profil_path}',
            'Étape 4 : Évaluation membre',
            'Même moteur, agrégé au niveau équipe',
            PAUSE_MEDIUM,
        )

    # Étape 5 : Export
    rapport_dir = DEMO_DIR / 'rapports'
    rapport_dir.mkdir(exist_ok=True)
    _run(
        f'laivelup team export DemoEquipe --format md --out {rapport_dir}',
        'Étape 5 : Export résultats',
        'Rapport exportable, prêt à partager',
        PAUSE_SHORT,
    )

    print(f'\n{"=" * 60}')
    print('  FIN DE LA DÉMO')
    print(f'{"=" * 60}')
    print(f'\nRapports générés dans : {rapport_dir}')


if __name__ == '__main__':
    main()
