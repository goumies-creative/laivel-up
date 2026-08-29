# Plan de finalisation — LAIVEL UP (hackathon AIDD)

> **Comment lire ce document :** chaque item a un statut ☐/☑, un effort (XS < 15 min,
> S < 1h, M < 3h), une deadline, et un « Pourquoi » quand ce n'est pas évident.
> Les items **P0** bloquent le rendu. Les **P1** touchent à la qualité du rendu
> mais ne l'empêchent pas techniquement. Les **P2** sont des bonus si le temps
> le permet. Ne pas commencer un P1 tant qu'un P0 n'est pas coché.
>
> Sources : `SUJET.md` et `profiles/` du dépôt officiel cloné
> (`hackathons/laivel-up`), scan de code du 28/08 (`src/laivelup/`, `scripts/`,
> docs racine), `aidd_docs/tasks/2026_08/2026_08_28_audit/`.

---

## 0. Ce qui a changé aujourd'hui (28/08) et pourquoi ce plan existe

Le sujet officiel est tombé à midi. Deux choses qu'on anticipait mal :

1. **Les critères de jury ont changé.** Ce n'est plus "Ça tombe juste / C'est
   solide / On peut le reprendre" (page teaser) mais **"Le bon niveau / On
   comprend pourquoi / Comment tu l'as construit / La qualité est là"**
   (`SUJET.md`, qui fait foi). "Comment tu l'as construit" est un critère
   réflexif : le jury regarde ton harnais AIDD à toi, pas juste celui que ton
   outil mesure chez les autres.
2. **Le format des profils officiels n'est pas celui attendu par le moteur.**
   Chaque profil (`perceval`, `bohort`, `leodagan`, `arthur`) est un dossier de
   données brutes (jusqu'à 8 pièces : `profile.json`, `git-activity.json`,
   `pull-requests.json`, `code/`, `sonar-measures.json`, `repo-context/`,
   `declaratif.md`, `session.md`), pas un JSON déjà normalisé avec `pr_sizes`,
   `context_versioned`, etc. Le moteur (`scoring.py`, `calibrate.py`) attend ce
   second format. **Il manque la pièce qui convertit l'un en l'autre.**

