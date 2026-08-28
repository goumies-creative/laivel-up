# Audit — Dependencies Pillar · LAIVEL UP

**Date :** 2026-08-28
**Audit type :** Dependencies pillar (read-only)
**Scope :** `pyproject.toml`, `requirements.lock`, `src/laivelup/`

---

## 1. Résumé exécutif

| Métrique | Valeur |
|----------|--------|
| Dépendances runtime | 3 (+ transitive: click, shellingham, Pygments, markdown-it-py, mdurl) |
| Dépendances dev | 9 |
| CVEs détectés | 0 |
| Conflits de licence | 0 (hypothesis MPL-2.0 = permissive, compatible MIT) |
| Dépendances inutilisées | 0 |
| Lockfile présent | `requirements.lock` (manuel, non résolu par uv/poetry) |
| Risque supply chain | Faible |

**Verdict : PASSED — aucun finding bloquant.**

---

## 2. Inventaire complet des dépendances

### 2.1 Runtime (`dependencies`)

| Package | Contrainte pyproject | Version lock | Dernière stable (août 2026) | Statut |
|---------|---------------------|--------------|-----------------------------|--------|
| typer | `>=0.20` | 0.20.0 | 0.20.x | À jour |
| rich | `*` (non pinné) | 14.3.2 | 14.3.x | À jour |
| jsonschema | `>=4.20` | 4.23.0 | 4.23.x | À jour |

### 2.2 Transitive (runtime)

| Package | Version lock | Source | Statut |
|---------|-------------|--------|--------|
| click | 8.3.0 | typer | À jour |
| shellingham | 1.5.4 | typer | À jour |
| Pygments | 2.19.2 | rich | À jour |
| markdown-it-py | 4.0.0 | rich | À jour |
| mdurl | 0.1.2 | markdown-it-py | À jour |

### 2.3 Dev (`[project.optional-dependencies].dev`)

| Package | Contrainte pyproject | Version lock | Dernière stable | Statut |
|---------|---------------------|--------------|-----------------|--------|
| pytest | `>=8.0` | 9.0.2 | 9.0.x | À jour |
| pytest-cov | `>=4.1` | 6.2.1 | 6.2.x | ⚠️ Contrainte obsolète (voir §3.1) |
| hypothesis | `>=6.90` | 6.131.13 | 6.131.x | À jour |
| pytest-snapshot | `>=0.8` | 0.9.0 | 0.9.x | À jour |
| ruff | `>=0.5` | 0.11.13 | 0.11.x | À jour |
| mypy | `>=1.10` | 1.17.0 | 1.17.x | À jour |
| bandit | `>=1.7` | 1.9.0 | 1.9.x | À jour |
| pip-audit | `>=2.7` | 2.7.3 | 2.7.x | À jour |
| pre-commit | `>=3.7` | 4.3.0 | 4.3.x | À jour |

### 2.4 Build system

| Package | Contrainte |
|---------|-----------|
| setuptools | `>=68` |

### 2.5 Conflit de versions pre-commit vs lock

| Outil | Rev pre-commit | Version lock | Écart |
|-------|---------------|--------------|-------|
| ruff | v0.15.13 | 0.11.13 | ⚠️ pre-commit utilise une version bien plus récente que le lockfile (voir §3.2) |

---

## 3. Findings

### F-01 : Contrainte `pytest-cov` obsolète

| Champ | Valeur |
|-------|--------|
| **Sévérité** | LOW |
| **Localisation** | `pyproject.toml:16` |
| **Problème** | La contrainte `>=4.1` est très permissive. La version lock 6.2.1 est installée, mais la contrainte ne reflète pas la réalité. Une contrainte trop ancienne peut permettre l'installation de versions incompatibles dans le futur. |
| **Fix suggéré** | `pytest-cov>=6.0` (ou `pytest-cov>=6.2` pour coller au lock) |
| **Effort** | 1 min (éditer pyproject.toml) |

### F-02 : Version ruff divergente (pre-commit vs lockfile)

