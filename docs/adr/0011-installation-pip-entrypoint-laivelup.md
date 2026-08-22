# ADR-0011 : Installation — pip install + entry point laivelup

**Status** : Accepted  
**Date** : 2026-08-15  
**Décideurs** : Romy Alula

## Contexte

Distribution de l'outil. Installation simple pour les utilisateurs.

## Décision

| Méthode | Commande |
|---------|----------|
| pip | `pip install laivelup` |
| pipx | `pipx install laivelup` |
| uv | `uv tool install laivelup` |
| Dev | `pip install -e ".[dev]"` |

**Entry point** : `laivelup = "laivelup.cli:app"`

## Conséquences

### Positives
- Zéro friction d'installation
- Compatible pip/pipx/uv
- Dev mode = editable install

### Négatives
- Pas de CLI wrapper externe (acceptable)

## Liens
- Code : `pyproject.toml` (`[project.scripts]`)