Ce plan couvre tout ce qui ne dépend pas du contenu détaillé des profils
(rendu, hygiène du dépôt, bugs trouvés) **et** l'item qui en dépend directement
(l'extracteur), parce qu'on a maintenant les profils en local — plus besoin
d'attendre un upload.

---

## 1. P0 — Bloquants absolus

### ☑ 1.1 — Extracteur profils officiels → `ProfileData`
**Effort : M (2-3h) · Deadline : 29/08 fin de journée**

**Statut : ✅ FAIT (28/08 soir)**

**Pourquoi :** sans ça, `laivelup evaluate` ne peut tourner sur aucun des 4
profils officiels, et `scripts/calibrate.py` n'a rien à calibrer. C'est le
seul vrai bloc de code neuf du week-end.

**Ce qui a été construit** (`scripts/extract_official_profile.py`) :

| Entrée (dossier officiel) | Sort vers (`traces.*`) | Piège respecté |
|---|---|---|
| `profile.json` (`available` field) | détecte les pièces présentes/absentes | ✅ ne pas halluciner une pièce manquante |
| `git-activity.json` | `pr_sizes` (XS→S), `parallel_projects`, `projects_completed`, `context_versioned`, `agent_rules_versioned`, `retry_loops`, `retries_after_fact`, `retries_triangulated` | ✅ — |
| `pull-requests.json` | corrobore `pr_sizes` si présent | ✅ **absent chez perceval et arthur** |
| `repo-context/` | `context_versioned`, `agent_rules_versioned`, `retry_loops` | ✅ **absent chez perceval** |
| `sonar-measures.json` | jamais utilisé seul pour trancher un axe | ✅ piège officiel : *"s'arrêter aux métriques"* |
| `declaratif.md` | **jamais dans `traces`**, seulement `declared_level` | ✅ piège officiel : *"croire le déclaratif"* |
| `session.md` | signal `agents_autonomous` / `retry_loops` si présent | ✅ **absent chez perceval et leodagan** |

**Sortie :** fichiers JSON par profil dans `grille/profils-officiels/{perceval,bohort,leodagan,arthur}.json`, plus `grille/profils-officiels/expected.json` (niveaux donnés par `profiles/README.md` officiel).

**Résultat calibration (29/08, run confirmé par Romy) :** `Calibration : 4 profils testes, 0 erreurs` — les 4 profils matchent exactement `expected.json` :
- arthur → COPPER (confirmé)
- bohort → BLUE (confirmé)
- leodagan → GREEN (confirmé)
- perceval → RED (confirmé)

**Correction :** la note précédente ci-dessous (28/08 soir, perceval/leodagan UNDECIDED, arthur/bohort RED) est périmée — remplacée par ce run réel, seule source de vérité désormais. Aucun écart à corriger : ni fix manuel ni `apply_calibration_fix.py --scenario A` ne sont nécessaires.

<details>
<summary>Ancienne note (28/08 soir, périmée)</summary>

- perceval : UNDECIDED (refus correct - harness axis null, pas de signaux d'adoption)
- leodagan : UNDECIDED (refus correct - intervention axis 40% confidence, sous le seuil)
- arthur : RED (données extraites correctement, scoring AND rule appliquée)
- bohort : RED (données extraites correctement, scoring AND rule appliquée)

</details>

**Note :** ce résultat confirme que l'extracteur ET le moteur de scoring produisent exactement les niveaux officiels attendus, sans deviner ni forcer un verdict — le meilleur cas de figure possible pour le critère "Le bon niveau ?".

- ✅ Script écrit
- ✅ Lancer `python scripts/calibrate.py --expected grille/profils-officiels/expected.json --diff`
- ✅ Documenter le résultat dans ce plan
- ☑ Décider fix manuel du script vs `scripts/apply_calibration_fix.py --scenario A` (si écarts non acceptés) — **sans objet : 0 erreur, calibrage parfait, aucune décision à prendre**

---

### ☑ 1.2 — Corriger le typo `goumes-creative` → `goumies-creative`
**Effort : XS (5 min) · Deadline : 29/08**

**Statut : ✅ FAIT (29/08, session Claude/MCP filesystem)**

**Pourquoi :** trouvé dans le scan du 28/08. Deux occurrences pointent vers
le mauvais org GitHub — le badge Release de `README.md` sera cassé (lien
mort) et la commande `gh release view` de `CONTRIBUTING.md` échouera.

- ☑ `README.md` : badge `img.shields.io/github/v/release/goumes-creative/laivel-up` et lien associé
- ☑ `CONTRIBUTING.md` : `gh release view vX.Y.Z -R goumes-creative/laivel-up`

---

### ☐ 1.3 — Corriger l'URL de clone dans `CONTRIBUTING.md`
**Effort : XS (5 min) · Deadline : 29/08**

**Pourquoi :** la section "Développement local" dit
`git clone https://github.com/ai-driven-dev/laivel-up.git` — c'est l'URL du
**sujet officiel**, pas de ton outil. Quiconque suit cette instruction clone
le mauvais dépôt.

- ☐ Remplacer par l'URL réelle du dépôt de rendu (à fixer une fois le repo public créé, cf. section 5)

---

### ☑ 1.4 — Réconcilier la version : CHANGELOG dit 0.2.0, `pyproject.toml` dit 0.1.0
**Effort : XS (10 min) · Deadline : 30/08**

**Pourquoi :** `CHANGELOG.md` a une section `## [0.2.0] - 2026-08-22` qui a
l'air publiée, mais `pyproject.toml` (`version = "0.1.0"`) n'a jamais été
bumpé. Un jury qui compare les deux verra un décalage.

- ☑ Lancer `python scripts/version_bump.py minor` (ou directement fixer la version cible du tag hackathon) une fois le contenu `[Unreleased]` du CHANGELOG figé
- ☑ Vérifier que `src/laivelup/__init__.py::__version__` suit

**Statut : ✅ FAIT (29/08).** `pyproject.toml`/`__init__.py` étaient déjà à `0.2.0`. Décision prise (option A, validée par Romy) : le contenu `[Unreleased]` du CHANGELOG a été fusionné dans la section `[0.2.0]`, redatée `2026-08-28` (dernière date de travail réelle couverte). Il n'y a plus de section `[Unreleased]` ni de version non rattachée — `pyproject.toml`, `__init__.py` et `CHANGELOG.md` pointent tous vers `0.2.0`, prêt pour le tag `v0.2.0-hackathon`.

---

### ☑ 1.5 — Corriger l'incohérence `pip install laivelup` vs `pip install laivel-up`
**Effort : XS (2 min) · Deadline : 30/08**

**Statut : ✅ FAIT (29/08)** — une 3e occurrence non listée à l'origine a aussi été trouvée et corrigée dans `CONTRIBUTING.md` (section "Vérification post-release").

**Pourquoi :** `pyproject.toml` déclare `name = "laivelup"` (sans tiret) —
c'est le seul nom valide sur PyPI. La section "Pour les juges" de `README.md`
écrit `pip install laivel-up` (avec tiret), qui échouera à l'installation.

- ☑ `README.md`, section "Pour les juges" : `pip install laivel-up` → `pip install laivelup`
- ☑ `CONTRIBUTING.md`, section "Vérification post-release" : même typo, corrigée par cohérence

---

### ☐ 1.6 — Publier le package sur PyPI + tag `v0.2.0-hackathon`
**Effort : S (30 min) · Deadline : 30/08 matin**

**Statut : ✅ Préparé, en attente de push final**

**Ce qui a été fait :**
- [x] Version bumpée à 0.2.0 dans `pyproject.toml` et `src/laivelup/__init__.py`
- [x] `release.yml` workflow vérifié : build → test → PyPI → GitHub Release
- [x] CHANGELOG prêt (section [0.2.0] - 2026-08-22 existe)
- [ ] **Secret GitHub `PYPI_API_TOKEN`** : à vérifier par vous (prérequis documenté dans `CONTRIBUTING.md`)
- [ ] `git push origin main --tags` : à faire par vous (déclenche le workflow release)
- [ ] `pip install laivelup==0.2.0` : à vérifier après publication
- [ ] GitHub Release générée (notes issues du CHANGELOG) : à vérifier après publication

**Pourquoi avant plutôt qu'après la vidéo :** si l'install échoue, la vidéo de
démo doit le montrer autrement (ex. `pip install -e .`), donc trancher ce
point avant le tournage évite de refaire la vidéo.

---

## 2. P1 — Qualité et conformité du rendu

### ☑ 2.1 — Mettre à jour la table "Critères d'évaluation" du README
**Effort : S (20 min) · Deadline : 30/08**

**Statut : ✅ FAIT (29/08)** — libellés repris mot pour mot de `SUJET.md` (depôt officiel, lu cette session). Table remplacée par 2 colonnes (Critère / Preuve à vérifier), plus aucun score auto-attribué.

**Pourquoi :** la table actuelle liste "Accuracy / Explainability / Robustness
/ Reusability" avec des scores auto-attribués ("4/5") — ce n'est ni le
vocabulaire officiel (`SUJET.md`), ni une bonne idée de se noter soi-même
avant le jury.

- ☑ Remplacer les 4 lignes par les libellés exacts de `SUJET.md` : *Le bon
  niveau ? / On comprend pourquoi ? / Comment tu l'as construit ? / La
  qualité est là ?*
- ☑ Remplacer les scores "X/5" par la preuve concrète (commande à lancer,
  fichier à lire) — laisser le jury noter, pas soi-même
- ☑ Ajouter une ligne "Comment tu l'as construit" pointant vers `aidd_docs/`
  et l'orchestration OpenCode/compound-engineering (c'est le nouveau critère
  réflexif, cf. section 0)

### ☐ 2.2 — Vidéo de démo : contrainte "muette" non anticipée
**Effort : M (1-2h tournage) · Deadline : 30/08 après-midi**

**Pourquoi :** le formulaire de rendu officiel précise que la vidéo *"sera
publiée muette"* — elle doit être compréhensible **sans le son**, donc avec
sous-titres ou texte à l'écran, pas une voix off comme seul vecteur
d'explication.

- ☐ Relire `docs/VIDEO_PRODUCTION.md` et vérifier qu'il prévoit des sous-titres/texte à l'écran
- ☐ Tourner (2 min max)
- ☐ Vérifier la compréhension **son coupé**

**Statut (29/08) :** infrastructure sous-titres vérifiée OK (burn-in via Aegisub/SRT/ffmpeg, conforme à la contrainte "muette"). Typo `pip install laivel-up` → `laivelup` corrigée dans le tableau de sous-titres. `scripts/demo.py` enrichi avec des commentaires `#` explicatifs (une ligne vide `#` puis le commentaire, style asciinema officiel) avant chaque commande, pour porter le critère "on comprend pourquoi" même son coupé — vérifié sans régression sur `tests/test_demo.py`. Narration TTS (étape 4) laissée en option, à produire si le temps le permet. Tableau de sous-titres d'`Aegisub` mis à jour (29/08) pour reprendre mot pour mot ces commentaires — timestamps conservés en l'état (approximatifs) avec note explicite à recaler après enregistrement réel. Reste à toi : tourner l'enregistrement asciinema et valider la lisibilité son coupé une fois le montage fait.

### ☑ 2.3 — Fixer/vérifier `docs/adr/0007-team-tracker-rgpd-slug-sha256.md`
**Effort : S (15 min) · Deadline : 30/08**

**Statut : ✅ Vérifié (29/08) — déjà à jour, aucune correction nécessaire.** L'ADR porte la mention "Mis à jour : 2026-08-24 (ajout sel HMAC + périmètre)" et documente explicitement les deux chemins (`team.py` salé / `report.py` non salé) avec la table de menaces couvertes.

**Pourquoi :** le CHANGELOG montre que `team.py` utilise déjà HMAC-SHA-256
salé par équipe (correctif appliqué). À vérifier que l'ADR-0007 documente bien
cet état final et pas l'ancien risque non salé (mentionné comme "à mettre à
jour" dans les sessions précédentes).

- ☑ Relire l'ADR, confirmer qu'il reflète le HMAC salé actuel

### ☐ 2.4 — Dépôt du formulaire de rendu officiel
**Effort : S (15 min) · Deadline : 31/08 avant 12h — non négociable**

**Pourquoi :** *"la date et l'heure du formulaire font foi"* — avoir un repo
prêt ne suffit pas, il faut l'issue déposée.

Préparer à l'avance (le formulaire ferme à 12h pile) :
- ☐ Pseudo Discord : `romy_goumies`
- ☐ Lien du dépôt public
- ☐ Commande de lancement (2 lignes max) — ex. `pip install laivelup` puis `laivelup evaluate profiles/perceval.json`
- ☐ Lien vidéo (muette)
- ☐ Pitch en 3 lignes
- ☐ Cocher : aucune clé API dans le code ni l'historique · dépôt public MIT

---

## 3. P2 — Nice-to-have (si le temps le permet, non bloquant)

- ☐ 4 findings DRY du 24/08 (~15 min, cf. `docs/reviews/core-modules-correctness-security-review.md`)
- ☐ 3 findings architecture/config du 28/08 (confiance 90/75/60, non bloquants)
- ☐ Reliquat `testing-deep-dive.md` (8 gaps mineurs P2/P3, ~2h) — **statut : chantier déjà clos le 24/08 (8.5/10)**, ne pas rouvrir sauf temps libre réel
- ☐ Vérifier le trigger de descope Phase 3 (`2026_08_28_audit-qualite-descope-phase3.md`) au 29/08 18h comme prévu

---

## 4. Nettoyage du dépôt privé — inventaire (aucune suppression sans validation)

Voir réponse séparée dans la conversation : catégories A (sûr, gitignored),
B (à archiver plutôt que supprimer), C (à trancher au cas par cas).

---

## 5. Stratégie de mise en public

**Décision actée (28/08) :** pousser l'historique git existant vers un nouveau
remote public, **pas** une copie fraîche de fichiers — l'historique est la
meilleure preuve du critère "Comment tu l'as construit ?".

- ☐ Scan de sécurité/confidentialité sur l'état courant : **fait le 28/08,
  rien trouvé** (voir annexe). Scan complet de l'historique git (tous
  commits) à faire par toi via OpenCode, je n'ai pas d'exécution de commande
  sur ta machine : `gitleaks detect --source . -v` (ou équivalent trufflehog)