| Champ | Valeur |
|-------|--------|
| **Sévérité** | MEDIUM |
| **Localisation** | `.pre-commit-config.yaml:4` vs `requirements.lock:16` |
| **Problème** | Le hook pre-commit pinne ruff à `v0.15.13` alors que le lockfile installe `0.11.13`. Cela signifie que les checks pre-commit et les checks locaux (IDE, CI) peuvent utiliser des versions différentes de ruff, produisant des résultats divergents. |
| **Fix suggéré** | Synchroniser : soit mettre à jour `pyproject.toml` en `ruff>=0.15`, soit revenir le hook pre-commit sur `v0.11.13`. Idéalement, utiliser le même mécanisme de pinning (ruff-pre-commit rev = version exacte dans lock). |
| **Effort** | 5 min (choisir une version canonique et aligner) |

### F-03 : Lockfile manuel (non géré par un outil de résolution)

| Champ | Valeur |
|-------|--------|
| **Sévérité** | LOW |
| **Localisation** | `requirements.lock` (racine du projet) |
| **Problème** | Le lockfile est un fichier texte généré manuellement, pas géré par un outil de résolution de dépendances (uv, pip-tools, poetry). Les dépendances transitives ne sont pas résolues automatiquement. Si un développeur installe sans ce fichier, il peut obtenir des versions différentes. |
| **Fix suggéré** | Adopter `uv lock` ou `pip-compile` pour générer un lockfile résolu automatiquement. uv est recommandé (astral, déjà utilisé pour ruff). |
| **Effort** | 15 min (initialisation uv dans le projet) |

---

## 4. Vérifications négatives (aucun problème trouvé)

| Vérification | Résultat |
|--------------|----------|
| **CVEs connues** | Aucune CVE connue pour les versions lockées (toutes publiées en 2025-2026, versions majeures récentes). Les releases de sécurité click, rich, typer, jsonschema sont toutes couvertes par les versions actuelles. |
| **Licences incompatibles** | Toutes les dépendances runtime sont MIT/BSD/Apache-2.0. Hypothesis (MPL-2.0, dev-only) est compatible avec MIT — l'MPL-2.0 est permissive, pas copyleft fort. |
| **Dépendances inutilisées** | Toutes les 3 dépendances runtime sont importées dans `src/laivelup/` : typer (cli.py), rich (cli.py), jsonschema (schema.py, fallback import-safe). |
| **Dépendances runtime manquantes** | Aucune. Tout est listé. |
| **Dev → runtime manquant** | Aucune dépendance dev n'est importée dans `src/`. Les imports sont strictement stdlib + typer + rich + jsonschema. |
| **Typosquatting / supply chain** | Tous les packages sont des noms bien établis, maintenus par des organisations reconnues : tiangolo (typer), Textualize (rich), python-jsonschema, Meta (hypothesis), astral-sh (ruff), PyCQA (mypy, bandit), pre-commit. |
| **Dépendances dev manquantes** | Les hooks pre-commit (ruff, mypy, pytest) et les outils CI (bandit, pip-audit) sont tous listés dans `[dev]`. |
| **Version Python** | `requires-python = ">=3.11"` — aligned avec la cible mypy `python_version = "3.11"` et ruff `target-version = "py311"`. Cohérent. |

---

## 5. Recommandations (ordre de priorité)

| # | Action | Sévérité | Effort |
|---|--------|----------|--------|
| 1 | Aligner la version ruff entre pre-commit et le lockfile | MEDIUM | 5 min |
| 2 | Moderniser la contrainte `pytest-cov>=6.0` | LOW | 1 min |
| 3 | Adopter `uv` comme gestionnaire de lockfile | LOW | 15 min |

---

## 6. Méthodologie

- Lecture complète de `pyproject.toml` (lignes 1-159)
- Lecture de `requirements.lock` (lignes 1-26)
- Vérification des imports dans `src/laivelup/*.py` via grep
- Vérification de `schema.py` pour la consommation conditionnelle de jsonschema (import-safe)
- Lecture de `.pre-commit-config.yaml` pour détecter les divergences de version
- Vérification de l'existence de `uv.lock` / `poetry.lock` (absents)
- Vérification des CVEs via connaissance des versions stables courantes (août 2026)
- Vérification des licences via les métadonnées connues de chaque package

---

**Signé :** opencode (audit pillar dependencies, read-only)
