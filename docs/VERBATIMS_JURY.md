# VERBATIMS_JURY.md

> **Source de vérité (nouveau) :** retour jury verbatim + résumé vainqueur lus dans
> `C:\Users\Romy\Desktop\GoumiesLand\GoumiesCreative-Agency\hackathons\goumies-creative-laivel-up\aidd_docs\tasks\2026_08\2026_09_02_retour-jury\report.md`
> (blocs `===JURY-START===...===JURY-END===` et `===VAINQUEUR-START===...===VAINQUEUR-END===`).
> Ce fichier source est en **lecture seule** : ni copié, ni déplacé.
> Commit évalué par le jury : `7cf4f06` (2026-08-31, cf. § « État du projet évalué » du report).
>
> **Item 8 = documentation seule.** Chaque verbatim ci-dessous est tracé vers son
> traitement (`fichier:ligne` vérifié par lecture) et sa preuve (test/commande).
> Rien d'autre n'est retouché par cet item (voir § « Corrections non faites »).
>
> **H1/H2 supprimées (fausses) :** `SUJET.md` n'est plus l'hypothèse — la vraie source
> est le report jury ci-dessus. Le « résumé vainqueur » existe : c'est le bloc
> `===VAINQUEUR-START===` (@Blandine, aidd-audit), pas le pitch de soumission.

## Légende