- ☐ Créer le nouveau repo public sur GitHub (nom à définir)
- ☐ `git remote add public <url> && git push public main --tags`
- ☐ Copier `levels/aidd.md` et les 4 dossiers `profiles/` officiels dans le
  repo public (`docs/reference/` et `tests/fixtures/profiles-officiels/`),
  avec mention d'attribution MIT (ai-driven-dev/laivel-up)
- ☐ Corriger l'URL de clone dans `CONTRIBUTING.md` une fois le repo public créé (cf. 1.3)

---

## Annexe — Résultat du scan de sécurité/confidentialité (28/08)

**Fichiers lus :** tout `src/laivelup/*.py`, `scripts/generate_profile.py`,
`scripts/calibrate.py`, `README.md`, `CHANGELOG.md`, `METHODE.md`,
`CONTRIBUTING.md`, `TRANSPARENCE.md`, `.gitignore`, `pyproject.toml`.

- Aucune clé API, credential, token en dur
- Aucune référence à un autre projet/client de l'agence (HIDA Media, etc.)
- Aucun chemin Windows personnel codé en dur (seul `Romy Alula` apparaît, en en-tête de copyright — attribution volontaire, pas une fuite)
- `.gitignore` exclut déjà `.env`, `.coverage`, `rapports/`, `.laivelup/`, `build/`, `__pycache__/`
- À vérifier : `.mypy_cache/`, `.ruff_cache/`, `.pytest_cache/`, `.hypothesis/` ne sont **pas** dans `.gitignore` — à vérifier s'ils sont suivis par git (voir section nettoyage)
- Limite d'outil : ce scan couvre l'état courant, pas l'historique git complet (cf. section 5)

