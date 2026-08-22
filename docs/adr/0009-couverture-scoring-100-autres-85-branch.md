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

```toml
# pyproject.toml
[tool.pytest.ini_options]
addopts = "--cov-fail-under=85 --cov-branch"

[[tool.coverage.overrides]]
module = "laivelup.scoring"
fail_under = 100
```

## Conséquences

### Positives
- scoring.py = zéro path non testé
- Autres modules = standard industriel
- `# pragma: no cover` = seulement ce qui est non testable

### Négatives
- Maintenance des tests = ~180 tests, ~97% couverture

## Liens
- Code : `pyproject.toml`
- Tests : `tests/`
