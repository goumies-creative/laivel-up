# ADR-0012 : Profil JSON Schema — Draft 2020-12, fallback minimal

**Status** : Accepted  
**Date** : 2026-08-20  
**Décideurs** : Romy Alula

## Contexte

Validation des profils JSON. Standard à utiliser.

## Décision

- **JSON Schema Draft 2020-12** : standard actuel
- **Fallback minimal** : `_validate_minimal()` sans jsonschema
- **Validation fail-fast** : profil invalide → erreur claire, pas de crash

### Schema
```json
{
  "declared_level": {"anyOf": [{"enum": ["WHITE",...]}, {"type": "null"}]},
  "traces": {"type": "object", "properties": {...}}
}
```

## Conséquences

### Positives
- Standard JSON Schema = interopérabilité
- Fallback = fonctionne sans jsonschema
- Validation rapide = erreurs lisibles

### Négatives
- Maintenance schema = 2 endroits (schema + fallback)

## Liens
- Code : `src/laivelup/schema.py`, `schemas/profile.schema.json`
- Tests : `tests/test_schema_extended.py`
