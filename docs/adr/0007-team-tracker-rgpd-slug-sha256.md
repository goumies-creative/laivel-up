# ADR-0007 : Team Tracker — RGPD slug SHA-256

**Status** : Accepted  
**Date** : 2026-08-18  
**Mis à jour** : 2026-08-24 (ajout sel HMAC + périmètre)  
**Décideurs** : Romy Alula

## Contexte

Suivi d'équipes multi-membres. Les rapports partagés ne doivent pas exposer les noms en clair.

## Périmètre

L'HMAC-SHA256 salé s'applique au **Team Tracker uniquement** — les rapports partagés via `team export`. Le chemin `evaluate`/`interrogate` (usage individuel local) utilise le slug sans sel, les fichiers restant sur le poste de l'utilisateur·rice sans fuite externe.

| Chemin | Sel | Usage |
|--------|-----|-------|
| `team.py` → `_slug(name, salt)` | ✅ Sel HMAC-SHA256 | Rapports d'équipe partagés |
| `report.py` → `_slug(name)` | ❌ SHA-256 brut | Fichiers individuels locaux |

## Décision

**Slug pseudo-anonymisé** : HMAC-SHA256(salt, name)[:8] + nom nettoyé

```python
# Team Tracker (salé — résistant dictionnaire)
hmac.new(salt.encode("utf-8"), name.encode("utf-8"), hashlib.sha256).hexdigest()[:8]

# Usage individuel (non salé — fichiers locaux uniquement)
sha256(name.encode("utf-8")).hexdigest()[:8]
```

- HMAC-SHA256 avec sel aléatoire par équipe (16 bytes = 32 chars hex)
- Sel généré à `create_team()`, stocké dans le fichier équipe, jamais exporté
- Fallback sans sel pour usage individuel + rétro-compatibilité
- Nom nettoyé (lowercase, alphanum uniquement)
- Format : `{name}-{hash8}`

## Menaces couvertes

| Menace | Team Tracker (salé) | Individuel (non salé) |
|--------|---------------------|----------------------|
| Collision (8 chars = 4B) | ✅ Acceptable | ✅ Acceptable |
| Dictionnaire sur espace restreint | ✅ Impossible sans sel | ⚠️ Possible (fichier local) |
| Fuite externe du fichier | ✅ Impossible (jamais exporté) | ✅ Fichier reste sur le poste |

## Conséquences

### Positives
- RGPD compliant pour les rapports partagés (résistant re-identification par dictionnaire)
- Déterministe (même entrée + même sel → même slug)
- Sel jamais exporté (ne fuit pas avec les rapports)
- Usage individuel simple sans gestion de sel

### Négatives
- Sel stocké côté serveur (fichier équipe) — compromis nécessaire
- Deux chemins de slug à maintenir (team vs report)

## Liens
- Code : `src/laivelup/utils.py` (`slug`, `generate_team_salt`)
- Code : `src/laivelup/team.py` (`create_team`, `save_team`, `load_team`)
- Code : `src/laivelup/report.py` (`_slug` — usage individuel)
- Tests : `tests/test_team_rgpd.py::TestReviewFixes::test_slug_resists_dictionary_attack`
