# LAIVEL UP · CLI d'évaluation AIDD

> Moteur d'évaluation du niveau **AI-Driven Development** d'un développeur.
> Approche La Décodeuse : refus de deviner, questions au lieu de verdicts.

[![CI](https://github.com/ai-driven-dev/laivel-up/actions/workflows/ci.yml/badge.svg)](https://github.com/ai-driven-dev/laivel-up/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

## Installation

```bash
# Via pip (recommandé)
pip install laivelup

# Via pipx (isolé)
pipx install laivelup

# Via uv
uv tool install laivelup
```

## Utilisation rapide

```bash
# Évaluer un profil JSON
laivelup evaluate profil.json

# Évaluer sans rapport HTML
laivelup evaluate profil.json --no-html

# Mode entretien guidé (La Décodeuse)
laivelup interrogate profil.json

# Gérer des équipes
laivelup team create "Alpha" "Alice,Bob,Charlie"
laivelup team evaluate "Alpha" <slug> profil.json
laivelup team export "Alpha" --format html
```

## Commandes

| Commande | Description |
|----------|-------------|
| `evaluate <profil>` | Évalue un profil et génère les rapports MD/HTML |
| `interrogate [profil]` | Mode entretien guidé : questions ouvertes, re-score itératif |
| `team create <nom> <membres>` | Crée une équipe avec pseudo-anonymisation RGPD |
| `team evaluate <équipe> <slug> <profil>` | Évalue un membre de l'équipe |
| `team export <équipe> --format <fmt>` | Exporte en MD, HTML, CSV ou JSON |

## Options

| Option | Description |
|--------|-------------|
| `--out <dossier>` | Dossier de sortie des rapports (défaut : `rapports/`) |
| `--html / --no-html` | Activer/désactiver le rapport HTML |
| `--verbose, -v` | Sortie technique détaillée |
| `--max-turns <n>` | Nombre max de questions en mode interrogate (défaut : 6) |
| `--format <fmt>` | Format d'export : md, html, csv, json |

## Structure du projet

```
src/laivelup/
    __init__.py     → version du package
    cli.py          → CLI Typer (evaluate, interrogate, team)
    model.py        → données (Level, AxisScore, Verdict, ProfileData)
    scoring.py      → moteur d'évaluation (grille AIDD 4 axes × 7 niveaux)
    report.py       → génération de rapports Markdown + HTML
    team.py         → Team Tracker (équipes, historique, export)

tests/
    test_scoring.py     → tests unitaires du moteur
    test_cli.py         → tests du CLI
    test_interactive.py → tests du mode interrogate
    test_properties.py  → tests property-based (hypothesis)
    test_snapshots.py   → tests snapshot de sortie CLI
    test_team.py        → tests du Team Tracker

exemples/           → profils de test JSON
grille/             → grille officielle AIDD
```

## Méthode d'évaluation

Voir [METHODE.md](METHODE.md) pour la description complète de l'algorithme.

**Principes clés :**

- **Règle AND** : un niveau n'est atteint que si tous ses 4 axes le sont
- **Refus de deviner** : données insuffisantes → questions, jamais de niveau arbitraire
- **Équité structurelle** : aucun neurotype demandé ni inféré
- **Transparence** : chaque verdict documente ses sources et limites

## Licence

MIT. AI-Driven Dev pourra réutiliser le projet en attribuant le travail à l'auteur.