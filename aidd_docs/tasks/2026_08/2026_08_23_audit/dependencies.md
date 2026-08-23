# Codebase Audit: dependencies — goumies-creative-laivel-up

Le vrai problème de dépendances n'est pas une CVE : c'est un fichier de données (`schemas/profile.schema.json`) qui n'est jamais empaqueté avec le wheel — la cause racine du plantage documenté en architecture.

- **Date**: 2026-08-23
- **Scope**: `pyproject.toml`, `requirements.lock`, `.github/workflows/ci.yml`
- **Health**: poor
- **Findings**: 1 critical, 1 warning

## Findings

| Sev | Category | Location | Issue | Suggested fix | Effort |
| --- | --- | --- | --- | --- | --- |
| 🔴 | dependencies | `pyproject.toml:30-31` | Aucune section `[tool.setuptools.package-data]` : `schemas/profile.schema.json` (hors de `src/`) n'est déclaré nulle part comme fichier de données du package → absent du wheel distribué sur PyPI. Confirme la casse décrite dans le finding architecture (`schema.py:13`). | Déplacer le schéma sous `src/laivelup/schemas/` puis ajouter `[tool.setuptools.package-data]` `laivelup = ["schemas/*.json"]` | M |
| 🟡 | dependencies | `requirements.lock:1-8` | Le lockfile de dev ne contient ni `jsonschema` (dépendance runtime obligatoire, `pyproject.toml:7`) ni aucun des 9 outils déclarés dans `[project.optional-dependencies].dev` (`pytest-cov`, `hypothesis`, `pytest-snapshot`, `ruff`, `mypy`, `bandit`, `pip-audit`, `pre-commit`), malgré le commentaire « Lockfile de développement · pytest + deps du CLI ». La reproductibilité de l'environnement de dev n'est pas garantie par ce fichier. | Régénérer le lockfile (`pip-compile` / `uv pip compile`) en incluant `.[dev]` | S |

## Top actions

1. Corriger l'empaquetage du schéma (`package-data`) — bloquant pour toute distribution réelle du CLI.
2. Régénérer `requirements.lock` pour qu'il couvre effectivement les dépendances déclarées.

## Coverage

- **Scanned**: dependencies (`pyproject.toml`, `requirements.lock`, config bandit/pip-audit dans `pyproject.toml`, jobs CI)
- **Skipped**: exécution de `pip-audit` (recherche de CVE) — pas d'outil d'exécution de code sur la machine de l'utilisatrice dans cet environnement d'audit ; pas de CVE inventée. Atténuant : `.github/workflows/ci.yml` (job `security`) exécute déjà `pip-audit --skip-editable` à chaque push, avec un lockfile de dépendances runtime minimal (3 paquets directs : `typer`, `rich`, `jsonschema`) qui limite la surface d'exposition.