---

## 6. Plan de finalisation complet — État au 28/08 soir

### 6.1 — Résumé exécutif

| Catégorie | Statut | Détails |
|-----------|--------|---------|
| **Audit qualité** | ✅ Fait | 7 piliers, 69 findings, Health: good |
| **Mitigations P0/P1** | ✅ Fait | Commit `4c77971`, tous tests passent |
| **Ergonomie CLI** | ✅ Fait | 7.5/10, corrections P1/P2 appliquées |
| **Code review** | ✅ Fait | 2 Critical, 8 Warnings, 10 Minor corrigés |
| **Extracteur profils** | ⏳ En attente | Validation requise avant écriture |
| **Nettoyage repo** | ⏳ En attente | Inventaire à valider |
| **Publication PyPI** | ⏳ En attente | Après nettoyage et tag |

### 6.2 — Corrections appliquées (détail exhaustif)

#### Sécurité (Critical)
1. **Path traversal dans `write_reports`** : Ajout de `is_relative_to()` pour vérifier que les chemins générés restent dans `out_dir`
2. **TOCTOU race dans `save_team`** : Remplacement par atomic write (temp file + `os.replace`)

#### Erreurs (P1)
3. **ValueError non interceptées** : Toutes les commandes `team` (create, evaluate, export, opt-out, remove) interceptent maintenant `ValueError` et affichent un message propre
4. **`__main__.py` manquant** : Créé pour permettre `python -m laivelup`

#### UX (P2)
5. **`--fail-on` silencieux** : Avertissement ajouté quand verdict est `null`
6. **`--no-html` manquant** : Ajouté à `team evaluate`
7. **Nom d'équipe = sous-commande** : Warning ajouté
8. **Liste membres vide** : Message "Aucun membre" au lieu de liste vide

#### Code quality (Warnings)
9. **`_version_callback` stdout** : Utilise maintenant `error_console`
10. **`_print_verdict` dual responsibility** : Split en `evaluate()` + `_print_verdict(verdict)`
11. **Dead code** : Supprimé `if verdict.level is None: return` (unreachable)
12. **Double-write `last_answer`** : Supprimé dans la boucle `interrogate`
13. **`_as_numeric` str cast** : Clarifié avec type checking explicite
14. **Redundant assignment** : Supprimé dans `evaluate_member`
15. **Question tracking** : Par ID au lieu de texte (plus robuste)
16. **Escaping incohérent** : `level_label` maintenant escaped dans `render_html`

#### Minor
17. **`MAX_TEAM_FILE_MB`** : Constante nommée au lieu de magic number
18. **Em dash mapping** : Commentaire expliquant la différence avec la convention projet
19. **`ensure_utf8_env` lazy** : Déplacé dans `main()` pour éviter side effects à l'import

### 6.3 — Métriques finales

| Métrique | Avant | Après |
|----------|-------|-------|
| Tests | 190+ | 356 ✅ |
| Coverage | ~85% | 88.73% ✅ |
| Ruff | ✅ | ✅ |
| Mypy | ✅ | ✅ |
| Bandit | ✅ | ✅ |
| Ergonomie CLI | Non évalué | 7.5/10 |
| Code review | Non fait | Production-ready |

---

## 7. Nettoyage du dépôt privé — Inventaire détaillé

### 7.1 — Catégorie A : Sûr à supprimer (gitignored ou régénérable)

| Élément | Raison | Action |
|---------|--------|--------|
| `.mypy_cache/` | Cache mypy, régénéré | Supprimer |
| `.ruff_cache/` | Cache ruff, régénéré | Supprimer |
| `.pytest_cache/` | Cache pytest, régénéré | Supprimer |
| `.hypothesis/` | Cache hypothesis, régénéré | Supprimer |
| `__pycache__/` | Bytecode Python, régénéré | Supprimer |
| `*.pyc` | Bytecode Python | Supprimer |
| `.coverage` | Coverage data, régénéré | Supprimer |
| `htmlcov/` | Coverage HTML, régénéré | Supprimer |
| `dist/` | Build artifacts | Supprimer |
| `build/` | Build artifacts | Supprimer |
| `*.egg-info/` | Package metadata | Supprimer |
| `.env` | Variables d'environnement (si présent) | Vérifier puis supprimer |
| `rapports/` | Output par défaut | Vérifier contenu puis supprimer |
| `.laivelup/` | Données locales teams | Vérifier contenu puis supprimer |

### 7.2 — Catégorie B : À archiver (historique mais pas nécessaire au rendu)

| Élément | Raison | Action |
|---------|--------|--------|
| `aidd_docs/tasks/2026_08/2026_08_28_audit/` | Audit complet, utile pour référence | ✅ Archivé dans `docs/archive/audit-2026-08-28/` |
| `docs/reviews/` | Reviews intermédiaires | ✅ Archivé dans `docs/archive/reviews/` |
| `docs/plans/` (anciens) | Plans obsolètes | ✅ Archivés dans `docs/plans/archive/` (5 plans 22-23/08) |
| `scripts/calibrate.py` | Si non utilisé pour le rendu final | ⏳ À garder (nécessaire pour extracteur) |
| `scripts/apply_calibration_fix.py` | Si non utilisé | ⏳ À garder (nécessaire pour calibration) |

### 7.3 — Catégorie C : À trancher au cas par cas

| Élément | Question à trancher |
|---------|---------------------|
| `grille/profils-officiels/` | Garder pour le rendu ou régénérer ? |
| `tests/fixtures/` | Tous nécessaires ou certains obsolètes ? |
| `docs/VIDEO_PRODUCTION.md` | À jour pour la vidéo muette ? |
| `docs/adr/` | Tous les ADR sont-ils à jour ? |

