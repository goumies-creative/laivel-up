# ADR-0005 : La Décodeuse — Refus > deviner, questions ciblées, rotation

**Status** : Accepted  
**Date** : 2026-08-15  
**Décideurs** : Romy Alula

## Contexte

L'outil d'évaluation doit être éthique et ne pas inventer de niveau. Pattern La Décodeuse : refus de trancher plutôt que de deviner.

## Décision

**Refus > deviner** : quand les données manquent, l'outil pose des questions au lieu d'arbitrer.

### Mécanisme
1. **Questions ciblées** : chaque refus génère des questions pour lever l'incertitude
2. **Rotation anti-boucle** : pas de question déjà posée
3. **Mode interview** : `laivelup interrogate` — interaction guidée tour par tour
4. **Fusion réponses** : `_merge_answer()` parse les réponses en traces

### Exemple
```json
// Pas de pr_sizes → question
"Quelle est la taille habituelle de tes features livrées avec l'IA (S, M, L, XL) ?"
```

## Conséquences

### Positives
- Zéro niveau arbitraire
- Transparence totale sur les données manquantes
- UX pédagogique (l'utilisateur comprend ce qui manque)

### Négatives
- Plus de interactions (mitigé : `--max-turns`)

## Liens
- Code : `src/laivelup/scoring.py` (`_questions_for`), `src/laivelup/cli.py` (`interrogate`)
- Tests : `tests/test_scoring_edge.py`, `tests/test_cli_extended.py`
