---
title: Revue full-codebase · correctness, sécurité/RGPD, maintenabilité
date: 2026-08-24
category: code-review
modules: [cli.py, scoring.py, scoring_defaults.py, model.py, schema.py, team.py, report.py]
reviewer: Claude (méthode adaptée de ce-code-review, Consortium Goumies Creative)
scope: full-source audit (pas de git diff — accès filesystem lecture seule, pas d'exécution shell côté repo)
status: open
tags: [security, rgpd, xss, correctness, maintainability, adr-followup]
---

# Revue full-codebase · LAIVEL UP

## Méthode et limites

Revue produite sans accès `git`/shell sur le dépôt (MCP Filesystem en lecture seule) : pas de diff, pas de sub-agents parallèles, pas d'exécution de `bandit`/`pytest`. Lecture complète de `src/laivelup/*.py`, `pyproject.toml`, `tests/test_team_rgpd.py`, `tests/security/test_sha256_anonymization.py`, et croisement avec `docs/adr/0007-team-tracker-rgpd-slug-sha256.md` et `docs/adr/0010-securite-bandit-baseline-sha256-only.md`.

`correctness_review.json` (racine du repo) est **obsolète** : il décrit une fonction `_parse_reprise` dans `scoring.py` qui a été renommée `_parse_retry_ratio` et déplacée dans `cli.py`. Certaines de ses conclusions (troncature silencieuse des floats) ne correspondent plus au mécanisme réel du code actuel — voir #4 ci-dessous pour la version corrigée. À déplacer ici ou supprimer, pas de review figée à la racine.

Sévérité P0-P3 (convention `ce-code-review`) : P0 casse/exploit critique, P1 haut impact en usage normal, P2 impact modéré avec un vrai inconvénient, P3 mineur.

---

## P1 — Haute

### 1. `team.py::export_html` — pas d'échappement HTML, XSS possible via nom de membre

`export_html` interpole `m.name`, `slug`, `m.limiting_axis`, `entry["slug"]`, `entry["limiting_axis"]` bruts dans le HTML généré. Un nom de membre contenant `<script>` s'exécute dans le rapport exporté.

`report.py::render_html` fait ça correctement dans le même repo (`from html import escape`, tous les champs dynamiques sont wrappés) — l'incohérence est donc évitable, le pattern correct existe déjà à copier.

Aucun test ne couvre l'échappement : `tests/test_team_rgpd.py::TestRGPDExportSansPII::test_export_html_ne_contient_pas_pii` vérifie l'absence de `@` (PII e-mail), pas l'échappement de caractères HTML.

**Recommandation :** importer `escape` depuis `html` dans `team.py` comme dans `report.py`, wrapper tous les champs interpolés dans `export_html` (et par cohérence, vérifier `export_markdown`/`export_csv` si le format de sortie est un jour consommé par un rendu HTML/Markdown non contrôlé).

### 2. `team.py` — la protection opt-out ne survit pas à un `remove(purge=False)`

`export_markdown`, `export_html` et `export_json` filtrent l'historique via `opt_out_slugs = {s for s, m in team.members.items() if m.opt_out}`, calculé sur les membres **actuels**. Un membre qui active l'opt-out puis est retiré sans purge disparaît de `team.members` — donc son flag opt-out disparaît aussi de ce calcul. Ses entrées d'historique (conservées par design lors d'un remove sans purge, cf. docstring de `remove_member`) redeviennent exportables alors qu'il avait explicitement demandé à être exclu.

`tests/test_team_rgpd.py` teste séparément « opt-out + export » et « remove + purge », jamais la combinaison opt-out → remove(sans purge) → export.

**Recommandation :** persister le flag opt-out dans les entrées d'historique elles-mêmes (au lieu de le dériver de l'état courant de `team.members`), ou interdire `remove(purge=False)` sur un membre en opt-out (forcer `--purge` dans ce cas).

---

## P2 — Modérée

### 3. `_slug` (RGPD) — hash non salé, réversible par dictionnaire

`report.py::_slug` et `team.py::_slug` : `sha256(nom)[:8]`, sans sel. ADR-0007 documente ce choix et conclut « Irréversible (SHA-256) », en ne discutant que le risque de collision (« 8 chars = 4 billions — acceptable pour usage interne »). Ce n'est pas le bon modèle de menace : contre un espace de noms plausibles et restreint (une équipe connue, un annuaire LinkedIn), un hash non salé se casse par dictionnaire en quelques secondes — l'irréversibilité affirmée ne tient pas face à ce scénario, qui est justement le scénario réaliste pour un outil de suivi d'équipe.

`tests/security/test_sha256_anonymization.py` (5 tests) vérifie uniquement l'algorithme utilisé (SHA-256, pas MD5/SHA1), le déterminisme et le format — aucun test ne couvre la résistance à la réidentification par dictionnaire, qui est pourtant l'objectif RGPD affiché.

**Recommandation :** ajouter un sel par équipe (généré à la création, stocké côté serveur/fichier équipe, jamais exporté) ou un HMAC avec clé dédiée. Mettre à jour ADR-0007 pour refléter le vrai modèle de menace (préimage sur espace restreint, pas collision).

### 4. `scoring.py::normalize_profile` vs `_as_int` — incohérence de coercition sur les floats

