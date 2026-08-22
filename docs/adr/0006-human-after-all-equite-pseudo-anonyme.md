# ADR-0006 : Human After All — Équité structurelle, pseudo-anonyme

**Status** : Accepted  
**Date** : 2026-08-15  
**Décideurs** : Romy Alula

## Contexte

L'évaluation ne doit pas discriminer. Aucun neurotype, aucune donnée sensible.

## Décision

**Équité structurelle** :
- Jamais de verdict plus bas que ce que les données prouvent
- Valeur inconnue/contradictoire → refus + question, jamais niveau arbitraire
- `retries_after_fact` auto-déclaré non triangulé → confiance basse → refus
- Le neurotype n'est **jamais demandé ni inféré**
- Hyperfocus : le pic est signalé en preuve, le niveau reste sur l'habituel
- White n'est jamais « deviné » par défaut

**Pseudo-anonyme RGPD** :
- Slug : `{name}-{sha256[:8]}` pour les rapports partagés
- SHA-256 (pas SHA-1/MD5) pour le hashing

## Conséquences

### Positives
- Aucune discrimination structurelle
- RGPD compliant
- Transparence sur les biais potentiels

### Négatives
- Moins de données pour les juges (mitigé : transparence)

## Liens
- Code : `src/laivelup/team.py`, `src/laivelup/scoring.py`
- Tests : `tests/security/test_sha256_anonymization.py`
