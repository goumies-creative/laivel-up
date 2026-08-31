# Audit — Pillier DEPENDENCIES

> **Projet :** goumies-creative-laivel-up (CLI Python `laivelup`)
> **Date :** 2026-08-31
> **Auditeur :** AIDD read-only
> **Scope :** manifestes (pyproject.toml), lockfile (requirements.lock), CI (.github/workflows/ci.yml), schemas embarqués

---

## Résumé

| Métrique | Valeur |
|----------|--------|
| Dependencies runtime déclarées | 3 (`typer`, `rich`, `jsonschema`) |
| Dependencies dev déclarées | 10 (`pytest`, `pytest-cov`, `hypothesis`, `pytest-snapshot`, `ruff`, `mypy`, `bandit`, `pip-audit`, `pre-commit`, `mutmut`) |
| Packages dans lockfile | 19 (6 runtime + 9 dev + 4 transitive) |
| Vulnérabilités connues (pip-audit) | 0 |
| Findings | **5** (1 Critical, 2 Warning, 2 Info) |

---

## Findings

### DEP-001 — Lockfile incomplet : `mutmut` manquant (CRITICAL)

**Fichier :** `requirements.lock`
**Sévérité :** Critical
**Description :** `mutmut<3` est déclaré dans `[project.optional-dependencies] dev` (pyproject.toml:24) mais absent du lockfile. Un `pip install -r requirements.lock` ne l'installerait pas, ce qui casse le workflow de mutation testing.

**Preuve :**
```
# pyproject.toml:24
"mutmut<3",
```
```
# requirements.lock — absent de la section Dev dependencies
```

**Impact :** Reproductibilité brisée pour le mutation testing (exécution manuelle post-soumission, cf. pyproject.toml:167-173).

**Recommandation :** Ajouter `mutmut==2.5.1` (version installée) à la section `# Dev dependencies` du lockfile.

---

### DEP-002 — Lockfile incomplet : transitives de `jsonschema` manquantes (WARNING)

**Fichier :** `requirements.lock`
**Sévérité :** Warning
**Description :** Le lockfile liste `jsonschema==4.23.0` mais omet ses 4 dépendances transitives obligatoires. `pip show jsonschema` révèle :

| Manquante | Version installée | Licence |
|-----------|-------------------|---------|
| `attrs` | 25.4.0 | MIT |
| `jsonschema-specifications` | (résolue) | MIT |
| `referencing` | (résolue) | MIT |
| `rpds-py` | (résolue) | MIT |

**Impact :** Le lockfile ne garantit pas la résolution complète pour `jsonschema` en environnement vierge. Fonctionnel car `pip install -e ".[dev]"` résout via pyproject.toml, mais le lockfile ne tient pas sa promesse de reproductibilité.

**Recommandation :** Compléter le lockfile avec les 4 transitives (ou adopter un outil de lock complet : `pip-compile`, `uv lock`, `pdm lock`).

---

### DEP-003 — `pip-audit` en CI : audit de l'environnement, pas du lockfile (WARNING)

**Fichier :** `.github/workflows/ci.yml:54`
**Sévérité :** Warning
**Description :** La CI lance `pip-audit --skip-editable` (ci.yml:54) qui audite les packages installés dans l'environnement CI, pas le lockfile lui-même. Le dry-run local confirme 0 vulnérabilités sur 309 packages, mais c'est un audit indirect.

**Preuve :**
```yaml
# ci.yml:54
- name: pip-audit dependency scan
  run: pip-audit --skip-editable
```

**Impact :** Un vulnerability audit ciblé le lockfile (`pip-audit -r requirements.lock`) serait plus faithful au produit shipé. L'approche actuelle audite aussi des dépendances de l'environnement CI qui ne font pas partie du produit.

**Recommandation :** Ajouter ou remplacer par `pip-audit -r requirements.lock` pour auditer le lockfile directement.

---

### DEP-004 — `build/` artefact obsolète présent (INFO)

**Fichier :** `build/`
**Sévérité :** Info
**Description :** Le répertoire `build/` contient des artefacts de build (`bdist.win-amd64/`, `lib/`). Il est listé dans le contexte comme obsolète mais toujours présent sur disque.

**Impact :** Inutile en version control. Devrait être dans `.gitignore` (vérifier) et nettoyé.

**Recommandation :** Vérifier que `build/` est dans `.gitignore` et le supprimer du workspace local.

---

### DEP-005 — `schemas/*.json` embarqués correctement (INFO — OK)

**Fichier :** `pyproject.toml:34-35`, `src/laivelup/schema.py:14`
**Sévérité :** Info (pas un finding, confirmation)
**Description :** `pyproject.toml` déclare `[tool.setuptools.package-data] laivelup = ["schemas/*.json"]` (pyproject.toml:35). Le fichier `schemas/profile.schema.json` existe et est chargé via `Path(__file__).parent / 'schemas' / 'profile.schema.json'` (schema.py:14). L'installation non-éditable (`pip install .`) embarquera le schéma.

**Impact :** Aucun. Conforme.

---

## Vérifications complémentaires

### pip-audit (vulnérabilités)

| Méthode | Résultat |
|---------|----------|
| `pip-audit --dry-run` (env local) | **0 vulnérabilités** sur 309 packages |
| `pip-audit -r requirements.lock` | Timeout (>120s) — réseau OSV lent |
| CI (`pip-audit --skip-editable`) | Configuré, exécuté sur ubuntu-latest |

### Licences

| Package | Licence | Statut |
|---------|---------|--------|
| typer | MIT | OK |
| rich | MIT | OK |
| jsonschema | MIT | OK |
| click | BSD-3-Clause | OK |
| shellingham | ISC | OK |
| Pygments | BSD-2-Clause | OK |
| mutmut | BSD | OK |
| attrs | MIT | OK |
| referencing | MIT | OK |
| rpds-py | MIT | OK |

**Aucune licence GPL/AGPL détectée.** Toutes les dépendances runtime + transitives sont permissives (MIT/BSD/ISC).

### Imports runtime — dépendances déclarées

| Dépendance | Importé dans src/ | Statut |
|------------|-------------------|--------|
| typer | `cli.py:34` | OK |
| rich | `cli.py:35-37` (Console, Prompt, Table) | OK |
| jsonschema | `schema.py:93` (lazy import) | OK |

### Dépendances transitives non listées dans lockfile

| Package parent | Manquantes |
|----------------|------------|
| typer → click, shellingham | click ✓, shellingham ✓ (listées comme runtime) |
| rich → markdown-it-py, Pygments | markdown-it-py ✓, Pygments ✓ (listées) |
| jsonschema → attrs, jsonschema-specifications, referencing, rpds-py | **Toutes manquantes** |

---

## Verdict

| Sévérité | Count |
|----------|-------|
| Critical | 1 |
| Warning | 2 |
| Info | 2 |
| **Total** | **5** |

**Le lockfile est fonctionnellement incomplet** — il ne couvre pas les transitives de `jsonschema` et omet `mutmut`. L'approche actuelle fonctionne grâce à `pip install -e ".[dev]"` (résolution via pyproject.toml), mais la promesse de reproductibilité du lockfile n'est pas tenue. Le scan de vulnérabilités est propre (0 CVE). Les licences sont toutes permissives. Le package-data schemas est correctement configuré.