| Colonne | Sens |
|---|---|
| Verbatim | Citation courte (1-2 phrases max) du retour jury ou du résumé vainqueur |
| Traitement | `fichier:ligne` existant vérifié (ou ADR) où le point est traité / tracé |
| Preuve | Test ou commande pour vérifier |
| Statut | `tracé` (existe déjà) / `résidu assumé` (non corrigé par l'item 8, docs seule) |

## Améliorations jury — à tracer obligatoirement

### (a) Next-steps génériques sur axe bloquant seul + repli « maintenir le niveau actuel »

| Verbatim | Traitement | Preuve | Statut |
|---|---|---|---|
| « Ta prochaine étape tient en une phrase, et seulement sur l'axe qui bloque. » | `src/laivelup/scoring.py:306` (`progress_for_axis`) + `src/laivelup/scoring.py:444` (`next_steps = progress_for_axis(limiting, ...)`) + `src/laivelup/report.py:658` (`_render_next_steps`) | `pytest tests/test_report_gaps.py -q` (19 tests) | tracé |
| « ta table n'a pas d'entrée tout en bas de la grille, donc le repli répond "maintenir le niveau actuel" » | `src/laivelup/scoring.py:340` (repli `steps.get(axe, {}).get(level, 'Maintenir le niveau actuel.')`) + `src/laivelup/report.py:939` (guide HTML, même repli) | `python -c "from laivelup.scoring import progress_for_axis; print(progress_for_axis('size','GOLD'))"` | résidu assumé — non corrigé par l'item 8 (docs seule) |

### (b) Bandeau « aucune alerte » jamais allumé + libellé à nommer

| Verbatim | Traitement | Preuve | Statut |
|---|---|---|---|
| « Ton bandeau "aucune alerte" attend un niveau déclaré qu'aucun des huit profils ne porte. » | `src/laivelup/scoring.py:272` (`detect_red_flags` : les 2 règles exigent `declared >= Level.BLUE`) + `src/laivelup/report.py:548` (bandeau `AUCUNE ALERTE` quand `red_flags` vide) | `laivelup evaluate <profil> --verbose` + ouvrir le HTML : section diagnostics | tracé |
| « Les deux règles qui le déclenchent demandent au moins Blue, et le champ est vide ou plus bas partout. » | `src/laivelup/scoring.py:278` (`if retries ... and declared >= Level.BLUE`) + `src/laivelup/scoring.py:293` (`if declared >= Level.BLUE and not ... context_versioned`) | `pytest tests/ -k "red_flag or refus" -q` | tracé |
| « Le nommer, par exemple "aucune contradiction entre déclaré et observé", le rendrait déjà lisible. » | `src/laivelup/report.py:548` (bandeau actuel `AUCUNE ALERTE`, sans ce libellé) | Relecture du HTML généré | résidu assumé — renommage non fait par l'item 8 (docs seule) |

### (c) Niveau déclaré par substring → mot entier + question du niveau

| Verbatim | Traitement | Preuve | Statut |
|---|---|---|---|
| « Le mot "redonner" donne Red. Le mot "ouvert" donne Green. » | `scripts/extract_official_profile.py:164` (`_extract_declared_level`) + `scripts/extract_official_profile.py:183` (`if word in declaratif.lower()` — substring, bug confirmé) | `python -c "from extract_official_profile import _extract_declared_level" 2>/dev/null; grep -n "if word in" scripts/extract_official_profile.py` | résidu assumé — extraction non corrigée par l'item 8 (docs seule ; script hors moteur, `team.py`/`calibrate*.py`/`scoring_defaults.py` interdits de retouche) |
| « Cherche le mot entier, et dans la réponse à la question du niveau. » | `src/laivelup/cli_interrogate.py:133` (`if re.search(rf'\b{word}\b', low)` — mot entier, déjà en place en conversation) + `src/laivelup/questions.py:14` (question `DECLARED_LEVEL`) | `pytest tests/test_interactive.py tests/test_cli_extended.py -q` | tracé (conversation OK ; extraction `extract_official_profile.py` reste en substring) |

### (d) Axe parallèle : nb dépôts comparé au seuil 3 chantiers

| Verbatim | Traitement | Preuve | Statut |
|---|---|---|---|
| « Ton axe en parallèle compare un nombre de dépôts au seuil des trois chantiers menés au bout. » | `src/laivelup/scoring.py:243` (`parallel_max`) + `src/laivelup/scoring.py:257` (`if completed_int is not None and completed_int >= 3: GOLD`) + `grille/aidd.md:45` (`"parallel": ["0", "1", "3"]`) | `python scripts/calibrate.py --expected grille/profils-officiels/expected.json --diff` | tracé |
| « Toute personne qui touche trois dépôts passe la porte. » (+ « quatre chantiers terminés pour deux branches ouvertes ») | `grille/aidd.md:93` (« mener quatre chantiers de front satisfait la case "3" » — règle officielle, minimum pas valeur exacte) + `src/laivelup/scoring.py:259` (complétude à confirmer → `GREEN` confiance basse si `projects_completed` absent) | `pytest tests/ -k "parallel" -q` | tracé — comportement conforme à la grille ; durcissement éventuel non fait par l'item 8 |

### (e) Chaîne qualité : porte 100 % moteur, auto-éval CI, diagnostic dégradé

| Verbatim | Traitement | Preuve | Statut |
|---|---|---|---|
| « Ta porte de qualité demande une couverture de 100 % sur ton moteur, mais le chemin qu'elle passe à l'outil n'en est pas un » | `.github/workflows/pr-quality-gate.yml:27` (`pytest --cov=src/laivelup.scoring` — point au lieu de slash) | Ouvrir `.github/workflows/pr-quality-gate.yml` ligne 27 | résidu assumé — workflow interdit de retouche par l'item 8 |
| « ton fichier de configuration élargit la mesure à tout le paquet. Elle se termine donc toujours à 89 %. » | `pyproject.toml:120` (`--cov=src/laivelup --cov=scripts --cov-fail-under=85`) — mesure élargie coexistante | `pytest --collect-only -q` puis lecture `coverage_report.txt` | tracé |
| « Elle n'a jamais tourné, faute de proposition de modification dans le dépôt. » | `.github/workflows/pr-quality-gate.yml:4` (`on: pull_request` — ne tourne que sur PR) | Historique CI du dépôt | tracé (constat, pas de code à changer ici) |
| « L'auto-évaluation en intégration continue s'arrête en erreur avant de poster son commentaire » | `.github/workflows/aidd-eval.yml:73` (`Evaluate AIDD` via `scripts/ci_evaluate.py`) + `scripts/ci_evaluate.py:44` (fail-fast schema `sys.exit(1)` avant commentaire) | `python scripts/ci_evaluate.py --user <handle> --out verdict.md --repo .` | tracé |
| « le diagnostic dégradé passe ses quatre profils puis sort en succès. » | `scripts/calibrate_degraded.py:215` (`--strict`, défaut gracieux) + `scripts/calibrate_degraded.py:223` (`sys.exit(1)` seulement si dossier invalide, sinon succès) + `.github/workflows/ci.yml:105` (job `calibrate-degraded`) | `python scripts/calibrate_degraded.py --official-dir grille/profils-officiels/ --expected grille/profils-officiels/expected.json --format table; echo $?` | tracé (comportement « graceful » voulu sauf `--strict`) |

### (f) Détails d'environnement : double échappement HTML + 10 tests

| Verbatim | Traitement | Preuve | Statut |
|---|---|---|---|
| « Un double échappement HTML qui affiche une apostrophe encodée à l'écran » | `src/laivelup/report.py:27` (`from html import escape`) — échappement appliqué à chaque couche (`report.py:495` evidence, `report.py:584` question, `report.py:978` glossaire) ; double application possible glossaire↔tooltip | `laivelup evaluate <profil> --out rapports` + chercher `&#x27;`/`&amp;` dans le HTML | résidu assumé — non corrigé par l'item 8 (docs seule) |
| « dix tests qui demandent ta machine : huit captures enregistrées sous Windows » | `tests/test_snapshots.py:5` (snapshots Rich) + `tests/test_snapshots.py:35` (normalisation chemins/ANSI) | `pytest tests/test_snapshots.py -q` (8 snapshots) | tracé |
| « deux qui appellent python au lieu de l'interpréteur courant. » | `tests/security/test_bandit_regression.py:25` (`['python', '-m', 'bandit', ...]` au lieu de `sys.executable`) | `grep -n "'python'" tests/security/test_bandit_regression.py` (lignes 25, 66, 105) | résidu assumé — non corrigé par l'item 8 (docs seule) |

## Points positifs jury (table séparée, bref)

| Verbatim (1 phrase) | Traitement | Preuve |
|---|---|---|
| « Tu lis la grille fidèlement. » | `src/laivelup/scoring.py:429` (`global_level = min(...)` — règle « tous les axes ou rien ») + `grille/aidd.md:91` (règle officielle) | `python scripts/calibrate.py --expected grille/profils-officiels/expected.json --diff` → 0 erreur |
| « Ta calibration se vérifie. » (extraction relancée = fichiers committés) | `src/laivelup/calibrate_core.py:59` (`run_calibration`) + `scripts/calibrate.py:24` (boucle unique réutilisée) | `python scripts/calibrate.py --expected grille/profils-officiels/expected.json --diff` |
| « Tu refuses rarement. […] Quand tu refuses, ça veut donc dire quelque chose. » (7/8 tranchés) | `src/laivelup/scoring.py:409` (`undecided_axes`/`low_conf_axes` → `scoring.py:412` `_refuse`) | `python scripts/calibrate.py --expected grille/profils-officiels/expected.json` |
| « Ton rapport HTML est autonome et agréable à lire. » | `src/laivelup/report.py:1137` (`_html_styles`, « aucun asset distant ») + `src/laivelup/report.py:1153` (`render_html`) | `laivelup evaluate <profil> --out rapports` + ouvrir le HTML hors ligne |
| « L'outillage machine est réel. » (JSON, champs, code retour, schéma) | `src/laivelup/cli.py:213` (JSON hors TTY) + `src/laivelup/cli.py:206` (`--fields` via `cli_display.py:164` `_filter_fields`) + `src/laivelup/cli.py:236` (`--fail-on`, exit 1) + `src/laivelup/cli.py:176` (`schema`) + `src/laivelup/report.py:1481` (`verdict_to_dict`) | `laivelup evaluate <profil> --json --fields level,axes --fail-on RED; echo $?` |
| « Ton typage est strict, et vérifié à chaque proposition de modification. » | `.github/workflows/pr-quality-gate.yml:20` (`mypy --strict src/`) | `mypy --strict src/` |
| « Le refus de trancher est une vraie sortie, pas un plantage. » (4 axes à blanc, encadré + 5 questions) | `src/laivelup/scoring.py:412` (`_refuse`) + `src/laivelup/report.py:752` (`_render_refusal`) + `src/laivelup/model.py:142` (`Verdict.decided`) | `laivelup evaluate <profil-peu-renseigné>` → encadré REFUS + questions |
| « ton mode conversation, qui recalcule après chaque réponse. » (barres + axe bloquant à chaque tour) | `src/laivelup/cli.py:306` (boucle `evaluate` par tour) + `src/laivelup/cli.py:344` (`_merge_answer`) + `src/laivelup/cli_interrogate.py:91` (`_merge_answer`) + `src/laivelup/cli_interrogate.py:17` (`_print_interrogate_score`) | `laivelup interrogate <profil> --max-turns 6` (6 tours, cœurs du jury) |

## Résumé vainqueur (@Blandine, aidd-audit) — couverture intégrale

Source : bloc `===VAINQUEUR-START===...===VAINQUEUR-END===` du report (lecture seule).

| Phrase du résumé (courte) | Traitement existant dans ce repo | Preuve |
|---|---|---|
| « Quand il lui manque une information, son outil le dit au lieu de mettre une mauvaise note. » | `src/laivelup/scoring.py:412` (refus + questions, jamais de zéro) + `src/laivelup/questions.py:10` (`QUESTION_IDS`, questions ciblées) + `docs/adr/0005-la-decodeuse-refus-deviner-questions-ciblees.md` | `laivelup evaluate <profil-incomplet>` → REFUS + questions ; `pytest tests/test_interactive.py -q` |
| « Il annonce précisément ce qui manque pour passer au niveau suivant » | `src/laivelup/scoring.py:306` (`progress_for_axis`) + `src/laivelup/report.py:658` (next-steps / gaps typés ✗/?) | `pytest tests/test_report_gaps.py -q` ; E2E `- ✗ …` / `- ? …` + légende MD/HTML |
| « on change toute la grille de niveaux en modifiant un seul fichier, sans toucher au code. » | `grille/aidd.md:12` (bloc `machine`, seule source) + `src/laivelup/grid_doc.py:1` (chargeur unique, refuse toute divergence) + `src/laivelup/model.py:7` (grille seule source, import échoue si incohérente) + `src/laivelup/scoring_defaults.py:26` (seuils séparés du moteur) | `python -c "from laivelup.model import GRID; print(GRID.level_ids)"` ; `pytest tests/ -k "grid or grille" -q` |
| « comment elle avait travaillé (docs, commit, architecture, harness, tests, robustesse), et c'est propre du début à la fin. » | `docs/adr/` (17 ADR, ex. `0004-grille-evaluation-4-axes-7-niveaux-seuils.md`) + `docs/architecture.mmd` + `aidd_docs/` (sessions, audits datés) + `.github/workflows/pr-quality-gate.yml:17` (ruff/mypy/bandit/pip-audit/couverture) + `QUALITY.md` + `TESTING_STRATEGY.md` | `mypy --strict src/` ; `pytest -q` (572 collectés) ; `pip-audit -r requirements.lock` (CI) |

## États / TOCTOU / vidéo-loader (sections « Améliorations détectées », « Où reste la course »)

| Verbatim (court) | Traitement | Preuve |
|---|---|---|
| « Course TOCTOU partiellement fermée dans team.py » + scénario vérification-puis-réutilisation (§ « Où reste la course ») | `src/laivelup/team.py:68` (`_is_link`) + `src/laivelup/team.py:76` (`_first_link`, ancêtres + jonctions) + `src/laivelup/team.py:148` (`_write_via_dir_fd`, E/S sur descripteur) + `src/laivelup/team.py:195` (`save_team`) — **déjà committé `b041986` (crit-1), non retouché par ce chantier** | `pytest tests/security/test_toctou_containment.py -q` ; `git show b041986 --stat` |
| « La démo vidéo tourne sans action visible : ajouter un loader lèverait l'ambiguïté » | `goumies-creative-laivel-up-demo.mp4` (1 min 53, committé `7cf4f06`) ; aucun loader — résidu assumé, non fait par l'item 8 | Lecture de la vidéo dans le dépôt |

## Traçabilité des 4 items du chantier (branche `laivelup-rebuild/socle-qualite`)

> Ajout SDLC 29/09 : chaque item ci-dessous est tracé vers son traitement
> (fichier:ligne ou décision ADR) et sa preuve (test ou commande).

| Verbatim / item | Traitement | Preuve |
|---|---|---|
| res-1 — « cli.py 738 lignes → <500, suite verte » (audit `aidd_docs/tasks/2026_08_31_audit/report.md:38`) | `src/laivelup/cli.py` (446 lignes, câblage Typer fin) + `src/laivelup/cli_display.py` (`_load_profile` via `utils.load_profile_data` canonique, `_print_verdict`, `_filter_fields`) + `src/laivelup/cli_interrogate.py` (entretien + fusion) ; shims de compat conservés ; `docs/architecture.mmd` (couches model→scoring→report→cli) | `wc -l src/laivelup/cli.py` → 446 ; `tests/test_cli.py` + `tests/test_cli_extended.py` + `tests/test_interactive.py` verts |
| res-7 — chaque règle de frontière a un test de violation délibérée | `src/laivelup/report.py` (gardes `is_relative_to` MD+HTML) + `src/laivelup/cli_display.py` + `src/laivelup/utils.py` (bornes 2 Mo) + `src/laivelup/schemas/profile.schema.json` (`additionalProperties: false` racine) + `src/laivelup/utils.py` (`slug` HMAC-SHA256 salé) + bandit (baseline) + `src/laivelup/schema.py` (`validate_profile`) + `src/laivelup/team.py` (containment, non retouché) | `tests/security/test_path_traversal.py` (+2 tests : slug `../evil` refusé, nom `../../evil` confiné) ; `test_dos_profil_giant.py` ; `test_json_injection.py` (+1 test `__proto__` isolé) ; `test_sha256_anonymization.py` ; `test_bandit_regression.py` (+1 canari B307) ; `test_toctou_containment.py` ; preuves rouge-sans-règle/vert-avec-règle au §6 du résumé SDLC |
| item 7 — écart de pratique (✗, U+2717) vs écart de preuve (?) | `src/laivelup/scoring.py:369` (`_gaps_proof`) + `src/laivelup/model.py` (`Gap.kind`, sérialisé `type`, `Verdict.gaps` sans casser `Verdict`) + `src/laivelup/report.py` (`GAP_PRACTICE_MARK`, `GAPS_LEGEND_MD`, `_render_next_steps`, refus HTML, `verdict_to_dict`) | `tests/test_report_gaps.py` (19 tests : moteur + MD + HTML + sérialisation) ; E2E `laivelup evaluate` : `- ✗ …` (perceval, décidé RED) / `- ? …` (profil-maison-1, refus) + légende MD et HTML |
| Top-action « Régénérer requirements.lock » (audit 🔴) | `requirements.lock` — **non retouché (déjà committé, interdit)** | `pip-audit -r requirements.lock` en CI |
| Résumé de soumission (pitch 3 lignes, plan §2.4, issue #47) : « refuse de trancher… Calibré à 4/4… 533 tests » | `src/laivelup/scoring.py:412` (refus) + `grille/profils-officiels/expected.json` + `src/laivelup/calibrate_core.py:59` | `python scripts/calibrate.py --expected grille/profils-officiels/expected.json --diff` → 0 erreur ; `pytest --collect-only` → 572 tests (le « 533 » du pitch est périmé) |

## Notes et hypothèses (mises à jour)

- **Source vraie (remplace H1/H2) :** le report jury `aidd_docs/tasks/2026_08/2026_09_02_retour-jury/report.md`
  (hors dépôt-worktree, lecture seule). H1 (`SUJET.md` introuvable) et H2 (« résumé vainqueur »
  introuvable) sont **supprimées** : le sujet n'est plus l'hypothèse et le résumé vainqueur
  est tracé au § ci-dessus.
- **H3 — Écart teaser vs sujet (conservé, historique).** `grille/README-OFFICIEL.md`
  (« Ça tombe juste ? / C'est solide ? / On peut le reprendre ? », page teaser du 19/08) ≠
  critères lus au plan §0 (tombés le 28/08 à midi). Les deux sont tracés ; en cas de conflit,
  le retour jury verbatim (report) fait foi pour cet item.
- **H4 — Compte de tests du pitch (conservé).** Le pitch et le § « La qualité est là ? »
  annoncent « 533 tests » ; mesure au 29/09 : **572 tests collectés** (dont 23 ajoutés par ce chantier).

## Corrections de code que l'item 8 exigerait mais non faites (item docs seule)

1. (a) next-steps par axe (4 axes + cran suivant chacun) — `scoring.py:306` — non fait : toucherait `scoring.py` (interdit).
2. (a/b) repli bas de grille + libellé « aucune contradiction entre déclaré et observé » — `scoring.py:340`, `report.py:548` — non fait : code interdit.
3. (c) extraction substring `extract_official_profile.py:183` → mot entier + question du niveau — non fait : script de calibration, hors périmètre item 8.
4. (e) porte qualité `pr-quality-gate.yml:27` (mauvais chemin coverage) — non fait : workflow interdit.
5. (e) auto-éval CI `aidd-eval.yml` / `ci_evaluate.py` (erreur avant commentaire) — non fait : workflows interdits.
6. (f) double échappement HTML `report.py` — non fait : toucherait `report.py` (interdit).
7. (f) 10 tests d'environnement (`test_snapshots.py`, `test_bandit_regression.py:25`) — non fait : tests interdits de retouche + snapshots Windows assumés.
8. Vidéo-loader — non fait : binaire démo, hors périmètre.
9. TOCTOU résiduel (§ « Où reste la course » : ancêtres/jonctions, `delete=False` si `json.dump` lève) — non fait : `team.py` déjà committé `b041986`, interdit de retouche.
