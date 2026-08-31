# CE Architecture Review — LAIVEL UP

**Persona** : ce-architecture-strategist  
**Date** : 2026-08-31  
**Scope** : `src/laivelup/`, `scripts/`, `tests/`, `docs/adr/` (0001-0017), `docs/architecture.mmd`, `pyproject.toml`, `.github/workflows/`  
**Framework** : Goumies Creative Quality Framework

---

## Verdict

**CONDITIONAL PASS** — l'architecture est saine dans sa conception globale (pas d'imports circulaires, frontières CLI↔domaine claires, ADRs cohérents), mais trois findings bloquent un PASS propre : deux modules au-delà du seuil 500l et un diagramme d'architecture périmé. L'implémentation ADR-0017 (bonus axis) est cohérente avec le statut « à venir » de l'ADR.

---

## Findings

### F1 — `cli.py` dépasse 500 lignes (985l) — SEVERITY: HIGH

**File:line** : `src/laivelup/cli.py:1-985`  
**Criterion** : modules < 500l  
**ADR ref** : ADR-0015 (CLI Typer+Rich), ADR-0004 (grille 4 axes)

Le module `cli.py` est le point d'entrée CLI (Typer app) et agit comme orchestrateur de toute la couche applicative. À 985 lignes, il dépasse le seuil de 500l de la critère. Il contient :
- La définition de l'app Typer + team_app (l.75-81)
- Le schéma de commande COMMAND_SCHEMA (l.86-164)
- Les sous-commandes `evaluate`, `interrogate`, `schema`, `team create|evaluate|export|history|remove|opt-out` (l.165-985)
- La logique de parsing des réponses utilisateur `_merge_answer()` et `_parse_answer()` (dans `interrogate`)
- Le rendering console (tables Rich, panels, arbres)

**Impact** : violation du Single Responsibility Principle. Le CLI contient de la logique métier d'interaction (parsing réponses, formatage sorties) qui pourrait être extraite. La densité de `# noqa` et les suppressions ruff (`ARG001`, `ARG002`, `E501`, `SIM108`, `F401`, `E741`, `RUF059`) à `pyproject.toml:59` confirment une complexité élevée.

**Recommendation** : Extraire un module `src/laivelup/interaction.py` (parsing réponses + questions interactives) et éventuellement `src/laivelup/output.py` (formatage console Rich). Chaque module resterait < 500l.

---

### F2 — `report.py` dépasse 500 lignes (1051l) — SEVERITY: HIGH

**File:line** : `src/laivelup/report.py:1-1051`  
**Criterion** : modules < 500l  
**ADR ref** : ADR-0016 (sortie MD+HTML)

Le module `report.py` contient :
- Le glossaire pédagogique AIDD `GLOSSARY` (l.19-62)
- Les références curatées `REFERENCES` (l.65-81)
- Les couleurs par niveau `LEVEL_COLORS` (l.84-92) — **dupliqué** avec `calibrate_dashboard.py:18-26`
- Les fonctions `render_markdown()` et `render_html()` (~800 lignes de rendering)
- `write_reports()` et `verdict_to_dict()`

**Impact** : violation du seuil 500l. La duplication de `LEVEL_COLORS` entre `report.py:84-92` et `calibrate_dashboard.py:18-26` est une violation DRY (Don't Repeat Yourself). Les deux dicts sont identiques.

**Recommendation** : Extraire `LEVEL_COLORS` dans `model.py` (ou un nouveau `src/laivelup/theme.py`) pour éliminer la duplication. Envisager de séparer `render_markdown()` et `render_html()` dans des sous-modules dédiés.

---

### F3 — `architecture.mmd` périmé — SEVERITY: MEDIUM

**File:line** : `docs/architecture.mmd:1-106`  
**ADR ref** : ADR-0001, ADR-0008, ADR-0015

Le diagramme Mermaid contient plusieurs inexactitudes par rapport au code actuel :

| Problème | Ligne | Détail |
|----------|-------|--------|
| `BENCHMARK --> CLI_YML` | l.83 | Référence `CLI_YML` inexistante — devrait être `CI_YML` (défini l.42) |
| Script manquant | — | `extract_official_profile.py` existe dans `scripts/` mais n'apparaît pas dans le diagramme |
| Module manquant | — | `calibrate_core.py` et `calibrate_dashboard.py` ne sont pas dans le diagramme (sous-graphe Core) |
| Module manquant | — | `_completion_patch.py` absent du diagramme |
| Ghost `tui/` | — | `src/laivelup/tui/` contient des `.pyc` sans sources `.py` — artefact d'une implémentation supprimée, non documenté |

**Impact** : un nouveau développeur ou un agent IA se basant sur le diagramme aurait une vue incomplète de l'architecture. La référence `CLI_YML` produirait un diagramme Mermaid cassé.

**Recommendation** : Mettre à jour le diagramme pour refléter la structure actuelle. Supprimer le répertoire `tui/` (ou documenter s'il est en suspens).

---

### F4 — ADR-0017 bonus axis : conforme, non implémenté — SEVERITY: INFO

**File:line** : `docs/adr/0017-axe-bonus-industrialisation-hors-regle-and.md`  
**ADR ref** : ADR-0017

L'ADR-0017 déclare explicitement le statut « code à venir, non implémenté à la date de cet ADR » (l.80-83). Une recherche `BONUS|bonus_axis|industrialisation` dans `src/laivelup/` retourne zéro résultat. Ceci est **cohérent** avec l'ADR.

Le `model.py` ne contient pas de `bonus_axis_scores` dans `Verdict` (l.100-112), et `scoring.py` n'a pas de chemin bonus. La conformité est respectée : l'ADR documente une décision future, le code ne l'a pas encore.

**Impact** : aucun risque architectural actuel. Le schema `schemas/profile.schema.json:80` a `"additionalProperties": false` sur `traces` — future implémentation devra y ajouter une propriété `industrialisation` optionnelle (comme souligné dans l'ADR l.47-53).

---

### F5 — `LEVEL_COLORS` duplication (DRY) — SEVERITY: MEDIUM

**File:line** : `src/laivelup/report.py:84-92` ∷ `src/laivelup/calibrate_dashboard.py:18-26`  
**ADR ref** : ADR-0004 (niveaux 7 couleurs)

Le dict `LEVEL_COLORS` est copié à l'identique entre deux modules. Les deux dicts mappent `Level → {bg, fg, accent, icon}` avec exactement les mêmes valeurs.

**Impact** : si les couleurs changent, il faudra modifier deux fichiers. Violation DRY.

**Recommendation** : Centraliser dans `model.py` ou un nouveau `src/laivelup/theme.py` et importer dans les deux modules.

---

### F6 — `team.py` mélange domaine + persistance + export — SEVERITY: LOW

**File:line** : `src/laivelup/team.py:1-412`  
**ADR ref** : ADR-0006 (équité), ADR-0007 (team tracker RGPD)

`team.py` contient :
- Le modèle domaine (`Team`, `MemberSnapshot` — l.126-148)
- La logique métier (`create_team`, `evaluate_member`, `remove_member`, `set_opt_out` — l.156-246)
- La persistance (`save_team`, `load_team` — l.50-123)
- Les exports (`export_json`, `export_markdown`, `export_csv`, `export_html` — l.249-412)

**Impact** : mélange de responsabilités. La persistance (sérialisation JSON + atomic write) et les exports (4 formats) pourraient être séparés. Cependant, à 412 lignes le module reste sous le seuil 500l, donc c'est un smell architectural, pas une violation.

**Recommendation** : Au prochain refactoring significatif, extraire `src/laivelup/team_export.py` (4 formats d'export) et éventuellement `src/laivelup/team_persistence.py` (save/load).

---

### F7 — `scoring.py.bak` dans l'arborescence source — SEVERITY: LOW

**File:line** : `src/laivelup/scoring.py.bak`  
**Criterion** : artefacts non trackés

Un fichier `.bak` existe dans `src/laivelup/`. Ce n'est pas un module Python, pas de référence dans `pyproject.toml`, et potentiellement tracké par git.

**Impact** : pollution de l'arborescence source. Risque de confusion si un développeur édite le mauvais fichier.

**Recommendation** : Supprimer `scoring.py.bak` et l'ajouter au `.gitignore` si nécessaire.

---

## Conformance ADRs

| ADR | Statut | Conforme | Notes |
|-----|--------|----------|-------|
| ADR-0001 | Stack Typer+Rich+pytest+hypothesis | **OUI** | `pyproject.toml:7` — deps alignées |
| ADR-0002 | FR→EN naming | **OUI** | Docstrings FR, vars EN, messages CLI FR |
| ADR-0003 | Encoding cross-platform | **OUI** | `encoding.py:20-132` — 4 couches documentées |
| ADR-0004 | 4 axes, 7 niveaux, seuils | **OUI** | `model.py:17-37`, `scoring.py:32-47` |
| ADR-0005 | La Décodeuse, refus>deviner | **OUI** | `scoring.py` refus, `cli.py:interrogate` questions |
| ADR-0006 | Équité, pseudo-anonyme | **OUI** | `team.py` RGPD, `scoring.py` neurotype absent |
| ADR-0007 | Team slug HMAC-SHA256 | **OUI** | `utils.py:16-31` — HMAC salé vs brut |
| ADR-0008 | CI matrix 3OS×3Py | **OUI** | `.github/workflows/ci.yml` existe |
| ADR-0009 | Couverture 100% scoring | **OUI** | `pyproject.toml:149-151` override scoring 100% |
| ADR-0010 | Sécurité bandit baseline | **OUI** | `pyproject.toml:153-159` bandit config |
| ADR-0011 | pip install entrypoint | **OUI** | `pyproject.toml:11` `laivelup = "laivelup.cli:app"` |
| ADR-0012 | JSON Schema Draft 2020-12 | **OUI** | `schemas/profile.schema.json:2`, `schema.py:99` |
| ADR-0013 | Calibration scripts | **OUI** | `scripts/calibrate.py` + `calibrate_core.py` |
| ADR-0014 | Vidéo démo asciinema | **N/A** | Hors périmètre code |
| ADR-0015 | CLI vs Web | **OUI** | CLI Typer unique, pas de serveur |
| ADR-0016 | Sortie MD+HTML | **OUI** | `report.py` render_markdown + render_html |
| ADR-0017 | Bonus axis hors AND | **OUI** | Non implémenté (cohérent avec ADR) |

---

## Couverture

### Import graph (DAG — pas de cycles)

```
model.py ← [leaf]
utils.py ← [leaf]
questions.py ← [leaf]
scoring_defaults.py → model
schema.py ← [leaf]
encoding.py ← [leaf]
_completion_patch.py ← [leaf]
scoring.py → model, questions, scoring_defaults
report.py → model, utils
calibrate_core.py → model, scoring
calibrate_dashboard.py → calibrate_core, model
team.py → model, scoring, utils
cli.py → __version__, _completion_patch, calibrate_dashboard, encoding, model,
         questions, report, schema, scoring, team
__init__.py → scoring_defaults
__main__.py → cli
```

**Résultat** : 0 imports circulaires. Le graphe est un DAG acyclique dirigé. La couche Core (`model`, `scoring`, `report`) est consommée par CLI sans couplage retour. Respect de la règle de dépendance : domaine ← CLI, jamais l'inverse.

### Module sizes (seuil: 500l)

| Module | Lignes | Status |
|--------|--------|--------|
| `cli.py` | 985 | **VIOLATION** (>500l) |
| `report.py` | 1051 | **VIOLATION** (>500l) |
| `scoring.py` | 443 | OK |
| `team.py` | 412 | OK |
| `calibrate_dashboard.py` | 331 | OK |
| `schema.py` | 166 | OK |
| `calibrate_core.py` | 165 | OK |
| `encoding.py` | 132 | OK |
| `model.py` | 112 | OK |
| `_completion_patch.py` | 83 | OK |
| `questions.py` | 44 | OK |
| `utils.py` | 31 | OK |
| `scoring_defaults.py` | 26 | OK |
| **TOTAL** | **3981** | — |

### Frontières CLI↔Domaine↔Persistance

| Frontière | Constat | Verdict |
|-----------|---------|---------|
| CLI → Domaine | `cli.py` importe `scoring`, `model`, `report`, `schema`, `questions` | OK — CLI consomme le domaine |
| Domaine → CLI | Aucun module domaine n'importe `cli` | OK — pas de couplage retour |
| Domaine → Persistance | `team.py` contient `save_team`/`load_team` (JSON read/write) | SMELL — mélange persistance/domaine |
| Persistance → Domaine | `team.py` importe `model` pour `Level`, `ProfileData`, `Verdict` | OK — persistance dépend du modèle |
| CLI → Persistance | `cli.py` importe `team.save_team`, `team.load_team` | OK — CLI orchestre |

### Packaging schemas dans wheel

`pyproject.toml:34-35` :
```toml
[tool.setuptools.package-data]
laivelup = ["schemas/*.json"]
```

Le fichier `schemas/profile.schema.json` est inclus dans le package distribué. L'installation `pip install laivelup` (non éditable) embarque le schema. L'installation dev `pip install -e '.[dev]'` le rend accessible via le path relatif dans `schema.py:14`. **Conforme**.

### build/ obsolète

Le répertoire `build/` existe mais est vide (0 fichiers). Le `.gitignore` devrait l'exclure. L'artefact de build n'est pas tracké. **Conforme** à la note du périmètre.

---

## Summary

| Critère | Résultat |
|---------|----------|
| Layout `src/` respecté | **OUI** — package `laivelup` sous `src/` |
| ADRs cohérents avec code | **OUI** — 17/17 conformes |
| Imports circulaires | **AUCUN** — DAG propre |
| Modules < 500l | **NON** — cli.py (985l), report.py (1051l) |
| Frontières CLI↔domaine↔persistance | **SMELL** — team.py mélange domaine+persistance |
| Packaging schemas dans wheel | **OUI** — package-data configuré |
| architecture.mmd à jour | **NON** — 5 inexactitudes (CLI_YLY, scripts manquants, ghost tui/) |
| ADR-0017 bonus axis | **COHÉRENT** — non implémenté, documenté |
