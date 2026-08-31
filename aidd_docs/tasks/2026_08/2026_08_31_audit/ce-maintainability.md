# CE Maintainability Review — LAIVEL UP

**Reviewer:** ce-maintainability-reviewer
**Date:** 2026-08-31
**Scope:** `src/laivelup/`, `scripts/`, `tests/`, `pyproject.toml`
**Method:** Read-only, file:line + grep proof

---

## Verdict

**PASS with reservations** — Le codebase est fonctionnel et bien documenté, mais souffre de duplication inter-fichiers et de god files qui impacteront la maintainability à moyen terme. Aucun blocker critique ; les findings sont des dette technique gérables.

---

## Findings

### F1 — Duplication `_load_profile` × 3 (DRY violation)

| Fichier | Lignes | Taille |
|---------|--------|--------|
| `src/laivelup/cli.py` | 199–242 | 43l |
| `src/laivelup/calibrate_core.py` | 44–54 | 11l |
| `scripts/calibrate.py` | 59–73 | 15l |

**Preuve grep:** `grep -rn "_load_profile" src/ scripts/` → 17 occurrences, 3 définitions.

Les trois font la même chose (charger JSON → `ProfileData`) avec des variantes mineures (cli.py ajoute la validation schema + taille max). Calibrate_core et calibrate.py sont quasi identiques. La version calibrate_core.py pourrait être la source unique.

**Impact:** Modification du format profil nécessite 3 mises à jour synchronisées.
**Confiance:** 85 — duplication objective, 3 implémentations visibles.

---

### F2 — Duplication `_load_expected` × 2

| Fichier | Lignes |
|---------|--------|
| `src/laivelup/calibrate_core.py` | 57–61 |
| `scripts/calibrate.py` | 76–81 |

Code quasi identique (5 lignes). `calibrate_core.py` est le module réutilisable ; le script duplique.

**Confiance:** 85

---

### F3 — Duplication `LEVEL_LABELS` / `AXIS_LABELS` dans `scripts/calibrate.py`

`scripts/calibrate.py:32–47` redéfinit `AXIS_LABELS` et `LEVEL_LABELS` au lieu d'importer depuis `model.py`.

```python
# scripts/calibrate.py:32
AXIS_LABELS = {
    'size': 'Taille',
    ...
}
```

`model.py:40–45` contient la source de vérité `AXIS_LABELS`. Le script ne l'importe pas (utilise `sys.path.insert` mais n'importe que `AXES`, `Level`, `ProfileData`, `evaluate`).

**Confiance:** 80

---

### F4 — Duplication `LEVEL_COLORS` × 2

| Fichier | Lignes |
|---------|--------|
| `src/laivelup/report.py` | 84–92 |
| `src/laivelup/calibrate_dashboard.py` | 18–26`

Dict `LEVEL_COLORS` copié-collé. Les deux fichiers ont les mêmes 7 entrées.

**Confiance:** 90 — duplication exacte vérifiable.

---

### F5 — Dead import `QUESTION_TRACE_KEYS`

`cli.py:44` importe `QUESTION_TRACE_KEYS` mais jamais utilisé dans le fichier.

```
# cli.py:44
from .questions import QUESTION_IDS, QUESTION_TRACE_KEYS
```

`grep -n "QUESTION_TRACE_KEYS" src/laivelup/cli.py` → uniquement la ligne d'import (44). L'import est masqué par le ruff rule `F401` override dans `pyproject.toml:59`.

**Confiance:** 95 — import sans usage, preuve grep.

---

### F6 — Wrapper superflu `_slug` dans `team.py`

`team.py:151–153` définit `_slug` qui est un wrapper direct de `slug` depuis `utils.py` :

```python
def _slug(name: str, salt: str | None = None) -> str:
    """Pseudo-anonyme RGPD — wrapper pour compatibilité interne."""
    return slug(name, salt)
