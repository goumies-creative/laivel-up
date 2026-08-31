# CE Performance Review — goumies-creative-laivel-up

**Reviewer :** ce-performance-reviewer
**Date :** 2026-08-31
**Périmètre :** `src/laivelup/` (scoring, report, team tracker), `scripts/` (generate_profile, benchmarks), `tests/`
**Méthode :** analyse statique file:line + ordres de grandeur

---

## Verdict

**4 findings dont 2 CONFIRMÉS (AIDD report validé), 2 NOUVEAUX, 1 RÉFUTÉ.**

Le projet est un CLI/hackathon avec un scope modeste (4 profils officiels, ~50 users max). Les performance problems sont réelles mais le blast radius est limité. Aucun finding n'est P0 — le plus impactant est le cold-start CLI qui affecte chaque invocation.

| Severity | Count | Description |
|----------|-------|-------------|
| P1 | 1 | Cold-start CLI : imports lourds au chargement |
| P2 | 1 | Subprocess séquentiels dans generate_profile.py |
| P2 | 1 | Render HTML reconstruit le CSS inline à chaque appel |
| P3 | 1 | ascii_fallback() inutile quand UTF-8 natif |

---

## Findings

### F1 — Cold-start CLI : imports eager de dépendances lourdes (CONFIRMÉ)

**File:** `src/laivelup/cli.py:26-60`
**Severité:** P1
**Confiance:** 85 (Anchor 75)

**Constat:** Au chargement de `cli.py`, 15+ modules sont importés en bloc :
- `typer` (lourd)
- `rich.console`, `rich.prompt`, `rich.table`
- `calibrate_dashboard` (génération HTML inline)
- `team` (12 fonctions importées une par une)
- `schema`, `report`, `scoring`, `model`, `encoding`, `questions`

La commande `calibrate_cmd` (ligne 846) fait un `from .calibrate_core import run_calibration` lazy, mais le reste est eager. Chaque `laivelup --help` ou `laivelup evaluate` paye le coût complet.

**Impact:** ~200-400ms de cold-start perçu sur CLI. Acceptable pour un hackathon, gênant si intégré en CI (benchmark.py lance N subprocess = N cold-starts).

**Recommandation:** Lazy imports pour `rich`, `typer`, `calibrate_dashboard`, `team` — ne charger que dans les branches qui les utilisent.

---

### F2 — generate_profile.py : 4 subprocess git séquentiels (CONFIRMÉ, corrigé vs AIDD)

**File:** `scripts/generate_profile.py:36-208`
**Severité:** P2
**Confiance:** 75 (Anchor 75)

**Constat:** L'AIDD report disait "7 subprocess séquentiels". Comptage réel via `_git()` :

1. `_detect_pr_sizes` → 1 appel `git log --merges --shortstat` (ligne 38-51)
2. `_detect_retries_after_fact` → 1 appel `git log --format=%H %s` (ligne 143-155)
3. `_detect_parallel_projects` → 2 appels `git branch` (lignes 181-195)

Total : **4 subprocess, tous séquentiels**, chacun avec `timeout=30`.

`_detect_context_versioned`, `_detect_agent_rules_versioned`, `_detect_retry_loops`, `_detect_agents_autonomous`, `_detect_prompts` sont des lectures fichier (pas subprocess) — ils ne comptent pas.

**Impact:** ~4-12s pour un repo moyen (1s/subprocess en moyenne). Le 2e et 3e git log sont indépendants du 1er. Les 2 git branch sont indépendants du reste.

**Recommandation:** Regrouper les 4 appels en 1-2 batchs via `subprocess.Popen` avec pipes, ou exécuter les 2 premiers en parallèle (ils lisent le même git log avec des filtres différents).

---

### F3 — render_html() reconstruit le CSS inline à chaque appel (NOUVEAU)

**File:** `src/laivelup/report.py:489-996`
**Severité:** P2
**Confiance:** 60 (Anchor 50)

**Constat:** `render_html()` retourne un f-string de ~500 lignes contenant tout le CSS (~400 lignes de styles). Ce CSS est **identique** à chaque appel — seul le contenu dynamique (verdict, badges, tables) change. La même structure existe dans `calibrate_dashboard.py:115-321`.

En l'état, `report.py` est appelé 1x par `evaluate` (CLI) ou 0x (mode JSON). Le coût est donc négligeable dans le flow actuel. Mais si le rapport était généré en boucle (batch evaluation, dashboard refresh), le CSS serait reconstruit à chaque fois.

**Impact:** ~1-2ms de plus par rapport (concaténation de ~15KB de CSS). Négligeable pour 1 appel, visible à 1000+.

**Recommandation:** Extraire le CSS dans une constante `REPORT_CSS` au niveau module, ou utiliser `string.Template`. Low priority vu le scope actuel.

