# ADR-0010 : Sécurité — bandit baseline + tests sécurité, SHA-256 only

**Status** : Accepted  
**Date** : 2026-08-22  
**Décideurs** : Romy Alula

## Contexte

Outil CLI commercial-grade. Sécurité = confiance des utilisateurs.

## Décision

| Standard | Outil | Seuil |
|----------|-------|-------|
| Aucune faille haute/critique | bandit | 0 issues |
| Baseline versionnée | bandit | `tests/security/bandit-baseline.json` |
| Tests sécurité | pytest | `tests/security/` — 21 tests |
| SHA-256 only | hashlib | Pas de SHA-1/MD5 |
| Pas de secrets en dur | bandit B105/B106 | 0 findings |

### Tests sécurité (5 fichiers)
- `test_json_injection.py` : injection via JSON malveillant
- `test_path_traversal.py` : manipulation de chemins
- `test_dos_profil_giant.py` : profils géants (>1MB)
- `test_sha256_anonymization.py` : RGPD SHA-256
- `test_bandit_regression.py` : pas de nouvelles failles

## Conséquences

### Positives
- Régression sécurité détectée automatiquement
- Baseline versionnée = historique des findings

### Négatives
- Maintenance baseline si code légitime change

## Liens
- Code : `tests/security/`
- Baseline : `tests/security/bandit-baseline.json`
