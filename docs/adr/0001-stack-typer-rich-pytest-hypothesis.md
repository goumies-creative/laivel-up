# ADR-0001 : Stack technique — Typer + Rich + pytest + hypothesis

**Status** : Accepted  
**Date** : 2026-08-15  
**Décideurs** : Romy Alula

## Contexte

Le hackathon AIDD impose un outil d'évaluation CLI. Choix des dépendances principale : framework CLI, rendering TUI, tests, validation.

## Décision

| Composant | Choix | Version |
|-----------|-------|---------|
| CLI | Typer | ≥0.20 |
| TUI/Rendering | Rich | latest |
| Tests | pytest | ≥8.0 |
| Property-based | hypothesis | ≥6.90 |
| Snapshots | pytest-snapshot | ≥0.8 |
| Lint | ruff | ≥0.5 |
| Type check | mypy | ≥1.10 |
| Sécurité | bandit | ≥1.7 |
| Build | setuptools | ≥68 |
| Python | ≥3.11 | — |

## Conséquences

### Positives
- Typer : type hints natifs → auto-completion shell, validation `--help` générée
- Rich : markdown, tables, progress bars, emoji handling, auto-détection UTF-8
- pytest : fixtures, parametrize, coverage intégré, plugins riches
- hypothesis : invariantes fondamentaux, tests property-based pour invariants métier

### Négatives
- Typer dépend de Click (poids) — acceptable pour un CLI
- Rich : dépendance lourde mais justifiée par le rendering

## Alternatives rejetées
- **Click** : pas de type hints natifs, moins d'intégration Rich
- **argparse** : pas d'auto-completion, verbose
- **Textual** : TUI complète = overkill, pas de sortie HTML native

## Liens
- Code : `pyproject.toml`
- Tests : `tests/`
