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

### ☑ 1.3 — Corriger l'URL de clone dans `CONTRIBUTING.md`
**Effort : XS (5 min) · Deadline : 29/08**

**Statut : ✅ FAIT (31/08).** Le repo public existe déjà (`.git/config` → remote `origin` = `https://github.com/goumies-creative/laivel-up.git`), le blocage annoncé ("une fois le repo public créé") n'existait plus.

**Pourquoi :** la section "Développement local" disait
`git clone https://github.com/ai-driven-dev/laivel-up.git` — c'est l'URL du
**sujet officiel**, pas de ton outil. Quiconque suivait cette instruction clonait
le mauvais dépôt.

- ☑ Remplacé par `git clone https://github.com/goumies-creative/laivel-up.git`

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

### ☑ 2.2 — Vidéo de démo : contrainte "muette" non anticipée
**Effort : M (1-2h tournage) · Deadline : 30/08 après-midi**

**Statut : ✅ FAIT (31/08, confirmé par Romy).** Enregistrement réalisé, sous-titres/texte à l'écran en place (conforme à la contrainte "publiée muette"). Reste à faire côté 2.4 : récupérer le lien final (hébergement) pour le formulaire de rendu.

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

- ☑ Scan de sécurité/confidentialité sur l'état courant : **fait le 28/08,
  rien trouvé** (voir annexe). Scan complet de l'historique git (tous
  commits) — **historique nettoyé, confirmé par Romy le 31/08** (pas de contre-vérification possible côté moi pour l'historique, MCP filesystem = état courant seulement)
- ⚠️ Créer le nouveau repo public sur GitHub — Romy confirme fait, **mais vérification indépendante (curl, 31/08) renvoie 404 sur `github.com/goumies-creative/laivel-up`** — conflit non résolu, cf. détail en 1.6 bis. Ne pas considérer comme acquis avant confirmation navigateur.
- ⚠️ `git remote add public <url> && git push public main --tags` — Romy confirme fait ; même réserve que ci-dessus tant que la visibilité n'est pas confirmée
- ☐ Copier `levels/aidd.md` et les 4 dossiers `profiles/` officiels dans le
  repo public (`docs/reference/` et `tests/fixtures/profiles-officiels/`),
  avec mention d'attribution MIT (ai-driven-dev/laivel-up) — à confirmer, non couvert par la confirmation « repo public + historique nettoyé »
- ☑ Corriger l'URL de clone dans `CONTRIBUTING.md` une fois le repo public créé (cf. 1.3) — déjà fait le 31/08 matin (édition de fichier, indépendant de la question de visibilité)

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
- [x] Scan sécurité historique git — historique nettoyé, confirmé par Romy le 31/08
- [ ] Repo public créé sur GitHub — Romy confirme fait, mais curl indépendant (31/08) renvoie 404 — **conflit non résolu, cf. 1.6 bis**
- [ ] Historique poussé vers repo public — idem, en attente de confirmation navigateur
- [ ] Package publié sur PyPI — **toujours en attente, cf. 1.6** (404 constaté en direct)
- [ ] GitHub Release créée — dépend du tag/push PyPI (1.6)

### 8.4 — Rendu officiel
- [x] Vidéo muette tournée et vérifiée — confirmé par Romy le 31/08 (cf. 2.2)
- [ ] Formulaire de rendu rempli et déposé avant 31/08 12h — **dernier bloquant, cf. 2.4**
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

**31/08 (matin) — Session Claude/MCP filesystem, vérifications pré-rendu :**
- Diagnostic à froid confirmé par lecture directe (pas supposé) : `.git/config` → remote `origin` = `https://github.com/goumies-creative/laivel-up.git` (repo public existe bel et bien)
- **1.3 fait** : URL de clone `CONTRIBUTING.md` corrigée (`ai-driven-dev` → `goumies-creative`), le blocage "repo pas encore public" n'était plus d'actualité
- **2.5 resynchronisé** : case ☐ → ☑ (le travail était fait et journalisé le 30/08, la case n'avait pas suivi)
- **11.6 vérifié** : lecture complète de `team.py::evaluate_member` — aucun écrasement, l'historique accumule bien un enregistrement par évaluation (voir détail dans la section 11.6)
- **1.6 — toujours en attente côté toi** : `.git/refs/tags` est vide et aucun `packed-refs` n'existe en local → le tag `v0.2.0-hackathon` n'a pas encore été poussé. Push/tag/PyPI restent hors de portée du MCP filesystem (lecture/écriture de fichiers seulement, pas de commandes git)
- **2 points de vigilance repérés (non corrigés, à trancher par toi avant le push)** :
  1. `src/laivelup/scoring.py.bak` existe à la racine du package — fichier de sauvegarde probablement oublié, à supprimer ou vérifier qu'il est bien gitignoré avant publication (bruit inutile pour un jury qui parcourt le code)
  2. `src/laivelup/tui/` (mascot/, screens/, viewmodels/, widgets/) est présent dans l'arborescence alors que le HEAD courant est sur `main` — la section 11.3 prévoyait cette isolation TUI sur la branche dédiée `feat/tui-8bit`, pas sur `main`. Le MCP filesystem ne permet pas de vérifier si ces fichiers sont trackés par git sur `main` ou simplement présents dans l'arbre de travail (untracked) — `git status` côté toi tranchera ; si trackés sur `main`, risque de contredire la règle d'isolement posée en 11.3

**31/08 (suite) — Vérification en direct GitHub/PyPI (bash_tool, API publiques, sans authentification) :**
- 🚨 **`https://api.github.com/repos/goumies-creative/laivel-up` → 404**, idème pour `/tags`, `/releases`, `/actions/runs`. L'utilisateur GitHub `goumies-creative` existe bien (200 sur `/users/goumies-creative`), donc ce n'est pas un problème de nom — le dépôt lui-même n'est **pas visible publiquement** en ce moment. Vu que le README documente déjà une note CI (jobs bloqués par la facturation, 495 tests/95% coverage en local) — la preuve que du code a bien tourné en CI dessus — le dépôt existe très probablement mais **en privé**, pas absent. **Correction de mon affirmation précédente** ("le repo public existe déjà", écrite en 1.3 ce matin) : l'URL de clone est la bonne, mais sa visibilité publique n'est **pas confirmée** — à vérifier et corriger en priorité absolue, cf. nouvel item 1.6 bis ci-dessous.
- **`https://pypi.org/pypi/laivelup/json` → 404** : le package n'est pas encore publié sur PyPI. Confirme (source indépendante du `.git/refs/tags` local, déjà vide) que 1.6 n'est pas fait.
- **11.4 avancé** : lecture de `docs/QUICKSTART_JUDGES.md` — trouvé et corrigé le même chantier que 2.1 avait déjà résolu dans le README, mais oublié ici : ancienne table "Accuracy/Explainability/Robustness/Reusability" avec scores auto-attribués (4/5), et compteur de tests périmé ("85+" puis "344"). Remplacé par la table officielle `SUJET.md` (identique au README) et le compte à jour (495 tests). `pip install .` remplacé par `pip install laivelup` en première commande (cohérent avec la commande de lancement annoncée en 2.4), `pip install .` gardé en option clone local.
- **README resynchronisé** : même écart trouvé dans la table "Critères d'évaluation" du README (356 tests/88.73% — périmé depuis le 29/08) → aligné sur 495 tests/95% (chiffre que tu avais toi-même noté dans la note CI juste au-dessus, dans le même fichier)

### ⚠️ 1.6 bis — URGENT : confirmer/forcer la visibilité publique du repo GitHub
**Effort : XS (2 min) · Bloquant absolu pour le formulaire (2.4) et pour 1.6**

**Statut : ⚠️ CONFLIT à résoudre (31/08).** Romy confirme le repo rendu public. Vérification indépendante faite à l'instant (bash_tool, sans auth, avec User-Agent explicite) : `https://github.com/goumies-creative/laivel-up` → **404**, et `https://api.github.com/repos/goumies-creative/laivel-up` → rate-limit (403, non concluant) sur un essai, puis à revalider. Le 404 sur la page web (pas l'API) est le signal le plus fiable ici : GitHub renvoie 404 (pas 403) pour un repo privé à un visiteur non authentifié, exactement le même comportement que « n'existe pas » — **ne pas cocher tant que ce n'est pas confirmé côté navigateur.** Hypothèses à trancher par Romy : (a) mauvais nom d'org/repo (le remote local point vers `goumies-creative/laivel-up`, mais un compte `github.com/Goumies` distinct existe aussi), (b) changement de visibilité pas encore propagé côté GitHub, (c) repo créé sous un autre chemin. **Action immédiate demandée : ouvrir le lien exact dans un navigateur en navigation privée (déconnectée) et confirmer que la page charge, avant de le coller dans le formulaire (2.4).**

**Pourquoi :** un jury qui reçoit un lien de repo privé ne peut rien évaluer. Vérifié en direct (31/08) : `goumies-creative/laivel-up` renvoie 404 sur l'API GitHub publique sans authentification — signe d'un dépôt privé (ou pas encore créé, moins probable vu la note CI déjà présente dans le README qui suppose des runs CI antérieurs).

- ☐ Ouvrir `https://github.com/goumies-creative/laivel-up/settings` → si la page charge, le repo existe : descendre à "Danger Zone" → "Change visibility" → Public
- ☐ Si la page ne charge pas (404 côté navigateur aussi) : le repo n'existe pas encore → le créer (`gh repo create goumies-creative/laivel-up --public --source=. --remote=origin` depuis le dossier du projet, ou via l'interface GitHub) puis `git push -u origin main`
- ☐ Une fois public, revalider en relançant `curl https://api.github.com/repos/goumies-creative/laivel-up` (doit répondre 200) — je peux le refaire côté moi si tu veux une confirmation indépendante

