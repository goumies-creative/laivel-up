# Codebase Audit: performance — goumies-creative-laivel-up

Outil léger (CLI + JSON < 2 Mo) : pas de risque de performance sur le moteur de scoring lui-même. Le seul point notable est côté génération de profil (git).

- **Date**: 2026-08-23
- **Scope**: `src/laivelup/`, `scripts/`
- **Health**: good
- **Findings**: 0 critical, 1 warning, 1 minor

## Findings

| Sev | Category | Location | Issue | Suggested fix | Effort |
| --- | --- | --- | --- | --- | --- |
| 🟡 | performance | `scripts/generate_profile.py:46-47` | `_detect_pr_sizes` lance un sous-processus `git diff --stat` par commit (jusqu'à 50 itérations séquentielles) au lieu d'un seul appel batché — chaque `git` démarre un nouveau processus. Ce chemin s'exécute à chaque run de `.github/workflows/aidd-eval.yml` (une PR = un run). | Remplacer la boucle par un seul `git log --shortstat --author=... --since=...` et parser la sortie agrégée | M |
| 🟢 | performance | `scripts/benchmark.py:24-40` | Le benchmark mesure `iterations` lancements complets d'un nouvel interpréteur Python (`subprocess.run([sys.executable, "-m", "laivelup.cli", ...])`) : le p50/p95 rapporté est dominé par le coût de démarrage du process, pas par la logique de scoring. | Ajouter un micro-benchmark in-process (`evaluate()` appelé directement) en complément du benchmark CLI end-to-end | S |

## Top actions

1. Batcher les appels `git` dans `generate_profile.py` — impact direct sur la latence du workflow `aidd-eval.yml` à chaque PR.

## Coverage

- **Scanned**: performance (boucles, opérations I/O, sous-processus dans `src/laivelup/*.py` et `scripts/*.py`)
- **Skipped**: no profiler, static heuristics only — pas d'outil de profiling exécutable dans cet environnement d'audit ; aucun goulot d'étranglement affirmé sans preuve de code.