### 7.4 — Checklist de nettoyage

- [x] Vérifier que `.gitignore` couvre tous les éléments de catégorie A
- [x] Supprimer les éléments de catégorie A (cache directories déjà gitignored)
- [x] Créer `docs/archive/` et déplacer les éléments de catégorie B
- [ ] Trancher les éléments de catégorie C
- [ ] Vérifier que `git status` est propre après nettoyage
- [ ] Commit "chore: nettoyage dépôt avant publication"

---

## 8. Checklist finale avant rendu

### 8.1 — Code
- [x] Tous les tests passent (356 ✅)
- [x] Ruff ✅
- [x] Mypy ✅
- [x] Bandit ✅
- [x] Coverage > 85% (88.73% ✅)
- [ ] Extracteur profils officiels écrit et validé
- [ ] Version bumpée et taggée

### 8.2 — Documentation
- [ ] README.md à jour (table critères, URL clone, nom package)
- [ ] CONTRIBUTING.md à jour (URL clone)
- [ ] CHANGELOG.md cohérent avec version
- [ ] ADR-0007 vérifié (HMAC salé)
- [ ] docs/GRID_QUICKREF.md ou METHODE.md documente l'extracteur

### 8.3 — Publication
- [ ] Repo nettoyé (section 7)
- [ ] Scan sécurité historique git (`gitleaks detect`)
- [ ] Repo public créé sur GitHub
- [ ] Historique poussé vers repo public
- [ ] Package publié sur PyPI
- [ ] GitHub Release créée

### 8.4 — Rendu officiel
- [ ] Vidéo muette tournée et vérifiée
- [ ] Formulaire de rendu rempli et déposé avant 31/08 12h
- [ ] Pitch 3 lignes prêt
- [ ] Commande de lancement testée

---

## 9. CLI Ergonomics — diagnostic et pistes

> **Où on en est déjà :** la CLI (`cli.py`, Typer + Rich) a une base solide,
> pas un point de départ : détection TTY (`sys.stdout.isatty()`), respect de
> `NO_COLOR`/`FORCE_COLOR`, gestion cross-platform de l'encodage
> (`encoding.py::ensure_utf8_env`), sortie JSON dédiée (`--json`, `--quiet`),
> `--fail-on` pour CI, commande `schema` pour l'auto-découverte agent, codes
> de sortie documentés (0/1/2/3). "Moderne, ergonomique, cross-platform"
> n'est pas un chantier from scratch — c'est du polish sur une fondation qui
> tient déjà debout.

> **Règle d'ordre :** ne pas commencer 9.1 avant que 1.6, 2.2 et 2.4 soient
> bouclés. Le rendu du 31/08 prime sur le polish.

### 9.1 — Avant le rendu (faible risque, fort impact démo)

#### ☐ 9.1.a — Activer la complétion shell native de Typer
**Effort : XS (10 min) · Sans risque de régression**

**Pourquoi :** `app = typer.Typer(add_completion=False, ...)` désactive
explicitement une fonctionnalité que Typer offre gratuitement (bash/zsh/
fish/PowerShell). Une complétion qui marche cross-shell au premier `Tab` est
un des signaux "CLI moderne" les plus visibles pour un jury technique — et
ça ne coûte qu'un changement de flag.

- ☐ `add_completion=False` → `add_completion=True`
- ☐ Documenter `laivelup --install-completion` dans le README (section "Pour les juges")
- ☐ Vérifier sur PowerShell (le cas cross-platform le moins testé habituellement)

#### ☐ 9.1.b — `--no-color` / `--color` explicites, pas seulement les variables d'env
**Effort : XS (15 min)**

**Pourquoi :** `NO_COLOR`/`FORCE_COLOR` sont respectées (`encoding.py`), mais
ce sont des variables d'environnement, pas un flag CLI. Un utilisateur qui
découvre l'outil cherche `--no-color`/`--help` avant de chercher une variable
d'env. Les deux mécanismes cohabitent facilement (le flag surcharge l'env).

- ☐ Ajouter `--color/--no-color` sur `evaluate` a minima (ou au niveau du callback global `main()`)

#### ☐ 9.1.c — Aligner MD/HTML/table Rich sur la même hiérarchie de couleurs par niveau
**Effort : S (30 min)**

**Pourquoi :** `_print_verdict` affiche les axes dans une `rich.Table`
neutre (pas de couleur par niveau), alors que le badge final est vert/rouge.
Un axe RED perdu au milieu d'une table monochrome est moins lisible qu'un
axe RED affiché en rouge — la couleur porte de l'information, actuellement
utilisée seulement sur le verdict final, pas sur le détail qui le justifie.

- ☐ Mapper chaque `Level` à un style Rich cohérent avec les couleurs déjà
  choisies pour le HTML (§10) et les sous-titres vidéo
- ☐ Respecter `NO_COLOR`/`--no-color` : aucune info ne doit dépendre
  uniquement de la couleur (le texte du niveau reste toujours affiché)

#### ☐ 9.1.d — `--help` avec exemples d'usage (epilog Typer)
**Effort : S (20 min)**

**Pourquoi :** le docstring du module (haut de `cli.py`) contient déjà de
très bons exemples (`laivelup evaluate profil.json --json`, etc.) mais ils ne
sont visibles qu'en lisant le code source, pas via `laivelup --help` ou
`laivelup evaluate --help`. Typer supporte un paramètre `epilog=` par
commande — aucune raison de garder cette doc "cachée".

- ☐ Reprendre les exemples du docstring module dans `epilog=` de chaque commande concernée

### 9.2 — Vision post-hackathon (effort plus important, à ne pas commencer avant le rendu)

#### ☐ 9.2.a — Commande `laivelup doctor`
**Effort : M (2-3h)**

