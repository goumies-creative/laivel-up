# Deep Dive Testing — LAIVEL UP

**Date** : 2026-08-24
**Méthode** : persona *Testing Reviewer* appliquée manuellement — lecture de 24 fichiers de test (344 tests, 4221 lignes) + 7 fichiers source (1903 lignes, 61 symboles).
**Angle** : pas "est-ce que les tests passent", mais "quels chemins critiques ne sont pas testés, quels tests sont fragiles, et où le faux positif menace".

## 0. Vue d'ensemble

| Métrique | Valeur |
|----------|--------|
| Fichiers de test | 24 (+ 4 conftest/fixtures) |
| Tests totaux | 344 |
| Lignes de test | 4 221 |
| Lignes de source | 1 903 |
| Ratio test/source | 2.2:1 |
| Symboles source | 61 (35 publics, 18 privés, 7 classes) |

**Couverture déclarée** : scoring.py = 100% (non-négociable), autres modules ≥ 80%.
**CI** : matrix 3 OS × 3 Python (9 combinaisons), + bandit + pip-audit.

## 1. Findings

| # | Sev | Catégorie | Location | Constat | Effort |
|---|-----|-----------|----------|---------|--------|
| 1 | 🔴 P0 | Missing test | `encoding.py` | 4/6 fonctions `# pragma: no cover` — aucun test unitaire pour `supports_utf8`, `ascii_fallback`, `ensure_utf8_env`, `make_console` | M |
| 2 | 🟡 P2 | Brittle test | `test_snapshots.py` | Snapshots basés sur le texte exact — tout changement de wording casse les tests sans bug réel | S |
| 3 | 🟡 P2 | Missing edge case | `scoring.py::intervention_max` | Pas de test pour `retries_triangulated=True` avec `retries_after_fact=None` (chemin "données manquantes") | XS |
| 4 | 🟡 P2 | Missing edge case | `scoring.py::harness_max` | Pas de test pour `agent_rules_versioned=True` sans `context_versioned` (chemin "rules sans contexte") | XS |
| 5 | 🟢 P3 | False confidence | `test_team.py` | Tests export vérifient `len(data["members"]) == 2` mais pas que les slugs sont bien pseudo-anonymes (SHA-256) | XS |
| 6 | 🟢 P3 | Mirror test absent | `test_report.py` | Pas de test qui vérifie que `render_markdown` et `render_html` produisent le même contenu informationnel (même verdict = mêmes infos) | S |
| 7 | 🟢 P3 | Untested branch | `cli.py::_load_profile` | Le branch `except KeyError` (clé manquante dans le JSON) n'est pas testé explicitement | XS |
| 8 | 🟢 P3 | Untested branch | `team.py::export_markdown` | Le branch `history vide` (pas d'historique) n'est pas testé explicitement | XS |

---

### #1 — encoding.py : 4/6 fonctions sans test unitaire (P0)

`encoding.py` contient 6 fonctions, 4 portent `# pragma: no cover` :
- `_enable_virtual_terminal_windows` — Windows-only, ctypes
- `_try_reconfigure_stdout` — reconfigure stdout
- `ensure_utf8_env` — force UTF-8
- `make_console` — crée Rich Console

**Problème** : ces fonctions sont appelées au démarrage de la CLI (`cli.py` L1-5) mais jamais testées isolément. Si `ensure_utf8_env` plante sur un OS spécifique, le test `test_install_clean` le détecte (install + `--help`), mais pas les tests unitaires.

**Correctif** : ajouter des tests unitaires pour `supports_utf8` (mock `sys.stdout.encoding`), `ascii_fallback` (test avec emojis), et un test d'intégration qui vérifie que `make_console` retourne un `Console` valide.

### #2 — Snapshots fragiles (P2)

`test_snapshots.py` (10 tests) compare les sorties CLI texte exactes. Tout changement de wording (correction faute, reformulation) casse les snapshots sans bug réel.

**Impact** : maintenance élevée — chaque changement de message nécessite un `--snapshot-update`.

**Correctif** : compléter les snapshots par des tests de contenu (vérifier la présence de clés `["Niveau", "Taille", "Harness"]` dans la sortie) plutôt que de se fier uniquement à la correspondance exacte.

### #3 — intervention_max : chemin "retries_triangulated sans ratio" non testé (P2)

`intervention_max` (L209-235) a un chemin où `retries_triangulated=True` mais `retries_after_fact=None` :
```python
if traces.get("retries_triangulated") and ratio is not None:
    # triangulé + ratio = confiance haute
elif ratio is not None:
    # non triangulé + ratio = confiance basse
else:
    # pas de ratio = refus
```

Le premier `elif` et le `else` sont testés, mais le cas `triangulated=True` + `ratio=None` ne l'est pas.

**Correctif** : un test avec `retries_triangulated=True` et `retries_after_fact` absent.

### #4 — harness_max : chemin "rules sans contexte" non testé (P2)

`harness_max` (L188-206) évalue `context_versioned` puis `agent_rules_versioned` de façon cumulative. Le cas `agent_rules_versioned=True` + `context_versioned=False` n'est pas explicitement testé — le score devrait rester à Red (pas de contexte = pas de rules).

**Correctif** : un test avec `context_versioned=False, agent_rules_versioned=True` qui vérifie que le niveau reste Red.

### #5 — Tests export sans vérification pseudo-anonyme (P3)

`test_team.py::TestExport` vérifie le contenu exporté (noms, nombre de membres) mais ne vérifie pas que les slugs dans l'export sont bien des slugs SHA-256 (pas les noms en clair).

**Correctif** : dans `test_export_json`, vérifier que `data["members"][key]["name"]` contient un slug (format `xxx-8chars`), pas un nom en clair.

### #6 — Pas de test miroir markdown↔html (P3)

`test_report.py` teste `render_markdown` et `render_html` séparément, mais jamais avec le même verdict pour vérifier qu'ils produisent le même contenu informationnel.

**Correctif** : un test qui vérifie que pour un verdict identique, les deux rendus contiennent les mêmes clés (`"Niveau"`, `"Taille"`, `"Transparence"`).

### #7 — _load_profile : branch KeyError non testé (P3)

`_load_profile` (L53-95) a un `except KeyError` pour les clés manquantes dans le JSON. Aucun test ne déclenche ce branch explicitement.

**Correctif** : un test avec un JSON qui a `"declared_level": "BLUE"` mais sans `"traces"`.

### #8 — export_markdown : branch "history vide" non testé (P3)

`export_markdown` (L261-302) a un branch qui gère l'absence d'historique. Aucun test ne vérifie ce cas.

**Correctif** : un test avec une équipe créée mais sans membre évalué (history vide).

## 2. Points positifs

- **344 tests** pour 1903 lignes de source — ratio 2.2:1, excellent.
- **Scoring 100%** — ADR-0009 respectée, tous les chemins de l'algorithme central sont testés.
- **Security tests complets** — 22 tests dans `tests/security/` couvrant injection, path traversal, DoS, HMAC, bandit.
- **RGPD tests complets** — 19 tests dans `test_team_rgpd.py` couvrant slug, opt-out, exports, droit à l'oubli.
- **Property-based tests** — 13 tests hypothesis dans `test_properties.py` pour les invariantes fondamentaux.
- **Edge cases well covered** — `test_scoring_edge.py` (48 tests) couvre les cas limites du moteur.
- **CI matrix robuste** — 9 combinaisons OS × Python, + bandit + pip-audit.
- **conftest.py isolation** — fixture autouse `_isolate_team_dir` isole `.laivelup/` via `tmp_path`.

## 3. Recommandations

| Priorité | Action | Effort |
|----------|--------|--------|
| P0 | Ajouter tests unitaires `encoding.py` (supports_utf8, ascii_fallback) | M |
| P2 | Compléter snapshots par tests de contenu (clés attendues) | S |
| P2 | Test `intervention_max` avec triangulated=True + ratio=None | XS |
| P2 | Test `harness_max` avec rules=True + context=False | XS |
| P3 | Test export vérifie pseudo-anonyme (slugs, pas noms) | XS |
| P3 | Test miroir markdown↔html (même verdict = mêmes infos) | S |
| P3 | Test `_load_profile` avec KeyError (clé manquante) | XS |
| P3 | Test `export_markdown` avec history vide | XS |

**Total** : ~2h de travail pour 8 améliorations.

## 4. Verdict Testing

**Score** : 8.5/10 — couverture excellente sur le cœur métier (scoring 100%, security 22 tests, RGPD 19 tests). Les 8 findings sont des gaps mineurs sur les bords (encoding, edge cases, snapshots). Le ratio 2.2:1 est au-dessus de la moyenne pour un projet CLI.

---

*Généré par testing review — session 3 critique, 2026-08-24*
