# Contribuer à LAIVEL UP

## Ajouter un axe d'évaluation

1. Ajouter la clé dans `AXES` et `AXIS_LABELS` (`src/laivelup/model.py`)
2. Ajouter les seuils dans `SCORING_DEFAULTS` (`src/laivelup/scoring_defaults.py`)
3. Ajouter la logique dans `scoring.py` → `evaluate()`
4. Ajouter les tests dans `tests/test_scoring.py`
5. Mettre à jour `schemas/profile.schema.json`

## Ajouter un axe bonus (hors règle AND)

Variante de la recette ci-dessus pour un axe **optionnel**, qui ne doit
**jamais** influencer le niveau global (`min()` sur `AXES`). Un axe bonus
mesure autre chose que les axes officiels (ex. professionnalisation du
delivery plutôt que la façon dont le code a été écrit) et reste affiché à
part. Cas d'usage réel documenté : l'axe Industrialisation, voir
`docs/plans/2026-08-28-001-chore-finalisation-hackathon-plan.md` §11.7 et
`docs/adr/0017-axe-bonus-industrialisation-hors-regle-and.md`.

1. Ajouter la clé dans un tuple séparé `BONUS_AXES` (**pas** dans `AXES`)
   et le libellé dans `AXIS_LABELS` (`src/laivelup/model.py`)
2. Ajouter un champ dédié sur `Verdict` (ex. `bonus_axis_scores: list[AxisScore]`)
   — jamais dans `axis_scores`, qui alimente le `min()` du verdict principal
3. Ajouter les seuils dans une sous-clé isolée de `SCORING_DEFAULTS`
   (`src/laivelup/scoring_defaults.py`)
4. Ajouter la logique dans `scoring.py` → `evaluate()`, en **second passage
   indépendant** après le calcul de `global_level` : un axe bonus non
   tranché (confiance basse ou données absentes) ne doit jamais déclencher
   le refus du verdict principal
5. Ajouter les tests dans `tests/test_scoring.py`, avec un cas de
   non-régression explicite sur les niveaux déjà calibrés des profils
   officiels
6. Ajouter les champs `traces.*` correspondants dans
   `schemas/profile.schema.json` comme **optionnels** (jamais `required`)
7. Afficher l'axe bonus visuellement séparé du bloc verdict AND (CLI +
   rapports MD/HTML) — jamais mélangé aux axes qui déterminent le niveau

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

## Benchmark

```bash
# Subprocess benchmark (p50/p95 par commande CLI)
python scripts/benchmark.py -n 50

# In-process micro-benchmark (overhead minimal, scoring seul)
python scripts/benchmark.py --in-process -n 1000
```

Résultats : `benchmark-results.json`.

## Calibration dégradée (Plan B)

Quand `calibrate.py` échoue sur les profils officiels :

```bash
# 1. Diagnostic brut
python scripts/calibrate_degraded.py \
    --official-dir grille/profils-officiels/ \
    --expected grille/profils-officiels/expected.json \
    --output diagnostic.json

# 2. Scénario A : patch seuils (si ≤2 écarts)
python scripts/apply_calibration_fix.py \
    --scenario A --diagnostic diagnostic.json --apply

# 3. Scénarios B/C : manuels (NotImplementedError avec instructions)
python scripts/apply_calibration_fix.py --scenario B --diagnostic diagnostic.json
```

**Note** : les axes dans `calibrate_degraded.py` (`specification`, `planning`, `implementation`, `validation`) sont des noms humains pour le diagnostic. Les axes réels du scoring sont `size`, `harness`, `intervention`, `parallel` (voir `model.py`).

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

## Conformité testing

### Checklist obligatoire

Pour toute nouvelle fonctionnalité :

1. **Test unitaire** : cas nominal + cas d'erreur
2. **Test edge case** : limites, types invalides, données manquantes
3. **Test snapshot** : si CLI (sortie visible)
4. **Test de régression** : si bug corrigé

### Seuils de couverture

| Module | Couverture minimale |
|--------|---------------------|
| `scoring.py` | 100% (non-négociable) |
| `model.py` | 95% |
| `team.py` | 95% |
| `report.py` | 85% |
| `cli.py` | 80% |
| `encoding.py` | 80% (hors Windows-only) |
| `schema.py` | 80% |

### Règles de nommage

```python
# Format : test_<ce_qu'on_teste>_<ce_qu'on_s_attend>
def test_evaluate_insufficient_data_refuses():
    """Laivel Up refuse quand les données manquent."""
    result = evaluate({})
    assert not result.decided

# Pas de multi-assertions sauf même comportement
def test_slug_deterministic():
    """Slug toujours identique pour même entrée."""
    s1 = slug("alice", salt)
    s2 = slug("alice", salt)
    assert s1 == s2  # Deux assertions, même comportement
```

### Documentation

Voir `docs/TESTING_CONFORMANCE.md` pour la checklist complète.