```

Appelé une seule fois (`team.py:163`). La couche d'indirection n'ajoute aucune logique.

**Confiance:** 75 — wrapper inutile avec un seul consommateur.

---

### F7 — Functions > 50 lignes

| Fonction | Fichier:Lignes | Taille | Raison |
|----------|----------------|--------|--------|
| `interrogate` | `cli.py:503–618` | **115l** | Flow entretien + rendu NES mélangés |
| `_print_verdict` | `cli.py:311–406` | **95l** | Rendu Rich + logique de display |
| `run_calibration` | `calibrate_core.py:64–165` | **101l** | Boucle + comparaison + construction résultats |
| `generate_calibrate_html` | `calibrate_dashboard.py:64–321` | **257l** | Template HTML inline |
| `render_html` | `report.py:433–996` | **563l** | Template HTML inline (CSS ~400l) |
| `_render_pedagogical_section` | `report.py:349–430` | **81l** | Construction HTML pédagogique |
| `_render_world_map` | `report.py:155–217` | **62l** | Carte Patapon |
| `export_html` | `team.py:341–412` | **71l** | Template HTML inline |
| `normalize_profile` | `scoring.py:76–136` | **60l** | Validation multi-champs |
| `evaluate_profile` | `cli.py:428–489` | **61l** | Orchestration evaluate + fail-on |

**Note:** `render_html` (563l) est principalement un template HTML inline — la logique Python réelle est ~60l. Le template est un artefact de JSX-like dans un fichier .py, pas de la complexité algorithmique. Même observation pour `generate_calibrate_html` et `export_html`.

**Confiance:** 70 — les seuils sont respectés mais les templates HTML inline sont la cause principale.

---

### F8 — God files `cli.py` (985l) et `report.py` (1051l)

**cli.py** concentre : CLI setup Typer, 7 command handlers, rendu NES 8-bit (constants + 5 fonctions), chargement profil, filtrage champs, flow interrogate (115l), 5 commands team. Deux responsabilités distinctes : CLI orchestration + rendu terminal.

**report.py** concentre : rendu Markdown, rendu HTML (563l template inline), sérialisation JSON, glossaire, références, couleurs. Le template HTML domine le fichier.

**Confiance:** 65 — les fichiers sont gros mais la structure interne est cohérente. Le vrai coût est la lisibilité pour un nouveau développeur face à 1000+ lignes.

---

### F9 — Dead code: `apply_scenario_b` / `apply_scenario_c`

`scripts/apply_calibration_fix.py:154–179` : deux fonctions lèvent `NotImplementedError`. Elles documentent un plan mais ne sont pas implémentées.

```python
def apply_scenario_b(diagnostic, dry_run=True):
    raise NotImplementedError(...)

def apply_scenario_c(diagnostic, dry_run=True):
    raise NotImplementedError(...)
```

Enregistrées dans `SCENARIO_HANDLERS` (ligne 182–186) — accessibles via CLI mais crashent.

**Confiance:** 75 — code atteignable mais qui crash par design.

---

### F10 — `_validate_minimal` (schema.py) — fallback inutile

`schema.py:109–166` implémente une validation minimale sans `jsonschema`. Or, `pyproject.toml:7` déclare `jsonschema>=4.20` comme dépendance obligatoire. Le fallback n'est jamais atteint en conditions normales.

**Confiance:** 70 — dépendance obligatoire rend le fallback mort en pratique.

---

## Métriques

| Métrique | Valeur | Cible | Statut |
|----------|--------|-------|--------|
| TODO/FIXME stale | 0 | 0 | PASS |
| Functions >50l | 10 | 0 | WARN |
| Type hints (estimé) | ~85% | >80% | PASS |
| God files (>500l) | 2 | 0 | WARN |
| DRY violations | 4 (F1-F4) | 0 | WARN |
| Dead code / imports | 3 (F5,F9,F10) | 0 | WARN |
| Wrapper inutile | 1 (F6) | 0 | INFO |

---

## Couverture

| Zone | Fichiers | Couvert |
|------|----------|---------|
| `src/laivelup/` | 15 fichiers .py | 100% |
| `scripts/` | 9 fichiers .py | 100% |
| `tests/` | 36 fichiers .py | Structure vérifiée |
| `pyproject.toml` | 1 | Vérifié |

---

## Message final

**Verdict: PASS with reservations**

- **10 findings** (0 critical, 4 high, 4 medium, 2 low)
- **0 stale TODO/FIXME**
- **~85% type hints** (au-dessus du seuil 80%)

**Top 3 à adresser :**
1. **F1+F2+F3+F4 — Duplication inter-fichiers** : `_load_profile` × 3, `_load_expected` × 2, `LEVEL_COLORS` × 2, `AXIS_LABELS` dupliqué. Extraire dans un module partagé (ex: `laivelup.profile_io`).
2. **F7 — 10 fonctions >50l** : principalement des templates HTML inline (`render_html` 563l). Extraire les templates dans des fichiers `.html.j2` ou des fonctions plus petites.
3. **F5+F9+F10 — Dead code** : `QUESTION_TRACE_KEYS` import inutilisé, `apply_scenario_b/c` NotImplementedError, `_validate_minimal` fallback mort. Nettoyage de ~150 lignes.
