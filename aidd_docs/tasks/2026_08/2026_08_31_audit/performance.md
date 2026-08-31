# Performance Audit — goumies-creative-laivel-up

Audit du pilier « performance » du CLI Python `laivelup` (hackathon, évaluation profils créatifs). Analyse statique heuristique — aucun profiler exécutable disponible dans cet environnement.

- **Date**: 2026-08-31
- **Scope**: `src/laivelup/`, `scripts/`, `tests/` (performance uniquement)
- **Health**: good
- **Findings**: 0 critical, 3 warning, 2 minor

## Findings

| Sev | Category | Location | Issue | Suggested fix | Effort |
| --- | --- | --- | --- | --- | --- |
| 🟡 | performance | `scripts/generate_profile.py:250-257` | `generate_profile()` chaîne 7 appels `_git()` séquentiels (PR sizes, retries, branches×2, etc.) sans parallélisation — chaque `_git()` spawn un process `git` (~15-40 ms overhead). Total ~7 process séquentiels = ~100-280 ms d'overhead de spawn à chaque run CI. | Grouper les appels redondants (ex. `_detect_parallel_projects` fait 2 appels `git branch` où 1 suffirait avec post-traitement Python). EffortXS : réduire 7→5 process. | S |
| 🟡 | performance | `tests/test_team_rgpd.py:230-240` | N+1 subprocess dans le setup du test : 6 appels `subprocess.run()` séquentiels (`git init`, `git config user.email`, `git config user.name`, `git add`, `git commit`) pour initialiser un repo de test. Chaque appel spawn un process. | Utiliser un seul `subprocess.run()` avec un script shell multi-lignes, ou créer le repo via `pathlib` + un commit unique. Effort XS. | S |
| 🟡 | performance | `src/laivelup/cli.py:34-60` | Cold-start CLI : imports `typer`, `rich` (Console, Prompt, Table), + 10 modules locaux (`_completion_patch`, `calibrate_dashboard`, `encoding`, `model`, `questions`, `report`, `schema`, `scoring`, `team`) au chargement du module, même pour `--version`. Pas de lazy-loading. | Différer les imports lourds (`rich`, `calibrate_dashboard`, `team`) derrière les commandes qui les utilisent via `import` tardif dans les fonctions command. Effort M. | M |
| 🟢 | performance | `src/laivelup/scoring.py:142-190` | Aucune mémoïsation sur les fonctions pures `size_max()`, `_dominant()`, `_peak_info()` — chaque appel à `evaluate()` recalcule `Counter(pr_sizes)`. Pour le scoring unitaire c'est négligeable (O(1) sur 4 axes), mais en batch calibration (~20 profils) ou mode `interrogate` (jusqu'à 6 tours × re-scores), le même profil peut être re-score N fois. | Ajouter `@functools.lru_cache(maxsize=128)` sur les fonctions pures du scoring si un pattern de re-scoring du même profil émerge. Effort XS. Ne pas mémoïser `evaluate()` elle-même (elle mute `profile`). | S |
| 🟢 | performance | `scripts/benchmark.py:28-46` | Le mode subprocess du benchmark mesure le coût de démarrage d'un interpréteur Python (`subprocess.run([sys.executable, ...])`) plutôt que le scoring pur — le p50/p95 rapporté est dominé par le spawn process, pas par la logique métier. Le mode `--in-process` (déjà présent, lignes 64-103) corrige partiellement ce biais. | Documenter explicitement que le mode subprocess mesure l'overhead CLI complet (cold-start + scoring), pas le scoring seul. Le mode `--in-process` est déjà le bon micro-benchmark pour le scoring pur. Effort XS. | S |

## Top actions

1. **Batcher les appels git dans `generate_profile.py`** (F1) : réduire 7→5 process en fusionnant les 2 appels `git branch` dans `_detect_parallel_projects` en un seul avec post-traitement Python. Effort XS, gain net ~30-80 ms/run CI. Act-skill : `ce-work`.

2. **Défragmenter le setup test `test_team_rgpd.py`** (F2) : remplacer les 6 `subprocess.run()` séquentiels par un shell multi-lignes ou une factory de repo. Effort XS, réduit le temps de test de ~100 ms. Act-skill : `ce-work`.

3. **Lazy-imports CLI** (F3) : différer `rich`, `calibrate_dashboard`, `team` derrière les commandes concernées. Effort M, réduit le cold-start de `--version` et `--help` (~200 ms estimé). Act-skill : `ce-work`.

## Coverage

- **Scanned**: `src/laivelup/cli.py`, `scoring.py`, `report.py`, `team.py`, `encoding.py`, `_completion_patch.py`, `calibrate_core.py`, `calibrate_dashboard.py` ; `scripts/generate_profile.py`, `benchmark.py`, `demo.py`, `version_bump.py`, `calibrate.py`, `ci_evaluate.py` ; `tests/test_team_rgpd.py`, `test_scripts.py`, `test_demo.py`, `test_install_clean.py`
- **Skipped**: pas de profiler exécutable (py-spy, cProfile) dans cet environnement — analyse heuristique statique uniquement. Les chiffres « ~15-40 ms/process » sont des estimations d'ordre de grandeur, pas des mesures sur ce repo précis. Le GC report concernant « 21 subprocess calls » est **contesté** : `_detect_pr_sizes` a déjà été corrigé (1 seul `git log --shortstat` au lieu de 1+50 process), et le total réel de subprocess dans le code de production est ~7 (generate_profile) + 0 (scoring/rendering) = ~7, pas 21. Les 14 restants sont dans `tests/` (mock/subprocess d'intégration) et `scripts/version_bump.py`/`demo.py` (scripts utilitaires non critiques).
