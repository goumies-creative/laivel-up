# ADR-0002 : Convention nommage FR→EN — Code EN, docstrings FR

**Status** : Accepted  
**Date** : 2026-08-15  
**Décideurs** : Romy Alula

## Contexte

Projet bilingue (FR/EN). Convention à choisir pour les identifiants code vs documentation visible.

## Décision

| Élément | Langue | Raison |
|---------|--------|--------|
| Noms de variables/fonctions/classes | EN | Convention open-source, pas de switching mental à la lecture |
| Docstrings | FR | Signature La Décodeuse, accessible aux non-anglophones |
| Messages d'erreur | EN | Convention Python, interopérabilité |
| Commentaires | FR | Documentation interne, accessibilité |
| Noms de fichiers | EN | Convention universelle, pas d'accents dans les chemins |
| Contenu visible (CLI) | FR | UX pour l'utilisateur final |

## Exemple

```python
# Avant (FR) — switching mental
taille_max(profile)
parallele_max(profile)

# Après (EN) — naturel en lecture code
size_max(profile)
parallel_max(profile)
```

## Conséquences

### Positives
- Pas de switching FR/EN quand on lit le code
- Convention respectée par les outils (ruff, mypy, IDE)
- Docstrings FR = signature La Décodeuse (pas de neurotype, pas de jargon technique)

### Négatives
- Debug : messages d'erreur EN pour utilisateurs FR (mitigé par traduction CLI)

## Liens
- `QUALITY.md` §2.1
- `CONTRIBUTING.md`
