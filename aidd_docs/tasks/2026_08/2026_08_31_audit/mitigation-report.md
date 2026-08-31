# Rapport de mitigation — Audit 2026-08-31

## Résumé exécutif

6 fixes appliqués + 1 test corrigé + validation CE (3 personas). Tous les tests passent (hors snapshots pré-existants).

| Fix | Description | Statut | Fichiers |
|-----|-------------|--------|----------|
| Fix 0 | Test `test_scoring_edge.py` — clé `XXcontext_versionedXX` | ✅ | tests/test_scoring_edge.py |
| Fix 1 | TOCTOU symlink team.py — check conservé | ✅ | src/laivelup/team.py |
| Fix 2 | requirements.lock régénéré | ✅ | requirements.lock |
| Fix 3 | Extraction team_cli.py depuis cli.py | ✅ | team_cli.py, console.py, cli.py |
| Fix 4 | Centralisation LEVEL_COLORS + load_profile_data | ✅ | model.py, utils.py, report.py, calibrate_dashboard.py, calibrate_core.py, scripts/calibrate.py |
| SEC-001 | Garde taille + validation dans load_profile_data() | ✅ | src/laivelup/utils.py |
| Archi | Lazy import calibrate_dashboard | ✅ | src/laivelup/cli.py |

## Validation CE

| Persona | Verdict | Top finding corrigé |
|---------|---------|---------------------|
| ce-security-reviewer | FIX-FIRST → SHIP (après SEC-001) | load_profile_data() sans garde taille → corrigé |
| ce-architecture-strategist | FIX-FIRST | cli.py 786l (>500l) — résidu documenté |
| ce-maintainability-reviewer | SHIP | Duplication réduite, 3 résidus mineurs |

## Impact sur les scores GC

| Métrique | Avant | Après |
|----------|-------|-------|
| cli.py lignes | 985 | 752 (-24%) |
| Modules >500l | 3 (cli, report, test_cli_extended) | 2 (cli, report) |
| Duplication LEVEL_COLORS | 2 copies | 1 (canonical dans model.py) |
| Duplication _load_profile | 3 copies | 2 (cli.py + utils.py) |
| Tests monkeypatch | 4 ciblaient cli | 4 ciblent team_cli |
| Tests | 384+ passent | 384+ passent |

## Résidus documentés

1. **cli.py à 752l** — au-dessus du seuil 500l. Prochaine étape : extraire `nes_rendering.py` (~180l)
2. **report.py à 1039l** — inchangé. Extraction de templates HTML recommandée
3. **calibrate.py duplique calibrate_core.py** — à migrer vers `run_calibration()`
4. **encoding.make_console** — code mort, à supprimer
5. **Snapshots** — 1 snapshot test pré-existant (wording changé), à mettre à jour avec `--snapshot-update`
