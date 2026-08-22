# Contribuer à LAIVEL UP

## Ajouter un axe d'évaluation

1. Ajouter la clé dans `AXES` et `AXIS_LABELS` (`src/laivelup/model.py`)
2. Ajouter les seuils dans `SCORING_DEFAULTS` (`src/laivelup/scoring_defaults.py`)
3. Ajouter la logique dans `scoring.py` → `evaluate()`
4. Ajouter les tests dans `tests/test_scoring.py`
5. Mettre à jour `schemas/profile.schema.json`

## Ajouter un niveau

1. Ajouter dans `Level` enum (`model.py`)
2. Ajouter dans `LEVEL_LABELS` (`model.py`)
3. Ajouter seuils dans `SCORING_DEFAULTS` si nécessaire
4. Mettre à jour `docs/GRID_QUICKREF.md`

## Ajouter un format de sortie

1. Implémenter dans `src/laivelup/report.py`
2. Ajouter option `--format` dans `cli.py`
3. Ajouter test snapshot dans `tests/test_snapshots.py`

## Ajouter une commande CLI

1. Créer fonction dans `cli.py` avec décorateur `@app.command()`
2. Ajouter test dans `tests/test_cli.py`
3. Mettre à jour `README.md`

## Hooks (optionnel)

```python
from typing import Protocol

class EvaluatorHook(Protocol):
    def before_evaluate(self, profile: dict) -> dict: ...
    def after_evaluate(self, result: dict) -> dict: ...
```

Voir `src/laivelup/hooks.py` (Phase 4).

## Plugins (optionnel)

Entrées `pyproject.toml` :

```toml
[project.entry-points."laivelup.plugins"]
mon_plugin = "mon_plugin:Plugin"
```

Voir `src/laivelup/plugins.py` (Phase 4).