### ☑ 2.5 — Revue copy française complète
**Effort : M · Deadline : 30/08**

**Statut : ✅ FAIT (30/08)** — voir journal de bord ci-dessous pour le détail (case restée ☐ par oubli de synchro, corrigée le 31/08).

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

---

## 11. Chantiers proposés (31/08, priorités posées par Romy) · à ne pas démarrer avant 1.6/2.2/2.4

> **Rappel de la règle posée en section 9, encore plus vraie à quelques
> heures du rendu :** aucun des chantiers ci-dessous ne démarre avant que
> 1.6, 2.2 et 2.4 soient clos : non confirmé clos à ce jour (cf. journal).
> Seuls **11.4** et **11.6** sont potentiellement éligibles *avant* midi
> (effort XS-S, valeur directe pour le rendu) ; tout le reste est
> post-soumission.

> **État CI (31/08) :** les jobs GitHub Actions échouent sur la facturation
> du compte (« recent account payments have failed or your spending limit
> needs to be increased »), pas sur le code. Fixes déjà poussés et verts en
> local : snapshots portables cross-OS, bandit B110 skippé (exit 0), 481
> tests · ruff · mypy. Re-vérifier sur GitHub après régularisation du
> billing ; note de transparence ajoutée au README (Pour les juges).
> Suite au passage : complétion shell documentée (contournement Windows),
> glossaire « Reprise », feedbacks interrogate nommés (495 tests).