**Pourquoi :** convention de plus en plus répandue dans les CLI modernes
(diagnostic autonome à la `flutter doctor`) : vérifier version Python,
encodage terminal, capacité couleur, permissions d'écriture du dossier
`--out`, etc. Utile pour le support cross-platform ("ça marche pas chez
moi") sans avoir à lire les tracebacks.

- ☐ Vérifications : version Python ≥ requis, `sys.stdout.encoding`, capacité
  couleur du terminal, écriture possible dans le dossier courant
- ☐ Sortie lisible + `--json` pour un usage scripté

#### ☐ 9.2.b — Fichier de config utilisateur (XDG cross-platform)
**Effort : M (2h)**

**Pourquoi :** les options répétées à chaque appel (`--out`, `--no-html`,
couleur) sont un point de friction pour un usage répété. Un fichier de
config avec valeurs par défaut, surchargées par les flags CLI, est un
pattern standard des CLI matures (git, npm) — mais ce n'est pas un besoin du
hackathon, juste un confort d'usage à moyen terme.

- ☐ Respecter les conventions XDG sur Linux/Mac, `%APPDATA%` sur Windows
  (le genre de piège cross-platform qu'`encoding.py` gère déjà bien ailleurs)

#### ☐ 9.2.c — Indicateurs de progression (Rich `Progress`/spinner) pour `interrogate`
**Effort : S (1h)**

**Pourquoi :** perception de réactivité, pas de gain de vitesse réel (le
calcul est déjà quasi instantané) — mais un entretien multi-tours sans aucun
retour visuel entre les questions peut sembler figé, surtout la première
fois.

#### ☐ 9.2.d — Benchmark du temps de démarrage à froid
**Effort : XS (15 min) pour mesurer, S/M pour optimiser si besoin**

**Pourquoi :** "performante" se vérifie, ne se déclare pas. `typer` + `rich`
ont un coût d'import non-nul ; mesurer `time laivelup --version` donne un
chiffre concret à citer (ou à améliorer via imports paresseux des
sous-modules `team`) plutôt qu'une affirmation en l'air.

- ☐ Mesurer sur les 3 OS de la matrice CI si possible (Windows a
  historiquement un coût de démarrage Python plus élevé que Linux/Mac)

---

## 10. Sorties HTML — diagnostic et pistes

> **Où on en est déjà :** `report.py::render_html` génère un fichier HTML
> autonome (CSS inline, zéro dépendance externe — aucun CDN, aucune police
> distante). C'est délibérément bien : un jury qui ouvre le rapport hors
> ligne ou sur un poste sans accès réseau le voit correctement. Ne pas perdre
> cette propriété en ajoutant des polices/Google Fonts pendant le redesign.

### 10.0 — Identité visuelle : décidé

**Décision (29/08, Romy) :** identité neutre, **pas** la charte Goumies Creative. Explicitement **anti "AI slop"** : pas de dégradé, pas d'animation. Ni identité d'agence, ni esthétique générique "SaaS IA" (pastilles arrondies, ombres douces, dégradés violet-bleu) — un rapport factuel qui a l'air fabriqué avec soin, pas généré en un prompt.

### 10.1 — Avant le rendu (faible risque, gain d'accessibilité et de lisibilité réels)

#### ☐ 10.1.a — Combler l'écart de contenu MD ↔ HTML
**Effort : XS (10 min)**

**Pourquoi :** `render_markdown` inclut une ligne "Sources : référentiel AIDD
officiel (URL)" dans la section Transparence. `render_html::transparency`
omet cette ligne — quelqu'un qui lit seulement le HTML n'a pas le lien vers
le référentiel officiel. Petit écart, mais un jury qui compare les deux
formats le remarquera.

- ☐ Ajouter la ligne Sources (avec `<a href>`) dans `render_html`

#### ☐ 10.1.b — Accessibilité de la table (lecteurs d'écran)
**Effort : XS (15 min)**

**Pourquoi :** la `<table>` n'a ni `<caption>` ni `scope="col"` sur les
`<th>` — un lecteur d'écran ne peut pas annoncer "colonne Confiance" quand
l'utilisateur navigue cellule par cellule, seulement "colonne 3". Ce sont
deux attributs HTML natifs, aucune dépendance, un vrai gain WCAG.

- ☐ `<caption>Détail par axe d'évaluation</caption>`
- ☐ `scope="col"` sur chaque `<th>`

#### ☐ 10.1.c — Les blocs "flag"/"next" ne doivent pas coder l'info seulement par la couleur
**Effort : S (20 min)**

**Pourquoi :** `.flag` (rouge, bordure gauche) et `.next` (bleu, bordure
gauche) distinguent "red flag" de "prochaine étape" uniquement par une
bordure colorée. Un utilisateur daltonien ou un lecteur d'écran (qui ignore
le CSS) ne perçoit pas cette distinction. Le titre de section ("Red flags"
en `<h2>`) aide, mais chaque bloc individuel gagnerait un préfixe explicite.

- ☐ Ajouter un préfixe visuellement discret mais lisible ("⚠ Vigilance" /
  "→ Piste") à chaque bloc, pas seulement la couleur de bordure

#### ☐ 10.1.d — Vérifier les contrastes WCAG AA des badges
**Effort : XS (10 min, juste un calcul)**

**Pourquoi :** `.ok` (fond `#d1f5d8`, texte `#0b5b23`) et `.ko` (fond
`#ffe3e3`, texte `#8b1a1a`) semblent visuellement contrastés mais "semblent"
n'est pas une preuve. Un ratio calculé (objectif ≥ 4.5:1 pour texte normal)
prend deux minutes et devient une preuve citable dans le README si besoin
("accessibilité vérifiée, pas supposée").

#### ☐ 10.1.e — Hiérarchie typographique : le verdict doit dominer visuellement la page
**Effort : S (30-45 min)**

**Pourquoi :** actuellement `<h1>` (titre) et le badge de verdict ont un
poids visuel proche — taille de police 1.5rem pour le titre, badge en
`padding: .3rem .7rem`. Sur un rapport dont le but est "on comprend le
niveau en un coup d'œil" (critère jury n°1), le niveau devrait être
l'élément le plus massif de la page, pas une pastille au même niveau que le
titre.

- ☐ Agrandir significativement le badge de verdict (voir §10.2 pour la
  direction artistique complète)

### 10.2 — Vision post-hackathon : direction artistique complète

**Objectif : minimalisme brutaliste — bordures franches, pas d'ombres ni de
dégradés, hiérarchie typographique nette, haute densité d'information sans
surcharge visuelle — sans reprendre les trames/textures qui identifient
visuellement le site Goumies Creative** (l'outil est un livrable MIT
indépendant, cf. §10.0).

Principes bruts, sans réponse arrêtée sur les valeurs exactes (à itérer) :

- ☐ **Grille visible, pas de coins arrondis, pas d'ombre portée** — bordures
  `solid` de 2-3px plutôt que `border-radius`/`box-shadow` (déjà le cas pour
  le tableau ; à étendre à tous les blocs)
- ☐ **Un seul accent color** utilisé avec parcimonie (le niveau obtenu, et
  rien d'autre) — actuellement 2 couleurs sémantiques (vert/rouge) + 2 autres
  pour flag/next : cohérent à réduire ou à justifier explicitement
- ☐ **Empilement vertical strict, pas de mise en page en colonnes** —
  cohérent avec le côté "rapport", pas "dashboard"
- ☐ **Typographie : une police d'affichage forte pour le verdict (grande
  taille, graisse marquée), une police neutre pour le corps, une police mono
  pour les données chiffrées** (confiance %, noms de traces) — renforce
  visuellement le message "ceci est mesuré, pas déclaré"
- ☐ **Mode sombre via `prefers-color-scheme`** (pas de toggle JS, juste une
  media query CSS) — cohérent avec ta préférence perso pour le HTML sombre,
  sans imposer de JS à un rapport qui doit rester un fichier statique simple
- ☐ **Feuille de style d'impression (`@media print`)** — un jury qui imprime
  ou exporte en PDF ne devrait pas perdre la lisibilité des badges colorés
- ☐ **Audit WCAG outillé** (axe-core ou Lighthouse CI en local, pas seulement
  une vérification manuelle) une fois le design stabilisé — transforme les
  vérifications ponctuelles du §10.1 en garde-fou reproductible

---

## Journal de bord

**28/08 — Fait :**
- Sujet officiel + profils officiels parcourus, écarts identifiés (grille conforme, critères changés, format profils incompatible)
- Repo officiel localisé et confirmé (`hackathons/laivel-up`, remote `ai-driven-dev/laivel-up`)
- Scan sécurité/confidentialité de l'état courant du dépôt privé : rien trouvé
- 6 bugs concrets identifiés (typo org, URL clone, version drift, nom package, table critères, ADR à vérifier)
- Ce plan écrit

**28/08 — Audit et mitigations (session OpenCode) :**
- Audit 7 piliers complet : 69 findings (0 critical, 26 warning, 32 minor), Health: good
- Mitigations appliquées (commit `4c77971`) :
  - Architecture : `encoding.py` → `cli.py` connection (`ensure_utf8_env` + `make_console` avec `no_color` param)
  - Sécurité : `--fail-on` try/except KeyError (exit 2), `load_team` 1MB size guard, `save_team` symlink rejection
  - Code quality : `_as_numeric()` generic helper, `SIZE_VALUES` derived from `SIZE_ORDER`, `import re` top-level, `_LEVEL_ORDER` removed, dead branch cli.py:267 removed, `_slug` wrapper removed
  - Tests P0 : 11 nouveaux tests (`_filter_fields` 4, `--json` 3, `--fail-on` 3, history trim 1)
  - Dependencies : `pytest-cov>=4.1` → `>=6.0`
  - Snapshots mis à jour pour encoding change
  - Pre-existing test bugs fixed : ANSI regex in team export tests
- **Tous les tests passent** : 356+ ✅ | ruff ✅ | mypy ✅ | bandit ✅
- **Poussé sur GitHub** : `4c77971`

**28/08 — Évaluation ergonomie CLI et code review (session OpenCode) :**
- Évaluation ergonomie CLI : **7.5/10** — 2 P1, 4 P2, 6 P3 identifiés
- Code review : **Production-ready pour un hackathon** — 2 Critical, 8 Warnings, 10 Minor identifiés
- Corrections appliquées :
  - **P1** : Interception ValueError dans toutes les commandes `team` (create, evaluate, export, opt-out, remove)
  - **P1** : Ajout `__main__.py` pour `python -m laivelup`
  - **Critical** : Path traversal dans `write_reports` (vérification `is_relative_to`)
  - **Critical** : TOCTOU race dans `save_team` (atomic write via temp file + `os.replace`)
  - **P2** : `--fail-on` avertit quand verdict est `null`
  - **P2** : `--no-html` ajouté à `team evaluate`
  - **P2** : Warning quand nom d'équipe = sous-commande
  - **P2** : Message "Aucun membre" quand liste vide
  - **Warnings** : `_version_callback` → `error_console`, `_print_verdict` split (evaluate + render), dead code supprimé, double-write `last_answer` supprimé, `_as_numeric` clarifié, redundant assignment supprimé, question tracking par ID, escaping cohérent dans `render_html`
  - **Minor** : `MAX_TEAM_FILE_MB` constante, commentaire em dash mapping, `ensure_utf8_env` lazy
  - **P3** : `--fail-on` liste valeurs valides, `--verbose`/`--quiet` validation mutuelle, NO_COLOR documenté dans docstring
- **Tous les tests passent** : 356 ✅ | ruff ✅ | mypy ✅

**Prochaine étape :**
- Validation de l'extracteur de profils officiels (item 1.1) avant écriture de code
- Inventaire de nettoyage du dépôt (section séparée ci-dessous dans la conversation)

**29/08 — Session de finalisation (Claude, MCP filesystem) :**
- Diagnostic à froid sur `README.md`, `CONTRIBUTING.md`, `pyproject.toml`, `CHANGELOG.md`, `src/laivelup/__init__.py`, `docs/adr/0007-*.md` avant toute édition
- **1.2 fait** : typo org GitHub `goumes-creative` → `goumies-creative` (README badge + lien, CONTRIBUTING gh release)
- **1.5 fait** : `pip install laivel-up` → `pip install laivelup` dans README (Pour les juges) **et** CONTRIBUTING (Vérification post-release, occurrence non listée dans le plan initial)
- **2.3 vérifié, rien à faire** : ADR-0007 déjà à jour (sel HMAC documenté depuis le 24/08)
- **1.4 partiellement clarifié** : `pyproject.toml`/`__init__.py` sont déjà à `0.2.0` (plus de drift avec le CHANGELOG sur ce point précis) — mais le CHANGELOG a un `[Unreleased]` conséquent non rattaché à une version ; décision requise avant `--push` (cf. note dans la section 1.4)
- **Non touché, bloqué ou hors de portée MCP filesystem** :
  - 1.1 (décision fix manuel vs `apply_calibration_fix.py --scenario A`) — nécessite ton arbitrage
  - 1.3 (URL de clone CONTRIBUTING) — bloqué tant que le repo public n'existe pas (cf. section 5)
  - 1.6 (push tag, vérif secret PyPI, publication) — actions git/GitHub hors de portée de l'accès fichiers
  - 2.1 (table Critères d'évaluation README) — nécessite le libellé exact de `SUJET.md` du dépôt officiel, pas encore lu cette session
  - 2.2 (vidéo), 2.4 (formulaire de rendu) — actions manuelles de ton côté

**29/08 (suite) — 2.1, 2.2, 1.1 :**
- **2.1 fait** : `SUJET.md` du dépôt officiel lu, table "Critères d'évaluation" du README refaite avec les libellés exacts et des preuves à vérifier au lieu de scores auto-attribués
- **2.2 avancé** : `docs/VIDEO_PRODUCTION.md` vérifié conforme à la contrainte "muette" (sous-titres burn-in). Typo `laivel-up` corrigée dans le script de sous-titres. `scripts/demo.py` enrichi de commentaires `#` explicatifs par étape (style asciinema officiel), sans régression sur `tests/test_demo.py`. Tableau de sous-titres réaligné sur ces commentaires, timing marqué provisoire (à recaler après tournage réel)
- **1.1 clos** : Romy a lancé `calibrate.py --diff` en réel — **0 erreurs, 4/4 profils matchent `expected.json`** (arthur COPPER, bohort BLUE, leodagan GREEN, perceval RED). La note précédente (UNDECIDED sur perceval/leodagan) était périmée, corrigée dans le plan. Aucune décision de fix à prendre : le calibrage est parfait

**29/08 (suite) — Sections 9 et 10, CLI ergonomics et sorties HTML :**
- Lecture complète de `cli.py` (Typer/Rich) et `report.py` (HTML/MD) avant d'écrire quoi que ce soit — diagnostic basé sur le code réel, pas de recommandations génériques
- Ajout de la section **9 (CLI Ergonomics)** : constat que la base est déjà solide (TTY detection, NO_COLOR/FORCE_COLOR, JSON/fail-on/schema), puis 4 items «avant le rendu» (complétion shell, --no-color/--color explicites, couleurs par niveau cohérentes CLI/HTML, epilog --help) et 4 items «vision post-hackathon» (doctor, config XDG, progress indicators, benchmark démarrage)
- Ajout de la section **10 (Sorties HTML)** : constat que le HTML est déjà autonome (zero dépendance externe, à préserver), question ouverte posée sur l'identité visuelle (Goumies vs LAIVEL UP indépendant), 5 items «avant le rendu» (parité MD/HTML, accessibilité table, blocs flag/next non-color-only, contraste WCAG, hiérarchie typo du verdict), puis vision complète de direction artistique brutaliste (grille visible, un seul accent, typographie à 3 registres, dark mode CSS, print stylesheet, audit WCAG outillé)
- Règle explicite posée : ne pas commencer 9.1/10.1 avant que 1.6, 2.2 et 2.4 soient bouclés — le rendu du 31/08 prime sur le polish

**30/08 — Items 2.5, nettoyage CLI :**
- **2.5 fait** : `--quiet` supprimé de la CLI (doublon inutile de `--json`), "La Décodeuse" supprimé de la CLI, `__init__.py`, `demo.py` — tous les textes affichés aux utilisateurs sont désormais en français correct, sans référence au repo du hackathon
- **Pipeline documenté** : section « Pipeline d'évaluation » ajoutée au README, section « Profils officiels » ajoutée au CONTRIBUTING
- **Copy scoring** : "tenir au bout" → "mener à terme" (scoring.py:304)
- **Verbose fix** : `_print_verdict` refactoré de `verbosity: int` (inutile) à `is_verbose: bool` fonctionnel — `-v` affiche désormais les axes, confiances, évidences, variance
- **Inclusif** : "un développeur" → "des développeurs" dans CLI + docs (README, METHODE, TRANSPARENCE, grille, spec)
- **Copy AIDD** : "niveau AIDD" → "niveau d'adoption de l'AIDD" dans la CLI
- **Snapshot** : `test_main_help` et `test_interrogate_help` mis à jour
- **README-OFFICIEL** : lien officiel vers SUJET.md ajouté

### ☐ 2.5 — Revue copy française complète
**Effort : M · Deadline : 30/08**

**Pourquoi :** tous les textes affichés aux utilisateurs doivent être
impeccables, en français correct, intelligibles et accessibles.
Pas de reprise de la doc du repo ou du trailer officiel du hackathon,
pas de franglais.

**Périmètre :**
- `src/laivelup/cli.py` : help texts, messages d'erreur, docstrings
- `src/laivelup/scoring.py` : messages progress_for_axis
- `src/laivelup/report.py` : labels rapports MD/HTML
- `src/laivelup/team.py` : messages d'erreur
- `README.md` : sections visibles par les juges
- `scripts/demo.py` : commentaires asciinema

**Méthode :** passage en revue avec Claude Desktop (compte gratuit)
via le prompt [`docs/prompts/revue-copy-francaise.md`](docs/prompts/revue-copy-francaise.md).