`normalize_profile` valide `parallel_projects`/`projects_completed` via `int(value)` (Python tronque silencieusement un float : `int(3.7) == 3`, aucune erreur levée). `_as_int`, utilisé au moment du scoring, fait `int(str(value))` — pour `3.7` cela lève `ValueError` et retourne `None`.

Résultat : un profil avec `"parallel_projects": 3.7` passe la validation sans erreur, puis l'axe est traité comme « non fourni » au scoring (refus + question), au lieu d'un message de validation clair signalant un type invalide dès l'entrée.

*(Correction du claim de `correctness_review.json` : ce n'est pas une troncature silencieuse vers `3`, c'est une incohérence entre deux chemins de coercition différents qui aboutit à un refus déguisé en « données insuffisantes ».)*

**Recommandation :** aligner `normalize_profile` sur la même logique de coercition que `_as_int` pour que le rejet ait lieu au bon endroit, avec un message explicite (« doit être un entier, pas un nombre décimal »).

### 5. `team.py::evaluate_member` — `confidence` du snapshot = max(), pas l'axe limitant

Le snapshot stocke `confidence = max(a.confidence for a in verdict.axis_scores)`, alors que le niveau global est décidé par l'axe **plancher** (`min()`, règle AND documentée dans `scoring.py`). Un membre peut afficher 90 % de confiance dans l'export équipe alors que l'axe qui a réellement fixé son niveau était à 55 %, tout juste au-dessus du seuil de refus (0.5) — métrique trompeuse pour quiconque lit ce seul chiffre dans l'export.

**Recommandation :** reporter la confiance de l'axe `verdict.limiting_axis`, pas le max toutes confidences confondues.

### 6. Couplage fragile entre le texte des questions (`scoring.py`) et leur parsing (`cli.py`)

`cli.py::_merge_answer` route les réponses libres par matching de sous-chaînes (`"jusqu'au bout" in question`, `"chantiers" in question`, `"peux-tu fournir" in question`...) contre le texte exact généré par `scoring.py::_questions_for`. Aucune constante partagée, aucun test qui verrouille l'invariant « si le texte change dans un fichier, le parsing suit dans l'autre ». Un changement de formulation dans un seul des deux fichiers casse silencieusement le merge de réponse (pas d'exception levée, juste une trace jamais mise à jour).

**Recommandation :** extraire des identifiants de question stables (constantes partagées entre `scoring.py` et `cli.py`) plutôt que du matching sur texte libre destiné à l'affichage.

---

## P3 — Faible

### 7. `cli.py::_merge_answer` — branche morte

`"menés au bout" in question` : la seule question de complétion générée (`scoring.py`) contient `"jusqu'au bout"`, jamais `"menés au bout"` comme sous-chaîne contiguë (`"menés jusqu'au bout"` ne contient pas `"menés au bout"`). Branche morte, sans impact actuel car `"jusqu'au bout"` capte déjà le cas.

**Recommandation :** supprimer la clause ou documenter qu'elle anticipe une formulation future.

### 8. `cli.py::_parse_retry_ratio` — frontière ambiguë à exactement `"1"`

`"1"` → `1.0` (ratio 100 %), cohérent avec la règle documentée (« ≤1 = ratio brut, >1 = pourcentage »), mais ambigu du point de vue utilisateur (« j'ai repris 1 fois » pourrait vouloir dire autre chose qu'un ratio de 100 %). Design assumé, faible confiance qu'il s'agisse d'un vrai bug plutôt que d'un choix documenté.

**Recommandation (optionnelle) :** clarifier dans le message de question ou METHODE.md.

### 9. `_slug` dupliqué à l'identique dans `report.py` et `team.py`

**Recommandation :** extraire dans un module commun (`utils.py` ou similaire).

### 10. `team.py::export_json` — filtrage de l'historique en O(n×m), style incohérent

`any(team.members[s].opt_out for s in team.members if s == h.get("slug"))` reproduit avec une complexité et un style différents ce que `opt_out_slugs = {...}` fait proprement dans `export_markdown`/`export_html`.

**Recommandation :** réutiliser le même pattern `opt_out_slugs` dans les trois fonctions d'export.

---

## Couverture / non vérifié

- Pas de `AGENTS.md`/`CLAUDE.md` à la racine → pas de lens *project-standards* appliquée.
- `scripts/` (calibrate.py, generate_profile.py, apply_calibration_fix.py), `.github/workflows/`, `docs/adr/0001-0016` (hors 0007/0010) non lus en détail.
- `tests/security/test_json_injection.py`, `test_path_traversal.py`, `test_dos_profil_giant.py`, `test_bandit_regression.py`, `bandit-baseline.json` non lus — probable que bandit (ADR-0010) ne couvre pas la classe de bug #1 (injection HTML via interpolation de chaîne brute) : bandit cible surtout `eval`/`subprocess`/crypto faible/secrets en dur, pas l'échappement HTML dans du code non-templating. À vérifier en exécutant bandit localement.
- Pas d'accès `git log`/`git blame` → impossible de dater ces findings par rapport à l'historique de commits, ni de savoir si certains sont déjà en cours de traitement.

## Verdict

**Prêt avec correctifs.** Rien de bloquant en soi (pas de RCE, pas d'injection SQL). #1 et #2 touchent directement les deux promesses affichées du projet (transparence/souveraineté et conformité RGPD) et sont corrigibles en quelques lignes chacun — à traiter avant toute démo où l'export équipe serait partagé. #3 mérite en plus une mise à jour d'ADR, pas seulement un correctif de code.