### ☐ 11.1 — Mutation testing avec `mutmut`
**Effort : M-L (config + run, mutmut est lent sur une suite de 481 tests) · Timing : après soumission**

**Pourquoi :** mesure la robustesse réelle des tests (pas juste leur couverture) en mutant le code et vérifiant que les tests échouent. Valeur réelle, mais aucun impact sur les critères jury directs · pas de raison de le lancer avant le rendu.

- ☐ Mobiliser les skills/agents AIDD et compound engineering pertinents (à identifier)
- ☐ Configurer `mutmut` sur `src/laivelup/`
- ☐ Lancer, analyser les mutants survivants
- ☐ Renforcer les tests sur les zones faibles identifiées

### ☐ 11.2 — Sorties « agréables + ludiques, inspirées jeu vidéo »
**Effort : M · Timing : après soumission (recoupe §9 et §10 déjà posés le 29/08)**

**Pourquoi :** le jury insiste sur les sorties. Constat réel : le HTML (`report.py`) a déjà une direction 8-bit/Patapon (world map, badges pixel, palette néon) ; c'est le **CLI** qui reste une table Rich neutre sans identité · l'écart est bien réel côté CLI, moins côté HTML.

- ☐ Reprendre §9.1.c (couleurs par niveau dans la table Rich) et §10.2 (direction artistique brutaliste complète) comme base
- ☐ Étendre l'identité pixel/jeu vidéo au CLI (pas seulement le HTML)