---

### F4 — ascii_fallback() inutile sur systèmes UTF-8 natifs (NOUVEAU)

**File:** `src/laivelup/encoding.py:64-96`
**Severité:** P3
**Confiance:** 50 (Anchor 25 — suppress)

**Constat:** `ascii_fallback()` itère sur 18 remplacements de caractères via `str.replace()` dans une boucle. Elle est appelée potentiellement à chaque affichage. Sur Linux/macOS (UTF-8 natif), `supports_utf8()` retourne `True` et la fonction retourne le texte inchangé — mais elle fait quand même l'appel et la vérification.

**Impact:** Microscopique (~1µs par appel). Strictement > Anchor 25.

**Recommandation:** **SUPPRIMER** ce finding. L'optimisation ne vaut pas le coût de lecture du code. La fonction est bien conçue (guard clause en haut).

---

## RÉFUTÉ — N+1 dans test_team_rgpd.py (AIDD report)

**File:** `tests/test_team_rgpd.py`
**Statut:** RÉFUTÉ

L'AIDD report signalait un "N+1 test_team_rgpd.py". Après analyse :
- Chaque test crée sa propre équipe via `create_team()` (isolation de test standard)
- `evaluate_member()` est appelé 1-2x par test, pas dans une boucle
- Le `sys.path.insert` dans chaque méthode est un code smell (duplicé 6x) mais n'est PAS un problème de performance — c'est un problème de DRY/maintenance
- Le `team_with_data` fixture (ligne 173) évalue 2 membres — O(1), pas N+1

**Verdict :** Le pattern est "test isolation standard", pas N+1. Le `sys.path.insert` duplicé est un finding de code quality, pas de performance.

---

## Hot paths analysés

| Hot path | File:Line | Complexité | Status |
|----------|-----------|------------|--------|
| `evaluate()` | scoring.py:369 | O(1) — 4 scorers + min() | OK |
| `normalize_profile()` | scoring.py:76 | O(n) sur keys traces (~10 keys max) | OK |
| `size_max()` | scoring.py:162 | O(n) sur pr_sizes (≤50 items) | OK |
| `_dominant()` | scoring.py:142 | O(n) Counter sur ≤50 items | OK |
| `render_html()` | report.py:433 | O(1) — f-string statique | OK (F3 note) |
| `evaluate_member()` | team.py:174 | O(1) — 1 evaluate + snapshot | OK |
| `_git()` | generate_profile.py:23 | O(1) — 1 subprocess, timeout=30 | OK |
| `_parse_retry_ratio()` | cli.py:883 | O(1) — 3 regex, interview only | OK |

Aucun hot path n'a de complexité > O(n) avec n significatif. Le scoring tourne sur des listes de ≤50 PR sizes et des dicts de ~10 keys.

---

## Couverture

| Catégorie | Couverte ? | Notes |
|-----------|------------|-------|
| N+1 queries | ✅ | Aucun — pas de BDD, subprocess 1x par fonction |
| Unbounded memory | ✅ | team.history capé à 100, history display à 20 |
| Missing pagination | ✅ | Aucun endpoint qui retourne tout |
| Hot-path allocations | ✅ | Pas de regex compilée en boucle, pas d'objet créé inutilement |
| Blocking I/O async | ⚠️ | Pas de code async dans le projet — tous les I/O sont sync (acceptable pour CLI) |
| Subprocess timeout | ✅ | Tous les subprocess ont `timeout=30` |
| Mémoïsation | ✅ | Pas de calcul pur coûteux qui le nécessiterait |
| Cold-start lazy imports | ❌ | F1 — eager imports dans cli.py |

---

## Message final

**Verdict : PROPRE — 2 confirmations AIDD, 1 réfutation, 2 nouveaux findings low-severity.**

| Metric | Value |
|--------|-------|
| Findings total | 4 |
| Confirmés (AIDD) | 2 (F1 cold-start, F2 subprocess) |
| Nouveaux | 2 (F3 CSS rebuild, F4 ascii_fallback — ce dernier à supprimer) |
| Réfutés | 1 (N+1 test_team_rgpd) |
| P0 | 0 |
| P1 | 1 (cold-start CLI) |
| P2 | 2 (subprocess, CSS rebuild) |
| P3 | 1 (suppress) |

**Top 3 :**
1. **F1 — Cold-start CLI** : imports eager de typer+rich+team au chargement. Lazy imports = -200ms perçu.
2. **F2 — Subprocess séquentiels** : 4 appels git indépendants lancés en série dans generate_profile.py. Parallelisable.
3. **F3 — CSS inline rebuild** : render_html() reconstruit ~15KB de CSS statique à chaque appel. Extraire en constante.
