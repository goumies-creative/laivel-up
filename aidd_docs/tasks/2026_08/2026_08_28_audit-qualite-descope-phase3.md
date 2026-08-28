---
type: audit
date: 2026-08-28
status: final
objectif: >
  Décision de descope Phase 3 (load-testing) + audit qualité codebase/architecture/configs
  mené le jour de réception du sujet officiel et des profils officiels du hackathon LAIVEL UP.
methode: >
  Consortium Goumies Creative (lecture croisée grille AIDD + personas Compound Engineering)
  via Filesystem MCP sur le dépôt local.
---

# Audit qualité + décision descope Phase 3 — LAIVEL UP (J0 profils officiels)

**Date** : 2026-08-28
**Contexte** : réception prévue du sujet officiel et des 4 profils officiels à 12h. Ce document tranche le trigger de descope Phase 3 resté en suspens depuis le 24/08, et documente un audit qualité frais (codebase, architecture, configs) mené avec les lentilles Compound Engineering pertinentes.

---

## 1. Décision — Descope Phase 3 (robustesse)

**Trigger binaire, vérifié le 29/08 à 18h :**

- [ ] `pytest tests/test_load.py -v` passe (1k profils + équipe 50 < 5s)
- [ ] `python scripts/benchmark.py` produit un artefact p50/p95 uploadé en CI

**Si les deux conditions ne sont PAS remplies à 29/08 18h → Phase 3 est descopée.**
Justification à citer dans le rendu : les 344 tests existants (dont 22 tests
sécurité, 19 tests RGPD, CI matrix 3 OS × 3 Python) constituent une preuve de
robustesse suffisante pour le critère jury « C'est solide », sans dépendre du
chantier load-testing.

**Si les deux conditions SONT remplies → Phase 3 reste au planning, mais
sans dépasser 30/08 10h (marge vidéo).**

> Remplace la ligne « Fix scoring si décalage — Itératif jusqu'à vert » de la section
> « Risques résiduels » de `2026_08_24_critique_complete_synthese.md`.

---

## 2. Audit codebase / architecture / configs — lentilles Compound Engineering + AIDD

**Personas mobilisées** (catalogue : `compound-engineering-plugin.git/node_modules/compound-engineering/skills/ce-code-review/references/persona-catalog.md`) — chemins exacts pour ré-exécution en terminal via `opencode`/Claude Code :

| Lentille | Fichier persona | Pourquoi retenue |
|---|---|---|
| `correctness` | `skills/ce-code-review/references/personas/correctness-reviewer.md` | Traçage d'exécution sur `scoring.py`, `team.py` |
| `architecture` | `skills/ce-plan/references/agents/architecture-strategist.md` | Couplage `scoring.py` ↔ `scoring_defaults.py`, flux de config |
| `code-quality` | `skills/ce-simplify-code/references/personas/code-quality-reviewer.md` | Shadowing, dead constants, wrappers |
| `project-standards` | `skills/ce-code-review/references/personas/project-standards-reviewer.md` | Recherche de `CLAUDE.md`/`AGENTS.md` — **absents du repo**, constat en soi |
| Maintainability/testing/security/performance | déjà exécutées le 24/08, non rejouées ici (pas de dérive détectée) | — |

Fichiers audités en direct : `model.py`, `scoring.py`, `scoring_defaults.py`, `utils.py`, `team.py`, `scripts/calibrate.py`, `scripts/apply_calibration_fix.py`, `pyproject.toml`, les 3 workflows CI.

---

### ✅ Finding critique — corrigé le 28/08 (était bloquant pour la calibration du jour)

**`scripts/apply_calibration_fix.py` (scenario A) — le patch de seuils échouait silencieusement**

- **Confiance : 100 (mécaniquement vérifiable, zéro interprétation)**
- Le script cherchait `f'"{key}": {old_val}'` — guillemets **doubles** — pour patcher `scoring_defaults.py`.
- Le fichier réel utilise des guillemets **simples** (`'CONFIDENCE_THRESHOLD': 0.5,`), imposés par `quote-style = "single"` dans `pyproject.toml`.
- `.replace()` sur une chaîne absente ne levait aucune erreur : il retournait la source **inchangée**, que le script réécrivait sur disque en rapportant `changes` comme si le patch avait réussi. Même défaut sur `RETRIES_PER_LEVEL.{sub_key}`.
- **Conséquence évitée** : lancer `python scripts/apply_calibration_fix.py --scenario A --thresholds expected.json --apply` aujourd'hui après calibration sur les profils officiels aurait annoncé un succès sans rien avoir changé.

**Vérification terminal :**
```bash
cd C:\Users\Romy\Desktop\GoumiesLand\GoumiesCreative-Agency\hackathons\goumies-creative-laivel-up
python scripts/apply_calibration_fix.py --scenario A --diagnostic diagnostic.json --thresholds expected.json --dry-run
grep -n "CONFIDENCE_THRESHOLD" src/laivelup/scoring_defaults.py
```

**Fix appliqué (2 lignes, confirmé en lecture sur disque le 28/08) :**
```python
# Dans apply_scenario_a(), les deux occurrences de .replace(...) :
current_source = current_source.replace(f"'{key}': {old_val}", f"'{key}': {new_val}")
current_source = current_source.replace(f"'{sub_key}': {old_val}", f"'{sub_key}': {new_val}")
```

**Statut : fix appliqué le 28/08** — les deux `.replace()` de `apply_scenario_a()` recherchent désormais `f"'{key}': {old_val}"` / `f"'{sub_key}': {old_val}"` (guillemets simples), alignés sur le style réel de `scoring_defaults.py`. Reste à faire avant usage réel : relancer un `--dry-run` avec un vrai `diagnostic.json` + `expected.json` issus des profils officiels pour confirmer que le diff annoncé correspond bien au contenu du fichier.

---

### 🟡 Findings architecture/config — importants, non bloquants

| # | Finding | Lentille | Confiance | Fichier:ligne |
|---|---|---|---|---|
| 2 | Double source de vérité : `scoring.py` fige les seuils `CONFIDENCE_*` en alias `float` à l'import (immuables) alors que `scoring_defaults.py` documente ces mêmes clés comme modifiables à chaud par les scripts Plan B. Fonctionne en pratique (CLI = process neuf à chaque appel), mais la validation post-patch ne recharge que `laivelup.scoring_defaults`, jamais `laivelup.scoring` — aucun test d'intégration n'appelle `evaluate()` après un patch pour confirmer que le moteur réagit correctement | architecture | 90 | `scoring.py:39-44` |
| 3 | `_MAX_TEAM_NAME_LEN = 64` défini mais jamais référencé — le seuil réel est un littéral `{1,64}` dupliqué dans la regex de `_validate_team_name`. Modifier la constante ne changerait rien | code-quality | 90 | `team.py:22` vs `team.py:29` |
| 4 | Paramètre `slug: str` qui masque l'import `from .utils import slug` dans `evaluate_member`, `remove_member`, `set_opt_out`, `export_csv`. Le wrapper `_slug()` (déjà signalé DRY le 24/08) n'est en réalité utile que dans `create_team`, qui n'a pas ce conflit de nom — renommer le paramètre en `member_slug` supprime le besoin du wrapper à la racine | code-quality | 75 | `team.py:167, 217, 234, 275` |

**Vérification terminal :**
```bash
ruff check src/laivelup/team.py --select F841,A002
grep -n "_MAX_TEAM_NAME_LEN" src/laivelup/team.py
```

---

### 🟢 Findings mineurs

| # | Finding | Lentille | Confiance |
|---|---|---|---|
| 5 | `size_max()` : deux chemins de refus voisins, deux logiques de niveau différentes — égalité parfaite → `SIZE_LEVEL[tied[-1]]` (dérivé grille) ; pic isolé dominant → `Level.BLUE` codé en dur, indépendant de la taille réelle | correctness | 60 |
| 6 | `SCORING_DEFAULTS: dict[str, object]` impose 6 `# type: ignore[assignment]` dans `scoring.py` — un `TypedDict` garderait la mutabilité « config Plan B » sans désactiver le typage | architecture | 60 |
| 7 | Pas de `CLAUDE.md`/`AGENTS.md` à la racine du repo — `METHODE.md`/`QUALITY.md`/`CONTRIBUTING.md` compensent en partie, mais aucun point d'entrée unique pour un agent IA qui clonerait le dépôt (pertinent pour le critère « reusability ») | project-standards | informational |

---

**Commandes de vérification groupées (terminal, depuis la racine du projet) :**
```bash
ruff check src/ tests/ && mypy src/ && bandit -r src/ -c pyproject.toml
grep -rn "type: ignore" src/laivelup/scoring.py
grep -n "_slug\b" src/laivelup/team.py
```

---

## 3. Prochaine étape

Fix du finding #1 appliqué. Reste : relancer `apply_calibration_fix.py --scenario A --dry-run`
avec les vrais `diagnostic.json`/`expected.json` issus des profils officiels dès leur réception,
pour confirmer que le patch matche désormais correctement le fichier source.

*Audit consortium — 2026-08-28, jour J du sujet officiel.*
