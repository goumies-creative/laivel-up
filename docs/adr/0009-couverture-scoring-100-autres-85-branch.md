# ADR-0009 : Couverture tests — scoring 100%, autres 85%, branch

**Status** : Accepted  
**Date** : 2026-08-22  
**Décideurs** : Romy Alula

## Contexte

Seuils de couverture pour garantir la fiabilité.

## Décision

| Module | Seuil | Raison |
|--------|-------|--------|
| `scoring.py` | 100% (branch) | Cœur métier — zéro compromis |
| Tous autres `src/` | 85% (branch) | Standard industriel |
| Global | ≥85% (branch) | Seuil CI |

**Règle** : scoring.py ne peut jamais être en dessous de 100%. Les autres modules visent 85% minimum.

**Pas de `# pragma: no cover` sur la logique métier** — uniquement sur :
- Code Windows-only (VT processing, reconfigure)
- CLI interactif (Prompt.ask mocké)
- Fallback import (ImportError)

## Implémentation

Deux passes de couverture distinctes. Un run pytest n'a qu'un seul `source` de
coverage : deux seuils sur deux périmètres différents exigent deux runs.

**Passe globale — 85%**, portée par les `addopts` pytest, sur toute la CI :

```toml
# pyproject.toml
[tool.pytest.ini_options]
addopts = "-ra -q --strict-markers --strict-config --cov=src/laivelup --cov=scripts --cov-fail-under=85 --cov-branch"

[tool.coverage.run]
source = ["src/laivelup", "scripts"]
```

```console
$ pytest -q
Required test coverage of 85% reached.
```

**Passe moteur — 100% statements et branches**, step dédié du job `test` :

```yaml
# .github/workflows/ci.yml
- name: Engine coverage gate (laivelup.scoring 100%)
  run: pytest -q -o addopts="" --cov=laivelup.scoring --cov-branch --cov-fail-under=100 --cov-report=term-missing
```

```console
$ pytest -o addopts="" --cov=laivelup.scoring --cov-branch --cov-fail-under=100 --cov-report=term-missing
Required test coverage of 100% reached.
```

Trois points non négociables :

1. **`-o addopts=""` est obligatoire** sur la passe moteur. Sans lui, les `addopts`
   partagés réimposent `--cov=src/laivelup --cov=scripts --cov-fail-under=85` et
   écrasent le périmètre et le seuil du gate. C'est le même échappatoire que celui
   du runner mutmut, dans la section `[mutmut]` de `pyproject.toml`.
2. **La forme module est obligatoire** : `--cov=laivelup.scoring`. La forme chemin
   `--cov=src/laivelup/scoring.py` collecte silencieusement rien, rapporte `0.00%`
   et échoue avec un avertissement `module-not-imported` plutôt qu'avec une erreur
   d'usage visible.
3. **La passe moteur doit porter la suite complète.** La restreindre à
   `tests/test_scoring*.py` signale `scoring.py:187` — le bras de refus
   `if isolated_peak and dominant == max_present:` — comme non couvert, ce bras
   étant exercé par des tests situés hors de ce sous-ensemble. C'est le chemin de
   refus de décider : il reste couvert, jamais exclu.

### Correction 2026-09-30 : `[overrides]` n'a jamais été une fonctionnalité

Cette section décrivait auparavant le seuil de 100% sur `scoring.py` comme produit
par un bloc `[[tool.coverage.overrides]]` dans `pyproject.toml`. **coverage.py
n'a aucune section `[overrides]` dans aucune version publiée.** Le bloc était lu,
jamais signalé, puis silencieusement ignoré. La version acceptée de cette ADR
recommandait donc une configuration qui ne produisait aucun gate, et `scoring.py`
est resté non tenu à 99% derrière le seul seuil global de 85%.

Vérifié contre `coverage` 7.11.3 installé et `coverage/config.py` amont aux tags
7.4.0, 7.5.0, 7.6.0, 7.9.0, 7.10.0 et 7.11.3, où la chaîne `overrides` apparaît
zéro fois. `coverage debug config` rapporte `fail_under: 0.0` et aucune machinerie
d'override : le seul seuil vivant provenait de `--cov-fail-under=85` sur la ligne
de commande.

Le bloc mort a été supprimé de `pyproject.toml` et remplacé par la passe CI
ci-dessus. La décision elle-même — 100% sur `scoring.py`, 85% sur le reste —
n'est pas modifiée. Issue #11.

## Conséquences

### Positives
- scoring.py = zéro path non testé
- Autres modules = standard industriel
- `# pragma: no cover` = seulement ce qui est non testable

### Négatives
- Maintenance des tests = ~573 tests (572 passés, 1 ignoré), ~88% de couverture globale
- Le seuil de 100% coûte une seconde passe pytest complète (~100 s) par exécution de CI, sur 3 OS × 3 Python

## Liens
- Code : `pyproject.toml`
- Gate CI : `.github/workflows/ci.yml` — job `test`, step « Engine coverage gate (laivelup.scoring 100%) »
- Tests : `tests/`
