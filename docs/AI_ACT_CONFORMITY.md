# Déclaration de Conformité EU AI Act — LAIVEL UP

> **Version** : 0.1.0 (hackathon)
> **Date** : 2026-08-23
> **Statut** : Auto-évaluation pré-déploiement — réviser post-hackathon

## Classification du Système

| Critère | Valeur | Référence |
|---------|--------|-----------|
| **Type** | Système IA à usage général (GPAI) + évaluation de personnes | Art. 3(1) |
| **Niveau de risque** | **Risque limité** (transparence) | Art. 50 |
| **Usage prévu** | Évaluation niveau AIDD développeur via traces observables | — |
| **Décision automatisée** | Non (refus de trancher si données insuffisantes, HITL via `interrogate`) | Art. 22 RGPD + Art. 14 AI Act |

> ⚠️ **Note** : Le système n'opère **pas** de notation continue (social scoring) ni de décision juridiquement contraignante → Art. 5(1)(c) scoring social **non applicable**.

## Exigences Applicables & Couverture

| Exigence AI Act | Article | Couverture LAIVEL UP | Preuve |
|-----------------|---------|---------------------|--------|
| **Transparence utilisateur** | Art. 50 | ✅ Partielle | Notice dans `README.md` + CLI `--help` |
| **Documentation technique** | Art. 11 + Annexe IV | ✅ Partielle | `docs/architecture.mmd`, `METHODE.md`, `docs/EXTENDING.md` |
| **Gestion des risques** | Art. 9 | ⚠️ En cours | `docs/AI_ACT_RISK_MANAGEMENT.md` (ce repo) |
| **Qualité des données** | Art. 10 | ⚠️ Partielle | Profils officiels 28/08 = référence ; tests load/robustesse |
| **Conservation documentation** | Art. 18 | ❌ Non applicable | Hackathon : artefacts CI 30j seulement |
| **Supervision humaine (HITL)** | Art. 14 | ✅ | Mode `interrogate` = boucle humaine |
| **Exactitude, robustesse, cybersécurité** | Art. 15 | ✅ | Tests load (1k profils < 5s), security CI (bandit, pip-audit), calibrate |

## Mesures de Transparence (Art. 50)

1. **Notice utilisateur** : "Cet outil évalue votre adoption AIDD via des heuristiques algorithmiques. Les résultats sont indicatifs, non contraignants."
2. **Documentation méthode** : `METHODE.md` — algorithme complet, grille ↔ code traçable
3. **Rapports explicables** : Chaque verdict liste axe plancher, red flags, next steps
4. **Refus de trancher** : Si confiance < 0.5 ou données manquantes → questions ciblées

## Gestion des Risques (Art. 9) — Résumé

Voir `docs/AI_ACT_RISK_MANAGEMENT.md` pour la matrice complète.

| Risque Principal | Probabilité | Impact | Mitigation |
|------------------|-------------|--------|------------|
| Faux négatif (sous-évaluation) | Moyenne | Élevé | Calibration profils officiels, refus si confiance faible |
| Faux positif (sur-évaluation) | Faible | Moyen | Règle AND (min des axes), triangulation requise |
| Biais données entraînement | N/A | N/A | Pas de ML — règles déterministes, seuils configurables |
| Fuite données personnelles | Faible | Élevé | Pseudo-anonymisation SHA-256, pas de PII en export, opt-out |

## Registre des Traitements (Art. 30 RGPD + Art. 18 AI Act)

Voir `docs/RGPD_REGISTER.md` (optionnel, hackathon).

## Conformité Post-Hackathon (Roadmap)

| Action | Échéance | Responsable |
|--------|----------|-------------|
| Documentation technique complète (Annexe IV) | Post-hackathon | Maintainer |
| Audit tiers sécurité | Post-hackathon | Maintainer |
| Processus surveillance post-mise sur marché | v1.0.0 | Maintainer |
| Mise à jour déclaration si évolution risque | Continue | Maintainer |

## Liens Officiels

- **Règlement (UE) 2024/1689** (AI Act) : https://eur-lex.europa.eu/eli/reg/2024/1689/oj
- **Article 50 — Transparence** : https://eur-lex.europa.eu/eli/reg/2024/1689/oj#art_50
- **Article 9 — Gestion des risques** : https://eur-lex.europa.eu/eli/reg/2024/1689/oj#art_9
- **Article 14 — Supervision humaine** : https://eur-lex.europa.eu/eli/reg/2024/1689/oj#art_14
- **Article 15 — Exactitude, robustesse, cybersécurité** : https://eur-lex.europa.eu/eli/reg/2024/1689/oj#art_15
- **Annexe IV — Documentation technique** : https://eur-lex.europa.eu/eli/reg/2024/1689/oj#anx_IV
- **Guidelines Commission — Classification risque** : https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai