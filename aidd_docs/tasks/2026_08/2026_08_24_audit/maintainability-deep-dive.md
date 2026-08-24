# Deep Dive Maintainability — LAIVEL UP

**Date** : 2026-08-24
**Méthode** : persona *Maintainability Reviewer* appliquée manuellement — lecture statique des 11 fichiers `src/laivelup/*.py` (1903 lignes), 55 fonctions, 7 classes.
**Angle** : pas "est-ce que ça compile", mais "combien ça coûte à maintenir, àmodifier, à transférer à un·e nouveau·elle développeur·se".

## 0. Vue d'ensemble

| Métrique | Valeur |
|----------|--------|
| Lignes totales | 1 903 |
| Fichiers | 11 |
| Fonctions | 55 |
| Classes/dataclasses | 7 |
| TODO/FIXME/HACK | 0 |
| Patterns dupliqués | 4 |
| Cyclomatic complexity max | ~15 (`evaluate` dans `scoring.py`) |

Le codebase est **propre et homogène** : aucun TODO, conventions de nommage cohérentes (snake_case, prefixes `_` pour le privé), docstrings FR sur les modules, type hints sur les signatures publiques. Pas de dette technique visible. Les 4 findings ci-dessous sont des optimisations, pas des dettes critiques.

## 1. Findings

| # | Sev | Catégorie | Location | Constat | Effort |
|---|-----|-----------|----------|---------|--------|
| 1 | 🟡 P2 | DRY | `team.py` lines 234, 277, 340 | Bloc opt-out history filtré 3× identique | XS |
| 2 | 🟡 P2 | DRY | `team.py` lines 155, 210, 227 | Guard "membre non trouvé" 3× identique | XS |
| 3 | 🟢 P3 | DRY | `team.py` + `report.py` | `_slug()` wrapper dupliqué dans 2 fichiers | XS |
| 4 | 🟢 P3 | DRY | `report.py` + `team.py` | CSS badge `.ok`/`.ko` quasi identique dans 2 fichiers | XS |

---

### #1 — Bloc opt-out history filtré 3× identique (`team.py`)

Le même bloc de 4 lignes apparaît dans `export_json` (L234), `export_markdown` (L277) et `export_html` (L340) :

```python
opt_out_slugs = {s for s, m in team.members.items() if m.opt_out}
history_filtered = [
    h for h in team.history
    if h.get("slug") not in opt_out_slugs and not h.get("opt_out")
]
```

**Correctif** : extraire dans `_filter_history(team)` → 1 appel au lieu de 3 copier-coller.

### #2 — Guard "membre non trouvé" 3× identique (`team.py`)

Le même if/raise apparaît dans `evaluate_member` (L155), `remove_member` (L210) et `set_opt_out` (L227) :

```python
if slug not in team.members:
    raise ValueError(f"Membre '{slug}' non trouvé dans l'équipe '{team.name}'")
```

**Correctif** : extraire dans `_get_member(team, slug)` qui retourne le member ou raise → plus de duplication, message d'erreur unique.

### #3 — `_slug()` wrapper dupliqué 2 fichiers

`team.py` (L130) et `report.py` (L167) définissent tous les deux :
```python
def _slug(name: str, salt: str | None = None) -> str:
    return slug(name, salt)
```

Aucune logique ajoutée. Les deux pourraient appeler `utils.slug()` directement, ou garder un seul wrapper dans `utils.py`.

### #4 — CSS badge identique dans 2 fichiers

`report.py::render_html` et `team.py::export_html` définissent des CSS quasi identiques :
```css
.badge { display: inline-block; padding: .2rem .5rem; border-radius: 999px; font-weight: 700; }
.ok    { background: #d1f5d8; color: #0b5b23; }
.ko    { background: #ffe3e3; color: #8b1a1a; }
```

Mineur (CSS inline, pas de stylesheet partagé), mais si le design change il faudra modifier aux 2 endroits.

## 2. Points positifs (pas de finding)

- **Zéro TODO/FIXME/HACK** dans tout le package — le code est "fermé" au sens où il n'y a pas de dette technique cachée.
- **Type hints** sur toutes les signatures publiques — aide l'autocomplétion et les refactors.
- **Docstrings FR** cohérentes — un·e nouveau·elle dev peut lire le code sans le README.
- **Fonctions courtes** : aucune ne dépasse 40 lignes (hors `evaluate` à ~50 lignes, acceptable pour la fonction centrale).
- **Séparation des couches** propre : `model.py` (types) → `scoring.py` (logique) → `report.py` (sortie) → `cli.py` (orchestration). Pas de cycle.
- **Imports en tête de fichier** — après le fix #5 de l'audit architecture, plus d'imports tardifs injustifiés.

## 3. Recommandations

| Priorité | Action | Effort |
|----------|--------|--------|
| P2 | Extraire `_filter_history(team)` dans `team.py` | 5 min |
| P2 | Extraire `_get_member(team, slug)` dans `team.py` | 5 min |
| P3 | Supprimer `_slug()` wrapper de `team.py` et `report.py`, appeler `utils.slug()` directement | 5 min |
| P3 | Extraire CSS badge dans un constant partagé ou laisser tel quel (CSS inline mineur) | 2 min |

**Total** : ~15 min de refactoring pour 4 améliorations DRY.

## 4. Verdict Maintainability

**Score** : 9/10 — codebase propre, bien structuré, sans dette technique. Les 4 findings sont des micro-optimisations DRY, pas des problèmes de maintenabilité. Un·e nouveau·elle développeur·se peut comprendre le code en ~30 min de lecture.

---

*Généré par maintainability review — session 3 critique, 2026-08-24*