### ☐ 11.3 — Bonus TUI 8 bits (branche dédiée)
**Effort : L · Timing : bonus conditionnel post-soumission, sur branche isolée**

**Pourquoi :** posé par Romy elle-même comme conditionnel (« si j'ai le temps »). Bon réflexe de l'isoler sur une branche dédiée : aucun risque sur `main`/le rendu si le temps manque.

- ☐ Créer la branche dédiée
- ☐ Scoper le MVP du TUI (bibliothèque à choisir, ex. Textual)

### ☐ 11.4 — Tests manuels via la doc juges + amélioration au passage
**Effort : S · Timing : éligible avant midi si marge, sinon juste après**

**Pourquoi :** dogfooding direct de l'expérience jury (`QUICKSTART_JUDGES.md`) · recoupe la vérification de 1.6 (`pip install laivelup` fonctionne réellement) et 2.4 (la commande de lancement annoncée est la bonne). Valeur directe pour le rendu, pas du pur polish.

- ☐ Suivre `docs/QUICKSTART_JUDGES.md` pas à pas, en conditions réelles
- ☐ Noter tout point de friction et corriger le doc au passage

### ☐ 11.5 — Audits AIDD + compound engineering complets
**Effort : L · Timing : après soumission**

**Pourquoi :** le dernier audit 7-piliers (28/08) a produit 69 findings sur du code qui passait déjà tous les checks · relancer un audit complet à quelques heures du rendu risque d'ouvrir des chantiers qu'il n'y aura pas le temps de fermer proprement.

### ☑ 11.6 — Ne pas écraser l'évaluation précédente d'un membre lors d'une réévaluation
**Effort : XS pour vérifier, S si correctif réel · Timing : éligible avant midi (vérification rapide d'abord)**

**Statut : ✅ Vérifié (31/08) — pas de bug, aucun correctif nécessaire.** Lecture complète de `team.py::evaluate_member` : chaque appel fait `team.history.append({...})` (accumulation, jamais une réécriture) puis trim S3 à `_MAX_HISTORY=100`. Seul `team.members[member_slug]` (l'instantané "état courant") est remplacé à chaque réévaluation — c'est le comportement attendu (état courant ≠ historique). `remove_member(purge=False)` marque les entrées passées `opt_out: True` sans les supprimer ; `purge=True` les filtre. Confirme la cohérence avec `test_remove_member_purge_historique`.

**Pourquoi :** intégrité des données d'équipe. `team.history` semble déjà accumuler un enregistrement par évaluation (cf. tests RGPD droit à l'oubli · `test_remove_member_purge_historique` vérifie `len(team.history) == 1` après un seul `evaluate_member`), mais ça reste à confirmer sur le code réel de `team.py`, pas à supposer depuis les tests seuls.

- ☑ Lire `team.py::evaluate_member` en entier avant toute conclusion
- ☑ Confirmer si l'historique est bien préservé pour une mise à jour partielle des traces (pas seulement une évaluation complète)
- ☑ Corriger si un écrasement réel est trouvé — sans objet, rien trouvé

### ☐ 11.7 — Nouvel axe « Professionnalisation / Industrialisation » (optionnel, hors règle AND)
**Effort : L · Timing : après soumission · décision de conception actée (31/08)**

**Décision actée (31/08, Romy) :** l'axe sera **optionnel**, affiché à part, **hors de la règle AND** qui détermine le verdict principal (`min()` sur les 4 axes officiels). Ça lève le risque identifié précédemment : les 4 profils officiels restent calibrés COPPER/BLUE/GREEN/RED sans dépendre de données d'industrialisation qu'ils n'ont pas · la preuve « 4/4, zéro écart » du pitch n'est plus menacée. Reste un chantier volumineux (L) : barème à concevoir, intégration CLI/rapports MD/HTML sans polluer le verdict principal, nouvelles fixtures · toujours hors scope du 31/08, mais sans risque structurel sur le rendu.

- ☐ Challenger la pertinence de l'axe face aux 4 axes officiels, avec les skills/agents AIDD et compound engineering pertinents
- ☐ Concevoir l'affichage « bonus » (CLI + rapports MD/HTML) : visuellement distinct du verdict AND, jamais mélangé aux 4 axes qui déterminent le niveau
- ☐ Vérifier si les données brutes des profils officiels (`profiles/*/git-activity.json`, `repo-context/`, `sonar-measures.json`, etc.) permettent réellement de répondre à cet axe
- ☐ Créer, dans un dossier dédié, un profil officiel réaliste complet couvrant ce nouvel axe (basé sur l'existant officiel)
- ☐ Créer un second profil avec 2 « trous » de données sur ce nouvel axe (cas refus de deviner)

**Vision (31/08) — ce que mesure l'axe :** au-delà des 4 axes officiels (qui
regardent *comment le code a été écrit*), cet axe regarde *comment le projet
est industrialisé pour durer* : CI/CD, outillage qualité, discipline de
release. Trois signaux pistés, chacun **corroboré** plutôt que pris seul —
même philosophie anti-déclaratif que les 4 axes officiels (cf. ADR-0004) :

| Signal (piste, non arrêtée) | Source brute envisagée | Pourquoi corroboré, pas seul |
|---|---|---|
| CI/CD configuré | `repo-context/` (workflows détectés) ou `git-activity.json` | Un fichier de config seul ne prouve pas qu'elle tourne réellement — à croiser avec un historique de runs si dispo |
| Qualité outillée | `sonar-measures.json` (**actuellement non utilisé** par l'extracteur, cf. `GRID_QUICKREF.md` — piste immédiate) | Piège déjà identifié pour les 4 axes officiels (« s'arrêter aux métriques ») : s'applique tout autant ici |
| Discipline de release | tags / CHANGELOG dans `git-activity.json` ou `repo-context/` | Un CHANGELOG statique ne prouve pas des releases réelles — à croiser avec des tags git si disponibles |

Ces 3 signaux restent des pistes : seuils et pondération sont un chantier à
part (1ère puce ci-dessus), et la disponibilité réelle de `sonar-measures.json`
et des workflows CI par profil officiel reste à vérifier fichier par fichier
(3e puce ci-dessus) — rien de ceci n'est supposé acquis par ce document.

**Cas d'usage détaillé de `docs/EXTENDING.md`** (recette « Ajouter un axe
bonus (hors règle AND) », ajoutée en miroir de cette vision — voir plus bas) :

1. **`model.py`** — ne **pas** ajouter la clé dans `AXES` (ça la ferait
   entrer dans le `min()` du verdict principal). Ajouter plutôt :
   - `BONUS_AXES = ('industrialisation',)` (tuple séparé de `AXES`)
   - `AXIS_LABELS['industrialisation'] = 'Industrialisation'` (même dict,
     l'affichage n'a pas besoin d'être séparé)
   - `Verdict.bonus_axis_scores: list[AxisScore] = field(default_factory=list)`
     — nouveau champ à côté de `axis_scores`, pour ne jamais mélanger les
     deux dans le calcul du niveau
2. **`scoring_defaults.py`** — nouvelle sous-clé
   `SCORING_DEFAULTS['INDUSTRIALIZATION']`, isolée des seuils des 4 axes
   officiels (aucun risque de collision si on retouche un jour les seuils
   historiques)
3. **`scoring.py` → `evaluate()`** — après le calcul de `global_level` (qui
   ne doit lire que `AXES`), ajouter un **second passage indépendant** sur
   `BONUS_AXES` avec un scorer `industrialisation_max()` dédié : même
   sémantique refus > deviner (confiance basse ou données absentes →
   `level=None`, jamais un niveau inventé) — **mais** un axe bonus non
   tranché ne doit **jamais** déclencher le `_refuse()` du verdict
   principal. C'est le point de vigilance n°1 de cette étape : un profil
   sans données d'industrialisation doit rester RED/BLUE/GREEN/COPPER
   normalement sur les 4 axes officiels, avec juste `bonus_axis_scores`
   vide ou à confiance basse à côté
4. **`tests/test_scoring.py`** — au minimum 3 cas en plus du nominal :
   (a) profil avec signaux d'industrialisation complets → axe bonus
   tranché sans toucher au niveau global ; (b) profil sans aucune donnée
   d'industrialisation → niveau global inchangé, axe bonus refusé/absent ;
   (c) **non-régression** : les 4 profils officiels calibrés
   (arthur/bohort/leodagan/perceval) gardent exactement leur niveau AND
   actuel après l'ajout — le test qui protège la preuve « 4/4, zéro écart »
   du pitch
5. **`schemas/profile.schema.json`** — champs `traces.*` de l'axe bonus
   ajoutés comme **optionnels** (jamais `required`), pour ne casser la
   validation d'aucun profil existant, y compris les 4 officiels qui n'ont
   pas ces données
6. **`scripts/extract_official_profile.py`** (extracteur profils officiels
   → traces — hors recette générique `EXTENDING.md`, spécifique à ce
   projet) — **vérifié sur les 4 profils réels (31/08)**, pas supposé :
   - `sonar-measures.json` **existe pour les 4 profils** (arthur, bohort,
     leodagan, perceval) — contrairement à `pull-requests.json`, ce n'est
     pas une pièce partielle : aucun « trou » sur cette pièce précise pour
     les profils officiels
   - Structure réelle : `component.measures` = liste de `{metric, value}`
     (valeurs en chaîne, à caster) — pas un objet plat comme les autres
     pièces. Champs utiles vérifiés sur les 4 profils : `coverage`,
     `code_smells`, `bugs`, `duplicated_lines_density`
   - **Correction de la piste CI/CD envisagée plus haut :** aucun fichier
     de workflow (`.github/workflows/*`) n'est présent dans `repo-context/`
     pour aucun des 4 profils — la piste « CI/CD configuré via
     repo-context » n'a donc pas de données réelles à lire. En revanche
     `git-activity.json` (déjà lu par l'extracteur pour les 4 axes
     officiels) contient un objet `ci` non exploité à ce jour —
     `ci.failure_rate` / `ci.median_runs_to_green`, présent sur les 4
     profils : signal plus fort qu'un simple fichier de config (il prouve
     que la CI tourne, pas seulement qu'elle existe), et **sans nouvelle
     source de données à brancher** — juste un champ de plus à lire dans un
     fichier déjà ouvert
   - Signal de tendance couverture, également déjà présent dans
     `git-activity.json → tests` : `coverage_start` / `coverage_end` /
     `prs_with_tests_ratio` — sert de **corroboration** au chiffre statique
     de `sonar-measures.json → coverage` (écart constaté sur les 4 profils :
     quelques points de pourcentage, cohérent avec une différence de
     périmètre de mesure entre les deux outils, pas une contradiction)
   - Nouvelles fonctions d'extraction, strictement additives :
     `_extract_sonar_measures()`, `_extract_ci_signals()`,
     `_extract_coverage_trend()` — écrites dans un **nouveau namespace**
     `traces['industrialisation'] = {...}`, jamais dans les clés existantes
     (`pr_sizes`, `context_versioned`, etc.) : aucune clé actuelle n'est
     renommée, déplacée ou recalculée → zéro risque de régression sur les 4
     niveaux déjà calibrés
   - Lecture protégée pièce par pièce (même pattern que le reste de
     l'extracteur) : un `sonar-measures.json` absent ou malformé sur un
     futur 5e profil ne doit jamais faire échouer l'extraction des 4 axes
     officiels — juste laisser `traces['industrialisation']` vide ou
     partiel

**Risque de régression identifié (schema) — à corriger dans la même passe :**
`schemas/profile.schema.json` a `"additionalProperties": false` sur
`traces` — une clé `industrialisation` non déclarée y serait **rejetée**
par le validateur `jsonschema` (`Draft202012Validator`), alors que le
fallback `_validate_minimal()` de `schema.py` (utilisé quand la dépendance
`jsonschema` n'est pas installée, cf. ADR-0012) ne fait lui aucune
vérification `additionalProperties` et laisserait passer la même clé sans
broncher — **asymétrie à connaître**, pas un bug en soi, mais un piège si on
ne corrige qu'un des deux chemins de validation en pensant avoir couvert le
cas. Fix : ajouter `industrialisation` comme propriété **optionnelle**
(objet imbriqué, ses propres sous-clés typées/bornées) dans
`traces.properties` du schema — jamais dans `required`, et sans toucher aux
10 propriétés existantes.

**Affichage (rappel décision actée) :** CLI + rapports MD/HTML, visuellement
distinct du bloc verdict AND (cf. §9.1.c et §10 pour les conventions de
couleur/typo déjà posées) — jamais dans le même bloc que les 4 axes qui
déterminent le niveau.

**Docs mises à jour en miroir de cette vision (31/08) :**
- `docs/EXTENDING.md` : nouvelle section « Ajouter un axe bonus (hors règle
  AND) » — recette générique pour tout futur axe optionnel, pas seulement
  Industrialisation
- `docs/adr/0017-axe-bonus-industrialisation-hors-regle-and.md` : décision
  actée formalisée au format ADR (même format que ADR-0004 sur la grille à 4
  axes), pour qu'un futur lecteur du dépôt (jury inclus) retrouve le
  raisonnement sans devoir relire ce plan

> Rappel : ce chantier reste **après soumission** (règle de section 11, non
> renégociée ici) — seule la documentation de la vision est faite le 31/08,
> aucun code n'est touché avant le rendu.

**31/08 (suite) — Session Claude/MCP filesystem, confirmations Romy (vidéo + repo public/historique) :**
- Romy confirme : vidéo de démo tournée (2.2 → fait), repo rendu public et historique nettoyé (section 5 → fait côté elle)
- **2.2 coché fait**, sans réserve — rien à vérifier côté moi sur une vidéo (pas d'accès au fichier/lien)
- **1.6 bis / section 5 (repo public) : conflit détecté, PAS coché.** Vérification indépendante via `bash_tool` (curl, avec et sans User-Agent explicite) : `https://github.com/goumies-creative/laivel-up` → **404** de façon répétée ; `https://api.github.com/repos/goumies-creative/laivel-up` → rate-limit (non concluant). Un 404 sur la page web GitHub pour un visiteur non authentifié est le comportement standard d'un repo **privé** (GitHub masque volontairement l'existence des repos privés en renvoyant 404, pas 403). **Ne pas coller ce lien dans le formulaire (2.4) avant confirmation visuelle par Romy elle-même, en navigation privée/déconnectée.**
- Sections mises à jour en conséquence : 1.6 bis (statut ⚠️), section 5 (2 items ⚠️ au lieu de ☑), section 8.3/8.4 (checklist resynchronisée)
