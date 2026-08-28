# Architecture Audit — LAIVEL UP

**Date** : 2026-08-28
**Scope** : `src/laivelup/` (11 modules, 2118 LOC), `pyproject.toml`, 4 CI workflows, `docs/architecture.mmd`, `docs/adr/` (16 ADRs), `scripts/` (8 Python + 2 shell)
**Method** : read-only static analysis — import graph, module responsibilities, coupling, layering, ADR conformance, diagram accuracy. Cross-referenced with prior audits (23/08 architecture.md, 24/08 architecture-deep-dive.md).

## Dependency Graph (verified)

```
model.py          ← stdlib only (dataclasses, enum) — domain root
utils.py          ← stdlib only (hashlib, hmac, os)
questions.py      ← no internal deps
scoring_defaults.py ← model
schema.py         ← stdlib + jsonschema (optional)
scoring.py        ← model, questions, scoring_defaults
report.py         ← model, utils
team.py           ← model, scoring, utils
cli.py            ← model, report, schema, scoring, team, questions (orchestrator)
encoding.py       ← stdlib only (os, sys) — unused by other modules
__init__.py       ← scoring_defaults
```

**Cycles** : none. **Direction** : CLI → core → model (no reverse deps). Clean layered architecture.

---

## Findings

| Sev | Category | Location | Issue | Suggested fix | Effort |
|-----|----------|----------|-------|---------------|--------|
| 🟡 | dead code / coupling | `src/laivelup/encoding.py` (entier) | Module inutilisé : 0 imports internes. `cli.py` réinvente `_make_console()`/`NO_COLOR`/`TTY` (lignes 56-71) au lieu d'utiliser `encoding.make_console()`. Les fonctions `ensure_utf8_env()`, `ascii_fallback()`, `supports_utf8()` ne sont appelées nulle part dans `src/`. Double implémentation du même souci (encodage cross-platform) sans partage. | Supprimer `encoding.py` OU l'intégrer dans `cli.py` (une seule source de vérité pour l'encodage). Si conservation, documenter l'usage dans une ADR. | S |
| 🟡 | module size / SRP | `src/laivelup/cli.py:1-623` | 623 lignes, 10+ responsabilités : parsing CLI, validation profil, affichage verdict, merge réponses entretien, regex retry ratio, 5 commandes team, schema command, JSON output, fail-on logic. Comparé à `model.py` (112L) et `scoring.py` (429L), le CLI absorbe de la logique métier qui devrait rester dans le domaine. | Extraire `_merge_answer()` + `_parse_retry_ratio()` + `_LEVELS_BY_KEYWORD` dans un module `interrogate.py` (logique d'entretien). Extraire `COMMAND_SCHEMA` dans `schema.py` ou un module dédié. Garder `cli.py` comme pure orchestration Typer. | M |
| 🟡 | coupling | `src/laivelup/scoring.py:42-47` | 6 alias backward-compatible (`CONFIDENCE_THRESHOLD`, `RETRIES_PER_LEVEL`, etc.) créés par lecture de `SCORING_DEFAULTS` avec `# type: ignore[assignment]`. Couplage étroit : si `scoring_defaults.py` change une clé, `scoring.py` casse silencieusement au runtime (pas au typecheck). Les `type: ignore` masquent le problème. | Soit utiliser `SCORING_DEFAULTS['CONFIDENCE_THRESHOLD']` directement dans le code (supprimer les alias), soit typer `SCORING_DEFAULTS` avec un `TypedDict` pour que mypy vérifie les clés. | S |
| 🟢 | documentation | `docs/architecture.mmd` vs `scripts/` | Diagramme complet depuis le deep dive du 24/08 (10 scripts listés). Mais 2 edges manquants : `GEN_PROFILE --> TEAM_MOD` (utilise `team.slug()` pour pseudo-anonymiser) et `CI_EVAL --> REPORT` (appelle `render_markdown()`). Le sous-graphe Scripts inclut les 10 fichiers réels. | Ajouter les 2 edges dans le diagramme Mermaid. | XS |
| 🟢 | ADR gap | `docs/adr/` (absent) | Aucune ADR pour la persistance du Team Tracker (`team.py:load_team/save_team`, `.laivelup/teams/`). Le deep dive du 24/08 notait déjà ce residual du 23/08. La décision existe dans le code (JSON local, zéro réseau, trim à 100 entrées) mais n'est pas actée dans `docs/adr/`. | Créer `docs/adr/0017-team-tracker-persistence-json-local.md`. | S |
| 🟢 | validation overlap | `src/laivelup/scoring.py:70-130` + `src/laivelup/schema.py:31-51` | Double validation du profil : `schema.validate_profile()` (JSON Schema, structural) + `scoring.normalize_profile()` (business rules, type coercion). Les deux vérifient `pr_sizes`, `retries_after_fact`, `parallel_projects` avec des logiques légèrement différentes. Pas de risque actuel (les deux sont appelés dans `cli.py:_load_profile`), mais divergence silencieuse possible si le schema évolue sans同步 normalize. | Documenter la séparation des responsabilités dans une note de code ou ADR. Idéalement, `normalize_profile` ne devrait vérifier que les règles métier non couvertes par le schema. | XS |
| 🟢 | import style | `src/laivelup/scoring.py:29` | `from .questions import QUESTION_IDS` importé en tête de module (correct). Noté comme "tardif" dans le deep dive du 24/08 (finding #5) — depuis corrigé. Plus de problème ici. | Aucun — resolved. | — |
| 🟢 | CLI separation | `cli.py` vs `scoring.py` | **Positif** : la CLI (`cli.py`) est bien séparée du business logic (`scoring.py`). Aucune logique de scoring n'est dans `cli.py`. `cli.py` orchestre : charge le profil, appelle `evaluate()`, affiche le résultat. Respect de la couche CLI → engine → model. | Aucun — conforme. | — |

---

## Top actions

1. **Intégrer ou supprimer `encoding.py`** — le module mort crée une confusion (deux implémentations de l'encodage cross-platform) sans apporter de valeur. Effort XS, impact clarificateur.
2. **Créer l'ADR-0017 pour la persistance Team** — la décision est déjà implémentée mais pas documentée, ce qui est un risque de dérive future. Effort S.
3. **Réduire `cli.py` en extrayant la logique entretien** — `_merge_answer` + `_parse_retry_ratio` + `_LEVELS_BY_KEYWORD` = ~80 lignes de logique métier dans le mauvais module. Effort M.
4. **Remplacer les alias `type: ignore` dans `scoring.py`** — soit `TypedDict` pour `SCORING_DEFAULTS`, soit utilisation directe du dict. Effort S.

---

## Coverage

- **Scanned** : `src/laivelup/*.py` (11 fichiers, intégralité), `pyproject.toml`, `.github/workflows/{ci,release,aidd-eval,pr-quality-gate}.yml`, `docs/architecture.mmd`, `docs/adr/0001-0016` (index), `scripts/ci_evaluate.py`, import graph complet.
- **Skipped** : `scripts/generate_profile.py` (analysé indirectement via `ci_evaluate.py`), `tests/` (hors périmètre architecture), exécution live (read-only).
- **Resolved since 23/08-24/08** : schema path (ADR-0011), team persistence, `verdict_to_dict()` canonique, `ci_evaluate.py` schema validation.
- **Remaining from 24/08** : ADR-0017 (team persistence) toujours en gap.
