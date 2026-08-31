# LAIVEL UP · CLI d'évaluation AIDD

> Moteur d'évaluation du niveau d'adoption de l'**AI-Driven Development** des développeurs.
> Approche La Décodeuse : refus de deviner, questions au lieu de verdicts.

[![CI](https://github.com/goumies-creative/laivel-up/actions/workflows/ci.yml/badge.svg)](https://github.com/goumies-creative/laivel-up/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/goumies-creative/laivel-up)](https://github.com/goumies-creative/laivel-up/releases)
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

# Dev (pre-commit obligatoire jusqu'au 31/08)
pip install -e ".[dev]"
pre-commit install
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
| `interrogate [profil]` | Mode entretien guidé : mené par l'évaluateur·rice avec la personne évaluée — questions ouvertes, re-score itératif |
| `team create <nom> <membres>` | Crée une équipe avec pseudo-anonymisation RGPD |
| `team evaluate <équipe> <slug> <profil>` | Évalue un membre de l'équipe |
| `team export <équipe> --format <fmt>` | Exporte en MD, HTML, CSV ou JSON |
| `team opt-out <équipe> <slug> [--enable/--disable]` | Active/désactive l'opt-out RGPD |
| `team remove <équipe> <slug> [--purge]` | Supprime un membre (historique optionnel) |

> **RGPD** : `opt-out` = droit d'opposition (art. 21 · refus d'évaluation +
> exclusion des exports, réversible via `--disable`) · `remove --purge` =
> droit à l'effacement (art. 17 · membre + historique supprimés). Les
> exports ne contiennent que les pseudo (slugs HMAC).

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
    utils.py        → slug HMAC-SHA256 + generate_team_salt
    questions.py    → QUESTION_IDS dict partagé scoring/CLI
    encoding.py     → UTF-8 cross-platform

tests/
    test_scoring.py     → tests unitaires du moteur
    test_scoring_edge.py → tests edge cases du moteur (48 tests)
    test_cli.py         → tests du CLI
    test_cli_extended.py → tests étendus du CLI (43 tests)
    test_interactive.py → tests du mode interrogate
    test_properties.py  → tests property-based (hypothesis)
    test_snapshots.py   → tests snapshot de sortie CLI
    test_team.py        → tests du Team Tracker
    test_team_rgpd.py   → tests RGPD (HMAC, XSS, opt-out)
    test_report.py      → tests des rapports MD/HTML
    test_encoding.py    → tests encodage cross-platform
    test_schema_extended.py → tests validation JSON schema
    security/           → tests sécurité (22 tests)

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

## Pipeline d'évaluation

Les profils doivent être **standardisés** avant évaluation. La chaîne complète :

```
scripts/extract_official_profile.py   ← convertit les données brutes
         ↓
grille/profils-officiels/*.json       ← format normalisé (ProfileData)
         ↓
scripts/calibrate.py                  ← vérifie la calibration
         ↓
laivelup evaluate <profil>.json       ← évalue et génère les rapports
```

> ⚠️ Ne jamais lancer `laivelup evaluate` sur des fichiers non standardisés.
> Utiliser d'abord `scripts/extract_official_profile.py` pour convertir
> les données brutes en format `ProfileData`.

| Script | Rôle | Usage |
|--------|------|-------|
| `extract_official_profile.py` | Extrait et standardise les profils bruts | `python scripts/extract_official_profile.py --source ../laivel-up/profiles` |
| `calibrate.py` | Vérifie que les verdicts correspondent aux niveaux attendus | `python scripts/calibrate.py --expected grille/profils-officiels/expected.json --diff` |

## Licence

MIT. AI-Driven Dev pourra réutiliser le projet en attribuant le travail à l'auteur.

---

## Pour les juges

> **Note CI :** les jobs GitHub Actions sont actuellement bloqués par la
> facturation du compte (limite de dépense), pas par le code. Tous les
> contrôles passent en local et via pre-commit : 495 tests, ruff, mypy,
> bandit, coverage 95 %. Ils relanceront dès la régularisation du billing.

### Installation rapide

```bash
pip install laivelup
```

### Complétion shell (bash/zsh/fish/PowerShell)

```bash
laivelup --install-completion
```

Active l'auto-complétion des commandes et options au premier `Tab`,
cross-shell (fournie nativement par Typer). Après l'installation, recharger
le shell (`source ~/.bashrc`, ou ouvrir un nouveau terminal), puis taper la
commande **sans extension** : `laivelup e` + `Tab` complète en `evaluate`.
(Nommer la commande `laivelup.exe` via la complétion par défaut de bash est
normal : la complétion des arguments s'applique après le nom de commande.)

**Windows · Git Bash :** si votre `~/.bashrc` contient des caractères hors
ANSI (accents, émojis), la commande peut échouer avec `UnicodeDecodeError`
(bug Typer en amont : lecture du rc sans encodage explicite, non corrigé
sur master). Contournement : ajouter à la main cette ligne dans
`~/.bashrc` :

```bash
source <(_LAIVELUP_COMPLETE=source_bash laivelup)
```

**PowerShell :** même mécanisme, à ajouter dans votre `$PROFILE` :

```powershell
_LAIVELUP_COMPLETE=source_powershell laivelup | Out-String | Invoke-Expression
```

### Évaluation d'un profil

```bash
laivelup evaluate exemples/profil-maison-1.json
```

### Mode entretien guidé (La Décodeuse)

```bash
laivelup interrogate exemples/profil-maison-1.json --max-turns 6
```

### Équipe RGPD

```bash
laivelup team create Equipe-Alpha "Alice,Bob,Charlie"
laivelup team evaluate Equipe-Alpha alice-2bd806c9 exemples/profil-maison-1.json
laivelup team export Equipe-Alpha --format md
laivelup team opt-out Equipe-Alpha bob-81b637d8
laivelup team remove Equipe-Alpha bob-81b637d8 --purge
```

### Critères d'évaluation

Libellés repris tels quels du sujet officiel (`SUJET.md`) — à vous de juger, pas à nous.

| Critère | Preuve à vérifier |
|---------|-------------------|
| 🎯 Le bon niveau ? | `python scripts/calibrate.py --expected grille/profils-officiels/expected.json --diff` — refuse un niveau (`UNDECIDED`) plutôt que d'en deviner un quand les données manquent |
| 💬 On comprend pourquoi ? | `laivelup evaluate <profil> --verbose` + rapports MD/HTML — chaque verdict documente ses sources et ses limites |
| 🔧 Comment tu l'as construit ? | `aidd_docs/` (sessions, audits, ADR) — orchestration OpenCode + compound-engineering, harnais documenté de bout en bout |
| ✨ La qualité est là ? | 495 tests (95% coverage), ruff/mypy/bandit ✅, CI matrix 3OS × 3Python — voir `QUALITY.md` |

### Vidéo démo

Voir [docs/VIDEO_PRODUCTION.md](docs/VIDEO_PRODUCTION.md) pour la vidéo 2 min.