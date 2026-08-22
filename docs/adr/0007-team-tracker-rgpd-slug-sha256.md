# ADR-0007 : Team Tracker — RGPD slug SHA-256

**Status** : Accepted  
**Date** : 2026-08-18  
**Décideurs** : Romy Alula

## Contexte

Suivi d'équipes multi-membres. Les rapports partagés ne doivent pas exposer les noms en clair.

## Décision

**Slug pseudo-anonymisé** : `{name_clean}-{sha256[:8]}`

```python
_hashlib.sha256(name.encode("utf-8")).hexdigest()[:8]
cleaned = "".join(c if c.isalnum() else "-" for c in name.lower()).strip("-")
return f"{cleaned[:32]}-{digest}"
```

- SHA-256 (pas SHA-1/MD5)
- Digest 8 caractères hex
- Nom nettoyé (lowercase, alphanum uniquement)
- Format : `{name}-{hash8}`

## Conséquences

### Positives
- RGPD compliant
- Déterministe (même entrée → même slug)
- Irréversible (SHA-256)

### Négatives
- Collision possible (8 chars = 4 billions) — acceptable pour usage interne

## Liens
- Code : `src/laivelup/team.py` (`_slug`)
- Tests : `tests/security/test_sha256_anonymization.py`
