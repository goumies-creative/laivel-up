# ADR-0007 : Team Tracker — RGPD slug SHA-256

**Status** : Accepted  
**Date** : 2026-08-18  
**Mis à jour** : 2026-08-24 (ajout sel HMAC)  
**Décideurs** : Romy Alula

## Contexte

Suivi d'équipes multi-membres. Les rapports partagés ne doivent pas exposer les noms en clair.

## Décision

**Slug pseudo-anonymisé** : HMAC-SHA256(salt, name)[:8] + nom nettoyé

```python
# Avant (déprécié — résistant collision, pas dictionnaire)
sha256(name.encode("utf-8")).hexdigest()[:8]

# Après (sel par équipe — résistant dictionnaire)
hmac.new(salt.encode("utf-8"), name.encode("utf-8"), hashlib.sha256).hexdigest()[:8]
```

- HMAC-SHA256 avec sel aléatoire par équipe (16 bytes = 32 chars hex)
- Sel généré à `create_team()`, stocké dans le fichier équipe, jamais exporté
- Fallback sans sel pour rétro-compatibilité (lecture anciens fichiers)
- Nom nettoyé (lowercase, alphanum uniquement)
- Format : `{name}-{hash8}`

## Menaces couvertes

| Menace | Avant | Après |
|--------|-------|-------|
| Collision (8 chars = 4B) | ✅ Acceptable | ✅ Acceptable |
| Dictionnaire sur espace restreint (équipe connue) | ❌ Quelques secondes | ✅ Impossible sans sel |
| Préimage sur SHA-256 | ✅ Fort | ✅ Fort |

## Conséquences

### Positives
- RGPD compliant (résistant re-identification par dictionnaire)
- Déterministe (même entrée + même sel → même slug)
- Sel jamais exporté (ne fuit pas avec les rapports)

### Négatives
- Sel stocké côté serveur (fichier équipe) — compromis nécessaire
- Migration des anciens slugs sans sel (lecture tolérante)

## Liens
- Code : `src/laivelup/utils.py` (`slug`, `generate_team_salt`)
- Code : `src/laivelup/team.py` (`create_team`, `save_team`, `load_team`)
- Tests : `tests/test_team_rgpd.py::TestReviewFixes::test_slug_resists_dictionary_attack`
