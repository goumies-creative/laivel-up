# Plan Critique Complète — Goumies Creative LAIVEL UP

> **Date** : 2026-08-23
> **Mode** : Plan (read-only) — à exécuter via Claude Desktop (comptes gratuits)
> **Projet** : `C:\Users\Romy\Desktop\GoumiesLand\GoumiesCreative-Agency\hackathons\goumies-creative-laivel-up`

---

## [x] 1. Audit Global — 7 Piliers AIDD

| # | Skill | Type | Emplacement Local | Sortie |
|---|-------|------|-------------------|--------|
| 1 | `aidd-dev-04-audit` | **Skill AIDD** | `C:\Users\Romy\.config\opencode\skills\aidd-dev-04-audit\` | `aidd_docs/tasks/2026_08/2026_08_XX_audit/report.md` + 7 `<pillar>.md` |

**Piliers couverts** : code-quality, architecture, security, dependencies, performance, tests, UI

**Lancement** :
```bash
# Dans Claude Desktop (projet ouvert)
/aidd-dev-04-audit
# → Choisir "all seven pillars"
```

---

## 2. Code Review Multi-Persona — Compound Engineering

| # | Skill | Type | Emplacement Local | Personas Sélectionnées (auto) |
|---|-------|------|-------------------|-------------------------------|
| 2 | `ce-code-review` | **Skill CE** | `C:\Users\Romy\.cache\opencode\packages\compound-engineering@git+https_\github.com\EveryInc\compound-engineering-plugin.git\node_modules\compound-engineering\skills\ce-code-review\` | **Toujours (6)** : `correctness-reviewer`, `testing-reviewer`, `maintainability-reviewer`, `project-standards-reviewer`, `agent-native-reviewer`, `learnings-researcher`<br>**Conditionnels (5)** : `security-reviewer`, `performance-reviewer`, `api-contract-reviewer`, `adversarial-reviewer`, `reliability-reviewer` |

**Pourquoi ces conditionnels ?**
- `security` : CLI public + `generate_profile.py` (git log parsing)
- `performance` : Load tests 1k profils < 5s
- `api-contract` : Typer CLI = API publique
- `adversarial` : 143+ tests, CI gates, mécanisme silent-pass
- `reliability` : Retries, timeouts, error handling

**Lancement** :
```bash
# Dans Claude Desktop
/ce-code-review depth:full grouping:always
# Sortie : /tmp/compound-engineering/ce-code-review/<run-id>/
```

---

## 3. Deep Dives Spécialisés — Agents CE (sessions séparées)

| # | Agent | Type | Emplacement Local | Focus |
|---|-------|------|-------------------|-------|
| 3a | `ce-security-sentinel` | **Agent CE** | `C:\Users\Romy\.cache\opencode\packages\compound-engineering@git+https_\github.com\EveryInc\compound-engineering-plugin.git\node_modules\compound-engineering\skills\ce-security-sentinel\` | Audit OWASP, secrets, input validation, auth |
| 3b | `ce-adversarial-reviewer` | **Agent CE** | `C:\Users\Romy\.cache\opencode\packages\compound-engineering@git+https_\github.com\EveryInc\compound-engineering-plugin.git\node_modules\compound-engineering\skills\ce-adversarial-reviewer\` | Scénarios d'attaque, failure modes |
| 3c | `ce-performance-oracle` | **Agent CE** | `C:\Users\Romy\.cache\opencode\packages\compound-engineering@git+https_\github.com\EveryInc\compound-engineering-plugin.git\node_modules\compound-engineering\skills\ce-performance-oracle\` | Bottlenecks, complexité, load tests |
| 3d | `ce-architecture-strategist` | **Agent CE** | `C:\Users\Romy\.cache\opencode\packages\compound-engineering@git+https_\github.com\EveryInc\compound-engineering-plugin.git\node_modules\compound-engineering\skills\ce-architecture-strategist\` | C4, ADRs, pattern compliance |
| 3e | `ce-maintainability-reviewer` | **Agent CE** | `C:\Users\Romy\.cache\opencode\packages\compound-engineering@git+https_\github.com\EveryInc\compound-engineering-plugin.git\node_modules\compound-engineering\skills\ce-maintainability-reviewer\` | Couplage, dead code, abstractions |
| 3f | `ce-testing-reviewer` | **Agent CE** | `C:\Users\Romy\.cache\opencode\packages\compound-engineering@git+https_\github.com\EveryInc\compound-engineering-plugin.git\node_modules\compound-engineering\skills\ce-testing-reviewer\` | Coverage gaps, brittle tests |

**Lancement** (chacun dans session Claude Desktop séparée) :
```bash
# Spawner directement l'agent via le skill CE
# Exemple pour security-sentinel :
# Task agent avec prompt : "Audit sécurité complet du projet goumies-creative-laivel-up"
```

---

## 4. Documentation & Architecture Review

| # | Skill/Agent | Type | Emplacement Local | Focus |
|---|-------------|------|-------------------|-------|
| 4a | `ce-doc-review` | **Skill CE** | `C:\Users\Romy\.cache\opencode\packages\compound-engineering@git+https_\github.com\EveryInc\compound-engineering-plugin.git\node_modules\compound-engineering\skills\ce-doc-review\` | Spawn 7 reviewers doc (coherence, design, feasibility, product, security, scope, adversarial-doc) |
| 4b | `ce-coherence-reviewer` | **Agent CE** | `C:\Users\Romy\.cache\opencode\packages\compound-engineering@git+https_\github.com\EveryInc\compound-engineering-plugin.git\node_modules\compound-engineering\skills\ce-coherence-reviewer\` | Contradictions, terminology drift |
| 4c | `ce-product-lens-reviewer` | **Agent CE** | `C:\Users\Romy\.cache\opencode\packages\compound-engineering@git+https_\github.com\EveryInc\compound-engineering-plugin.git\node_modules\compound-engineering\skills\ce-product-lens-reviewer\` | Goal-work misalignment, opportunity cost |

**Docs à reviewer** : `spec.md`, `plan.md`, `METHODE.md`, `architecture.mmd`, `AI_ACT_CONFORMITY.md`, `AI_ACT_RISK_MANAGEMENT.md`, `RGPD_REGISTER.md`

**Lancement** :
```bash
# Dans Claude Desktop
/ce-doc-review
```

---

## 5. Synthèse & Plan d'Action

| # | Activité | Type | Emplacement | Livrable |
|---|----------|------|-------------|----------|
| 5 | Consolidation rapports | Manuel (Claude Desktop) | N/A | `CRITIQUE_CONSOLIDEE_2026_08_23.md` |

**Contenu du livrable final** :
- Top 5 fixes critiques (P0/P1) — security, correctness
- Top 5 améliorations architecture/performance (P1/P2)
- Dette technique priorisée — tests, docs, maintainability
- Gaps conformité RGPD/AI Act
- Plan d'action pré-hackathon (J-8 à J-0)

---

## Arborescence des Sorties Attendues

```
aidd_docs/tasks/2026_08/
├── 2026_08_XX_audit/
│   ├── report.md              # Audit merged 7 piliers
│   ├── code-quality.md
│   ├── architecture.md
│   ├── security.md
│   ├── dependencies.md
│   ├── performance.md
│   ├── tests.md
│   └── ui.md
├── 2026_08_XX_ce-code-review/
│   └── <run-id>/
│       ├── correctness-reviewer.json
│       ├── testing-reviewer.json
│       ├── maintainability-reviewer.json
│       ├── project-standards-reviewer.json
│       ├── agent-native-reviewer.json
│       ├── learnings-researcher.json
│       ├── security-reviewer.json
│       ├── performance-reviewer.json
│       ├── api-contract-reviewer.json
│       ├── adversarial-reviewer.json
│       ├── reliability-reviewer.json
│       └── review-report.md
├── 2026_08_XX_security-sentinel/
│   └── security-report.md
├── 2026_08_XX_adversarial/
│   └── adversarial-report.md
├── 2026_08_XX_performance/
│   └── performance-report.md
├── 2026_08_XX_doc-review/
│   └── doc-review-report.md
└── CRITIQUE_CONSOLIDEE_2026_08_23.md
```

---

## Exécution Recommandée (5 Sessions Claude Desktop)

| Session | Durée estimée | Contenu |
|---------|---------------|---------|
| **1** | 30-45 min | `aidd-dev-04-audit` all seven pillars |
| **2** | 20-30 min | `ce-code-review depth:full grouping:always` |
| **3** | 3×15 min | 3 agents parallèles : security-sentinel, adversarial-reviewer, performance-oracle |
| **4** | 20 min | `ce-doc-review` + architecture-strategist sur `architecture.mmd` |
| **5** | 30 min | Synthèse + `CRITIQUE_CONSOLIDEE_2026_08_23.md` |

---

## Raisonnement — Pourquoi Claude Desktop (Comptes Gratuits)

| Critère | Claude Desktop | OpenCode + DeepSeek |
|---------|----------------|---------------------|
| Contexte long (docs + code + tests) | ✅ 200K tokens | ❌ Contexte rot prouvé |
| Multi-sessions parallèles | ✅ Onglets isolés | ❌ Session unique |
| Coût | Gratuit (quota journalier) | Payant (DeepSeek) |
| Qualité review doc didactique | ✅ Supérieure | ❌ Plantages mémoire |
| Skills CE/AIDD | Via prompts manuels | ✅ Natif |

> **Règle AGENTS.md** : "Contenu didactique/pédagogique → préférer Claude Desktop à OpenCode + DeepSeek"

---

## Questions de Validation (HITL)

1. **Ordre d'exécution** : Audit global → CE review → Deep dives → Doc review → Synthèse (validé ?)
2. **Scope** : Tout le repo (`src/`, `tests/`, `scripts/`, `docs/`, `schemas/`) ou focus `src/laivelup/` + `tests/` ?
3. **Priorité hackathon** : Focus P0/P1 (security, correctness, calibration 28/08) ou revue exhaustive P2/P3 incluse ?
4. **Accès Claude Desktop** : Compte(s) disponible(s) pour 4-5 sessions, ou préparation prompts à copier-coller ?

---

## Commandes de Vérification Pré-Session

```bash
# Vérifier que les skills sont installés
ls ~/.config/opencode/skills/aidd-dev-04-audit/
ls ~/.config/opencode/skills/aidd-dev-05-review/
ls ~/.cache/opencode/packages/compound-engineering@git+https_github.com_EveryInc_compound-engineering-plugin.git/node_modules/compound-engineering/skills/ce-code-review/
ls ~/.cache/opencode/packages/compound-engineering@git+https_github.com_EveryInc_compound-engineering-plugin.git/node_modules/compound-engineering/skills/ce-security-sentinel/
ls ~/.cache/opencode/packages/compound-engineering@git+https_github.com_EveryInc_compound-engineering-plugin.git/node_modules/compound-engineering/skills/ce-adversarial-reviewer/
ls ~/.cache/opencode/packages/compound-engineering@git+https_github.com_EveryInc_compound-engineering-plugin.git/node_modules/compound-engineering/skills/ce-doc-review/

# Vérifier le projet
cd C:\Users\Romy\Desktop\GoumiesLand\GoumiesCreative-Agency\hackathons\goumies-creative-laivel-up
git status --short
python -m pytest tests/ -q --no-cov | tail -5
```