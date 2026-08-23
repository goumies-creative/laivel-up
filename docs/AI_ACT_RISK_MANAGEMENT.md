# Gestion des Risques EU AI Act — LAIVEL UP

> **Article 9** : Système de gestion des risques pour systèmes IA
> **Version** : 0.1.0 (hackathon)
> **Date** : 2026-08-23

## Méthodologie

Matrice **Probabilité × Impact** → Niveau de risque → Mesures de mitigation → Risque résiduel.

| Probabilité | Impact | Niveau |
|-------------|--------|--------|
| Élevée | Élevé | **Critique** |
| Élevée | Moyen | **Élevé** |
| Moyenne | Élevé | **Élevé** |
| Moyenne | Moyen | **Moyen** |
| Faible | Élevé | **Moyen** |
| Faible | Moyen | **Faible** |

## Matrice des Risques

| ID | Risque | Description | Prob. | Impact | Niveau | Mitigation Implémentée | Risque Résiduel |
|----|--------|-------------|-------|--------|--------|------------------------|-----------------|
| **R1** | **Sous-évaluation (faux négatif)** | Développeur AIDD avancé classé niveau inférieur | Moyenne | Élevé | **Élevé** | Calibration 4 profils officiels 28/08 ; refus si confiance < 0.5 ; règle AND (min axes) | Moyen (dépend calibration) |
| **R2** | **Sur-évaluation (faux positif)** | Développeur débutant classé niveau supérieur | Faible | Moyen | **Faible** | Règle AND ; triangulation requise pour Intervention ; seuils taille stricts | Faible |
| **R3** | **Biais algorithmiques** | Seuils favorisent certains patterns (ex: gros PRs = XL) | Faible | Élevé | **Moyen** | Seuils dans `SCORING_DEFAULTS` configurables ; grille publique ; tests edge cases | Faible (configurable) |
| **R4** | **Fuite données personnelles** | Emails, noms réels dans exports/rapports | Faible | Élevé | **Moyen** | Pseudo-anonymisation SHA-256 (8 chars) ; exports sans PII ; opt-out (prévu) | Faible |
| **R5** | **Données d'entraînement biaisées** | N/A — pas de ML, règles déterministes | N/A | N/A | **N/A** | Pas de modèle ML ; seuils explicites dans code | N/A |
| **R6** | **Défaillance robustesse** | Crash/timeout sur gros volume | Faible | Élevé | **Moyen** | Load tests 1k profils < 5s ; timeouts CI ; validation schéma stricte | Faible |
| **R7** | **Vulnérabilité sécurité** | Injection, path traversal, déps vulnérables | Faible | Élevé | **Moyen** | Bandit + pip-audit CI ; validation entrée JSON Schema ; pas d'eval() | Faible |
| **R8** | **Absence supervision humaine** | Décision automatisée sans recours | Faible | Élevé | **Moyen** | Mode `interrogate` = HITL ; refus de trancher = questionnement | Faible |
| **R9** | **Opacité décision** | Utilisateur ne comprend pas pourquoi niveau X | Moyenne | Moyen | **Moyen** | Rapports MD/HTML explicatifs ; `METHODE.md` public ; traçabilité grille↔code | Faible |
| **R10** | **Dérive post-déploiement** | Seuils obsolètes, profils officiels changent | Moyenne | Moyen | **Moyen** | Calibration script ré-exécutable ; versionning profils ; CHANGELOG | Moyen |

## Plan de Surveillance Post-Mise sur Marché (Art. 9(6))

| Action | Fréquence | Responsable | KPI |
|--------|-----------|-------------|-----|
| Ré-exécuter calibration profils officiels | À chaque release | Maintainer | 100% profils officiels = niveau attendu |
| Surveiller issues "faux niveau" | Continue | Maintainer | < 5% signalements utilisateurs |
| Mettre à jour seuils `SCORING_DEFAULTS` | Si dérive détectée | Maintainer | Changement tracé dans CHANGELOG |
| Audit sécurité déps | Mensuel | Dependabot + pip-audit CI | 0 CVE critiques non patchées |
| Revue documentation technique | Semestriel | Maintainer | À jour vs code |

## Processus de Révision (Art. 9(2))

1. **Identification** : Nouveaux risques via issues, audits, retours utilisateurs
2. **Analyse** : Matrice P×I → niveau
3. **Évaluation** : Acceptable ? Si non → mitigation
4. **Traitement** : Code fix + test + doc + release
5. **Surveillance** : Vérifier efficacité mitigation

## Documentation Requise (Art. 11 + Annexe IV) — État Hackathon

| Élément Annexe IV | Fichier LAIVEL UP | Statut |
|-------------------|-------------------|--------|
| Description générale | `README.md`, `METHODE.md` | ✅ |
| Usage prévu | `README.md`, `QUICKSTART_JUDGES.md` | ✅ |
| Spécifications techniques | `docs/architecture.mmd`, `docs/EXTENDING.md` | ✅ |
| Méthodes développement | `aidd_docs/tasks/.../plan.md`, `spec.md` | ✅ |
| Données d'entraînement | N/A (pas de ML) | N/A |
| Mesures gestion risques | **Ce fichier** | ✅ |
| Spécifications exactitude | `METHODE.md`, tests load/edge | ✅ |
| Mesures cybersécurité | CI security (bandit, pip-audit) | ✅ |
| Système surveillance post-marché | Section ci-dessus | ✅ |

## Références

- AI Act Article 9 : https://eur-lex.europa.eu/eli/reg/2024/1689/oj#art_9
- AI Act Annexe IV : https://eur-lex.europa.eu/eli/reg/2024/1689/oj#anx_IV
- Commission Guidelines — Risk Management : https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai