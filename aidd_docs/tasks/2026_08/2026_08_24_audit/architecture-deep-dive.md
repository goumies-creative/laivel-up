# Deep Dive Architecture — LAIVEL UP

**Date** : 2026-08-24
**Méthode** : persona *System Architecture Expert* (`skills/ce-plan/references/agents/architecture-strategist.md` du plugin compound-engineering, cache local `~/.cache/opencode/...`) appliquée manuellement au code actuel — pas de pipeline multi-agents (indisponible dans ce chat). Lecture directe : `docs/architecture.mmd`, les 16 ADR (`docs/adr/`), `src/laivelup/*.py` en intégralité, `scripts/ci_evaluate.py`, `scripts/version_bump.py`, `.github/workflows/{ci,release,aidd-eval}.yml`, `pyproject.toml`. Comparaison avec les audits du 23/08 (`architecture.md`, `report.md`) et les deep dives du 24/08 (`adversarial-deep-dive.md`, `performance-deep-dive.md`).
**Angle** : pas "est-ce que le diagramme est joli", mais alignement code ↔ décisions documentées (ADR), frontières de composants, cohérence des abstractions, et dérive silencieuse entre chemins d'exécution qui devraient partager un seul contrat.

## 0. Ce qui était déjà signalé le 23/08 — état aujourd'hui

Les 2 findings architecture du 23/08 (`architecture.md`) sont désormais dans des états différents :

- **Résolu** : la violation ADR-0011 (`schema.py:13` cassait `evaluate`/`interrogate` après une install non-éditable) — le schéma est bien sous `src/laivelup/schemas/`, `pyproject.toml` déclare `package-data`, confirmé par `adversarial-deep-dive.md` §0.
- **Résolu** : l'absence de persistance du Team Tracker — `team.py` a maintenant `load_team()`/`save_team()`, `cli.py` les appelle dans les 4 sous-commandes `team`. **Mais** : toujours aucune ADR dédiée à cette frontière CLI ↔ domaine (persistance JSON locale, `.laivelup/teams/`) — la décision existe dans le code depuis le 23/08, pas encore dans `docs/adr/`. C'est le seul residual du 23/08 encore ouvert.
- **Partiellement corrigé** : `docs/architecture.mmd` incluait 3 des 5 scripts manquants au 23/08 (`generate_profile.py`, `ci_evaluate.py`, `benchmark.py` apparaissent maintenant dans le sous-graphe `Scripts`). Il manque toujours `release_hackathon.sh` et `run_all_examples.sh`.

Bonne nouvelle donc, dans la continuité de `adversarial-deep-dive.md` §0 : le fondamental (schéma, persistance) tient. Voici ce que la lentille architecture trouve **en plus**, sur des frontières que les deep dives sécurité/perf du 24/08 n'ont pas regardées.

## 1. Vue d'ensemble de l'architecture

Le graphe de dépendances réel (lu module par module, pas depuis le diagramme) est propre et acyclique :

```
model.py        ← type central du domaine (Level, AxisScore, Verdict, ProfileData), aucune dépendance interne
scoring_defaults.py ← model
schema.py        ← stdlib + jsonschema (optionnel), indépendant du reste
scoring.py       ← model, scoring_defaults, questions (import tardif)
report.py        ← model, utils
team.py          ← model, scoring, utils
questions.py      ← aucune dépendance
utils.py         ← stdlib uniquement
cli.py           ← model, report, schema, scoring, team (orchestrateur du haut)
```

Aucun cycle, aucune dépendance remontante vers `cli.py` depuis le domaine — la couche CLI reste bien la seule à composer les autres. C'est une architecture en couches propre pour un projet de cette taille, et la discipline ADR est solide (16 décisions actées, avec des mises à jour tracées — ex. ADR-0007 « Mis à jour : 2026-08-24 »). Les 3 findings ci-dessous ne remettent pas ça en cause : ce sont des frontières précises où un même contrat (anonymisation RGPD, validation de schéma, sérialisation du verdict) se retrouve appliqué deux fois, de façon divergente, sans qu'aucune ADR ne couvre le deuxième chemin.

## 2. Findings

| # | Sev | Catégorie | Location | Constat | Confiance |
|---|-----|-----------|----------|---------|-----------|
| 1 | 🟡 P1 | architecture/sécurité | `src/laivelup/report.py:_slug`, `utils.py:slug` | **Le contrat RGPD de l'ADR-0007 (HMAC-SHA256 salé) n'est appliqué que côté `team.py` ; le chemin `evaluate`/`interrogate` — la fonctionnalité vitrine — reste en permanence sur la branche « dépréciée »** | 90 |
| 2 | 🟡 P2 | architecture/couches | `scripts/ci_evaluate.py` | **Le chemin d'évaluation utilisé sur chaque PR contourne entièrement la validation JSON Schema (ADR-0012)** | 90 |
| 3 | 🟡 P2 | architecture/DRY | `report.py`, `team.py::export_json`, `scripts/ci_evaluate.py` | **Trois sérialisations indépendantes et non testées du même objet `Verdict`/`AxisScore` — une a déjà dérivé (champs manquants)** | 95 |
| 4 | 🟢 P3 | architecture/documentation | `docs/architecture.mmd` | Diagramme toujours incomplet : `release_hackathon.sh` et `run_all_examples.sh` absents | 100 |
| 5 | 🟢 P3 | architecture/cohérence | `scoring.py`, `cli.py` | Import tardif (`from .questions import QUESTION_IDS` dans le corps de fonction) sans raison structurelle — `questions.py` n'a aucune dépendance, aucun risque de cycle | 70 |

---

### #1 — Le contrat RGPD salé de l'ADR-0007 ne couvre qu'une moitié des chemins d'exécution

**Ce que documente l'ADR-0007** (mise à jour 2026-08-24) : le slug pseudo-anonyme doit passer par `hmac.new(salt, name, sha256)`, le SHA-256 simple sans sel étant explicitement qualifié de « déprécié — résistant collision, pas dictionnaire », gardé uniquement « pour rétro-compatibilité (lecture anciens fichiers) ».

**Ce que fait le code** :

```python
# team.py — chemin "équipe" : salt systématiquement fourni
def _slug(name: str, salt: str | None = None) -> str:
    return slug(name, salt)
# → create_team() passe toujours team.salt (généré à la création)
```

```python
# report.py — chemin "evaluate / interrogate" (la fonctionnalité que le README
# met en avant en premier, celle testée par les juges) :
def _slug(name: str) -> str:
    # Slug court et stable, sans conserver de nom humain lisible (prudence RGPD).
    return slug(name)   # ← aucun salt passé, jamais
```

`write_reports()` (appelé par `evaluate`, `interrogate`, et `team evaluate`) utilise `report._slug()` pour nommer les fichiers dans `rapports/`. Pour tout usage individuel — `laivelup evaluate profil.json` où `profil.json.name` est le nom de la personne évaluée, cas d'usage central du README — le nom de fichier est dérivé par SHA-256 **sans sel**, exactement le chemin que l'ADR-0007 qualifie de vulnérable au dictionnaire sur un espace de noms restreint (ex. l'équipe ou la promo connue du client). Ce n'est pas de la lecture de « anciens fichiers » : c'est le comportement par défaut, actuel, de la commande la plus utilisée du produit.

**Pourquoi c'est une frontière, pas juste un bug isolé** : `utils.slug()` est le point d'entrée unique du contrat RGPD (§ADR-0006, ADR-0007), appelé depuis deux couches différentes (`team.py` et `report.py`) avec deux postures de sécurité opposées, et rien dans l'architecture (ni le type, ni un paramètre obligatoire, ni une ADR) ne force l'appelant à fournir un sel. Le paramètre `salt` étant optionnel avec défaut `None`, l'omission est silencieuse — aucun test, aucun linter ne peut la détecter, contrairement à un type qui rendrait le sel obligatoire.

**Recommandation** : soit `report.py` génère/consomme un sel par exécution (documenté dans une ADR étendant l'ADR-0007 au périmètre hors-équipe), soit — plus simple — le nom de fichier n'a pas besoin d'être un pseudonyme résistant au dictionnaire pour un usage individuel local (le fichier reste sur le poste de l'utilisateur⋅rice, il ne « fuit » pas comme un rapport d'équipe partagé) : dans ce cas, l'ADR-0007 devrait dire explicitement que son périmètre est le Team Tracker uniquement, et pas prétendre couvrir « les rapports partagés » au sens large sans le vérifier pour `report.py`. Dans les deux cas, c'est une décision à acter, pas un défaut implicite.

---

### #2 — `ci_evaluate.py` contourne la validation JSON Schema sur le chemin qui tourne à chaque PR

**Frontière documentée** : ADR-0012 fixe la validation JSON Schema (`schema.validate_profile()`) comme garde fail-fast avant toute évaluation. `cli.py::_load_profile()` est le seul endroit qui applique ce contrat pour les commandes `evaluate`/`interrogate`/`team evaluate`.

**Ce que fait `scripts/ci_evaluate.py`** (exécuté par `.github/workflows/aidd-eval.yml` sur chaque `pull_request: [opened, synchronize]`, donc à chaque push sur une PR) :

```python
from generate_profile import generate_profile
profile = generate_profile(repo, args.user, verbose=False)

from laivelup.model import ProfileData
from laivelup.scoring import evaluate   # ← pas d'import de schema.validate_profile

profile_data = ProfileData(
    name=profile["name"],
    declared_level=None,
    traces=profile["traces"],
    ...
)
verdict = evaluate(profile_data)   # ← normalize_profile() interne, pas le schema JSON
```

Ce chemin construit un `ProfileData` directement depuis la sortie de `generate_profile()` et appelle `scoring.evaluate()` sans jamais passer par `schema.validate_profile()`. La seule garde qui reste est `scoring.normalize_profile()` (interne à `evaluate()`), qui vérifie les types mais pas la forme complète du schéma (`profile.schema.json`) — deux validations qui existent en parallèle depuis l'ADR-0012 (« Négatives : maintenance schema = 2 endroits ») mais dont un seul est réellement appliqué ici.

**Conséquence concrète** : le workflow qui poste un commentaire visible sur chaque PR — donc la fonctionnalité la plus « publique » de l'outil après le CLI lui-même — n'a pas la garantie fail-fast que l'ADR-0012 promet pour le reste du produit. Si `generate_profile()` produit un jour une valeur de trace hors des bornes que `normalize_profile()` vérifie mais que le schema JSON contraint plus strictement (ou l'inverse), les deux chemins peuvent diverger silencieusement sans qu'aucun test ne le voie — il n'existe aucun `tests/test_ci_evaluate.py` (confirmé : absent de `tests/`, comme déjà noté pour `generate_profile.py` dans `performance-deep-dive.md` §3.1).

**Recommandation** : faire passer `ci_evaluate.py` par `schema.validate_profile(profile_dict)` avant de construire `ProfileData`, exactement comme `cli.py::_load_profile()`, pour que les deux points d'entrée du produit partagent la même garantie. Effort : S (quelques lignes, le schéma est déjà empaqueté et importable).

---

### #3 — Trois sérialisations indépendantes de `Verdict`, une déjà en dérive

`report.py` expose `render_markdown()` et `render_html()`, mais aucun `render_json()`/`to_dict()`. Le format JSON — que l'ADR-0016 mentionne pourtant explicitement (« JSON (team export) ») — n'a jamais de fonction canonique dans `report.py`. Résultat : deux endroits distincts réinventent la sérialisation JSON d'un objet du domaine, avec des champs différents :

**`team.py::export_json`** sérialise `MemberSnapshot` (pas `Verdict` directement, mais dérivé du même verdict) — inclut `name`, `slug`, `level`, `limiting_axis`, `confidence`, `timestamp`.

**`scripts/ci_evaluate.py --format json`** sérialise `Verdict` à la main :

```python
result = {
    "name": verdict.name,
    "level": verdict.level.name if verdict.level else None,
    "limiting_axis": verdict.limiting_axis,
    "axes": [
        {"axe": a.axe, "level": a.level.name if a.level else None, "confidence": a.confidence}
        for a in verdict.axis_scores
    ],
    "red_flags": [...],
    "next_steps": verdict.next_steps,
}
```

**La dérive est déjà visible, pas hypothétique** : `AxisScore` a deux champs supplémentaires que `render_markdown()`/`render_html()` affichent tous les deux — `evidence` (liste des preuves observées) et `variance` (signal de pic isolé, ex. hyperfocus, cf. `model.py` docstring et ADR-0006). Aucun des deux n'apparaît dans le JSON de `ci_evaluate.py`. Un consommateur du JSON CI (dashboard, second outil, IA en aval) perd silencieusement l'explicabilité que le reste du produit (rapports MD/HTML) met justement en avant comme argument central (« Explainability 4/5 » dans le tableau du README) — la version JSON, elle, est structurellement moins explicable que les deux autres formats, sans que ce soit documenté ni testé nulle part.

**Pourquoi c'est un finding architecture et pas juste un bug de script** : c'est l'absence d'un point de sérialisation canonique dans le domaine (`model.py` ou `report.py`) qui rend cette dérive possible et invisible — chaque nouveau consommateur du `Verdict` réinvente sa propre projection, sans contrat partagé ni test de régression qui vérifierait que les trois exports restent alignés sur les mêmes champs.

**Recommandation** : ajouter un `verdict_to_dict(verdict: Verdict) -> dict` unique dans `report.py` (aux côtés de `render_markdown`/`render_html`), incluant `evidence` et `variance`, et faire consommer cette fonction par `ci_evaluate.py` et par `team.py::export_json` (ce dernier ajoute son propre enveloppe équipe autour). Un test de non-régression sur les clés produites fermerait la boucle. Effort : S-M.

---

### #4 — `docs/architecture.mmd` : les 2 scripts shell toujours absents

Depuis le 23/08, `generate_profile.py`, `ci_evaluate.py` et `benchmark.py` ont été ajoutés au sous-graphe `Scripts`. Il manque encore `release_hackathon.sh` et `run_all_examples.sh` — les deux seuls scripts non-Python du dossier, ce qui explique probablement l'oubli (le diagramme semble avoir été mis à jour en scannant les `.py`). Mineur, mais autant fermer le finding du 23/08 complètement plutôt qu'aux trois quarts.

---

### #5 — Import tardif de `questions.py` sans justification structurelle (mineur)

`scoring.py::_questions_for()` et `cli.py::_merge_answer()` importent tous les deux `from .questions import QUESTION_IDS` **à l'intérieur** de la fonction plutôt qu'en tête de module — un pattern habituellement réservé à casser un cycle d'imports. Ici, `questions.py` ne dépend de rien (ni `model`, ni `scoring`, ni `cli`) : un import en tête de fichier dans `scoring.py` et `cli.py` ne créerait aucun cycle. L'indirection n'a donc pas de rôle architectural — probablement un résidu de refactor (le commentaire de `cli.py` référence « B3 : Matching par ID de question (stable) », suggérant un ajout tardif). Sans impact fonctionnel ; à nettoyer seulement par cohérence de style avec le reste du fichier (tous les autres imports internes sont en tête).

## 3. Ce que je n'ai pas vérifié (résidu, pas un finding)

- `EXTENDING.md` et le contrat de plugin/hooks qu'il décrit (mentionné en Phase 4 optionnelle du plan hackathon) — pas lu en détail, pourrait révéler d'autres frontières si un système de hooks existe déjà en code.
- `scripts/generate_profile.py` en détail (au-delà de ce que `performance-deep-dive.md` en dit) — je m'appuie sur sa signature (`generate_profile(repo, user, verbose) -> dict`) vue depuis `ci_evaluate.py`, pas sur une lecture complète du fichier ; le contrat exact de son dict de sortie face au schema JSON n'est pas vérifié ligne à ligne.
- `docs/reviews/core-modules-correctness-security-review.md` — non lu, pourrait recouper certains findings ci-dessus sous un autre angle.

## 4. Priorisation

1. **#2 (schema bypass en CI)** — S, quelques lignes, referme un vrai trou de garantie sur un chemin qui tourne à chaque push de PR.
2. **#1 (slug non salé sur `evaluate`/`interrogate`)** — décision à trancher (documenter le périmètre réel de l'ADR-0007 ou étendre le sel à `report.py`), pas juste un fix mécanique — à traiter avant toute publicité RGPD forte sur ce produit.
3. **#3 (sérialisation JSON dupliquée)** — S-M, ferme une dérive déjà réelle (champs manquants) et protège contre la prochaine.
4. **#4 et #5** — cosmétique/style, à faire en passant si un des trois points ci-dessus est touché.

## Coverage

- **Scanned** : `docs/architecture.mmd`, `docs/adr/0001` à `0013` et `0016` (14 des 16 ADR — `0014`/`0015` non lues, hors-scope architecture logicielle : vidéo et choix CLI-vs-web déjà tranché), `src/laivelup/*.py` (10 fichiers, intégralité), `scripts/ci_evaluate.py`, `scripts/version_bump.py`, `.github/workflows/{ci,release,aidd-eval}.yml`, `pyproject.toml`.
- **Skipped** : `scripts/generate_profile.py`, `scripts/demo.py`, `scripts/benchmark.py`, `scripts/calibrate*.py`, `scripts/apply_calibration_fix.py` (lus indirectement via les audits précédents, pas relus ligne à ligne ici) ; `docs/EXTENDING.md`, `docs/reviews/core-modules-correctness-security-review.md` ; exécution live (pas d'outil d'exécution disponible dans cet environnement, comme les audits précédents) — analyse fondée sur lecture statique croisée code + ADR, sans modification apportée au code.
