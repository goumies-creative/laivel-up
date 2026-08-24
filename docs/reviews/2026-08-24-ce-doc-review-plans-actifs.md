---
type: doc-review
skill: ce-doc-review (condensé manuel, sans dispatch subagents — contexte Claude Desktop/web sans Task tool)
date: 2026-08-24
scope: docs/plans/*.md (5 documents actifs)
---

# Review — Plans actifs LAIVEL UP (5 documents)

Méthodologie ce-doc-review appliquée manuellement (lenses simulées en un seul passage, pas de dispatch subagents — non disponible hors Claude Code). Classification + personas sélectionnées selon les règles du skill, findings tiérés.

---

## Vue d'ensemble classification

| Doc | Type détecté | Personas actives (+ always-on coherence/feasibility) |
|---|---|---|
| `2026-08-22-calibration-degraded-mode-plan.md` | `plan` (legacy) | adversarial |
| `2026-08-22-plan-b-calibration-brainstorm-plan.md` | `unified-requirements` | product, scope-guardian, adversarial |
| `2026-08-22-plan-b-calibration-implementation-plan.md` | `unified-plan` | *(aucune conditionnelle — dérive d'un Product Contract validé, hors périmètre high-stakes)* |
| `2026-08-23-critique-complete-plan.md` | `plan` (méta/orchestration) | product, scope-guardian, adversarial |
| `2026-08-23-github-api-integration-plan.md` | `plan` | product, security, scope-guardian, adversarial |

---

## 🔴 CRITIQUE — Contradiction cross-document (coherence + feasibility)

**`calibration-degraded-mode-plan.md` (S1-S5) contredit `plan-b-calibration-implementation-plan.md` (IU1-IU6) sur la même feature.**

- Les deux docs datent du 22/08 et couvrent le même objectif (Plan B calibration dégradé), mais :
  - Le plan IU dit explicitement : *"IU1 (SCORING_DEFAULTS) — PRIORITÉ, tout dépend de là"*.
  - Le plan S1-S5 ne mentionne **jamais** SCORING_DEFAULTS ni l'extraction des constantes — il traite `calibrate_degraded.py`/`apply_calibration_fix.py` comme de simples scripts à créer en squelette (S1), sans dépendance à un refactor préalable de `scoring.py`.
- Le doc S1-S5 a `status: in-progress` en frontmatter ; le doc IU a `status: confirmed` + `artifact_readiness: implementation-ready`. Lequel fait foi ?
- **Hypothèse la plus probable** : `calibration-degraded-mode-plan.md` est un brouillon antérieur, supplanté par la paire unifiée (`plan-b-calibration-brainstorm-plan.md` + `plan-b-calibration-implementation-plan.md`) produite le même jour. Non archivé/marqué obsolète.

**Recommandation :** soit archiver/supprimer `calibration-degraded-mode-plan.md` (déplacer vers un dossier `archive/` ou ajouter `status: superseded`), soit fusionner ses éléments utiles (ex. `release_hackathon.sh` details) dans le plan IU si non couverts. **Décision requise avant toute exécution du Plan B** — risque réel de suivre le mauvais ordre d'étapes.

---

## 🟠 IMPORTANT

### `plan-b-calibration-brainstorm-plan.md` (unified-requirements)

1. **Feasibility (R6)** — `apply_calibration_fix.py` patche `SCORING_DEFAULTS` **directement dans le code source** `scoring.py`. Aucune mention de sauvegarde/backup ni de validation post-patch (parse + tests) avant que `--apply` ne soit considéré réussi. Risque : source corrompu silencieusement en pleine semaine de hackathon.
   **Suggestion :** ajouter à R6/R7 — backup automatique (`.bak` ou stash git) + `python -c "import ast; ast.parse(...)"` (ou relance ciblée des tests scoring) juste après patch, avant de déclarer succès.

2. **Adversarial (R9)** — `release_hackathon.sh` vérifie "CI verte" puis release. Aucun garde-fou si le check `gh run list` renvoie un état périmé/en cache, ou si la release doit être annulée après coup (pas de procédure de rollback documentée).
   **Suggestion :** documenter un chemin de rollback minimal (delete tag + release) même si non scripté.

3. **Coherence (positif)** — Bonne nouvelle : R1-R14 sont tous tracés vers IU1-IU6 dans le plan d'implémentation, aucune orphan requirement.

### `github-api-integration-plan.md`

1. **Security-lens** — Bonne pratique déjà présente (PAT via env, cascade `secrets.py` env>config>keyring>prompt, permissions `contents: read` minimales sur l'Action). Point de vigilance non couvert : aucune mention explicite de **ne jamais logger le token** (masquage dans les logs `httpx`/erreurs). À ajouter comme critère de test (P2.7).
2. **Scope-guardian** — La Phase 2 (8.5 jours, 8 IU, GraphQL complet, cache SQLite, keyring) est explicitement "HORS périmètre hackathon", mais représente la majorité du volume documentaire du plan. Sur un plan J-8, c'est un investissement de rédaction important pour du travail différé — cohérent avec le principe compound engineering (documenter une fois), mais à confirmer que ça n'a pas mordu sur le temps Phase 1 (H1-H3, seul livrable du 31/08).
3. **Feasibility** — P2.7 prévoit des tests d'intégration contre des repos publics réels (`github/github-docs`, `microsoft/vscode`). Fragile en CI : dépend de la disponibilité/contenu de repos externes non versionnés par vous → source de flakiness. Préférer des fixtures GraphQL enregistrées (cassettes/VCR) en plus des repos réels ponctuels.

### `critique-complete-plan.md` (méta-plan d'audit)

1. **Product-lens / Vigie bien-être** — Ce plan engage 5 sessions Claude Desktop (~2-3h) pour auditer un side-project hackathon à J-8 du 31/08. Les dossiers `2026_08_23_audit/`, `2026_08_24_audit/` (deep-dives) et `2026_08_24_critique_complete_synthese.md` existent déjà dans `aidd_docs/tasks/` — une bonne partie du plan (item 1, coché `[x]`, et item 2 marqué `[-]` en cours) semble déjà exécutée. Le doc n'a pas été mis à jour pour refléter cet avancement réel.
   **Suggestion :** rafraîchir les checkboxes selon l'état réel avant de lancer les sessions 3-5, pour éviter de re-dupliquer du travail déjà fait.
2. **Scope-guardian** — 11 activités de review distinctes (7 piliers + 6 personas CE + 4 agents deep-dive + doc-review) pour un repo hackathon. Écart notable avec le principe Business-First (acquisition prioritaire jusqu'à mi-2026 selon le pilotage business Goumies). Pas un blocage, mais mérite un arbitrage explicite : ce niveau d'exhaustivité sert-il le hackathon (jugement, démo) ou relève-t-il de la "perfectionnite documentaire" ?
3. **Adversarial** — Ce doc n'a pas de `product_contract_source` / `origin` (pas de Product Contract validé en amont) — sa prémisse (faut-il vraiment 5 sessions ?) n'a pas été challengée avant rédaction.

---

## 🟡 MINEUR / FYI

- `calibration-degraded-mode-plan.md` : aucun ID de risque, pas de section Risks — contraste avec `plan-b-calibration-implementation-plan.md` qui en a une. Cohérence de format à uniformiser si le doc est conservé.
- `github-api-integration-plan.md` : Questions Ouvertes (GitHub App vs PAT, GraphQL/REST hybride, multi-utilisateurs, webhooks) sont pertinentes mais toutes reportées à "validation finale Phase 2" — aucune ne bloque le hackathon, classement correct.
- Terminologie : "Plan B" utilisé dans 3 docs différents sans lexique commun définissant ce que "Plan A" était — un lecteur externe (jury hackathon ?) n'a pas ce contexte. FYI seulement si ces docs sortent du cercle interne.

---

## Synthèse — Top 3 actions avant exécution

1. **Trancher le conflit `calibration-degraded-mode-plan.md` vs `plan-b-calibration-implementation-plan.md`** — lequel exécuter (S1-S5 ou IU1-IU6) ? Recommandation : IU1-IU6 (plus complet, Product Contract tracé), archiver l'autre.
2. **Ajouter backup + validation post-patch à R6/R7** (apply_calibration_fix.py) avant tout `--apply` réel sur `scoring.py`.
3. **Rafraîchir `critique-complete-plan.md`** avec l'état réel (audits déjà livrés) et trancher explicitement le niveau d'exhaustivité restant vs le J-8.

---

*Review condensée — personas simulées en un passage unique pour économie de tokens, pas de dispatch multi-agents (indisponible hors Claude Code/Task tool). Pas de fix auto-appliqué : validation humaine requise avant toute modification de fichier, conformément au protocole Goumies (validation avant exécution).*
