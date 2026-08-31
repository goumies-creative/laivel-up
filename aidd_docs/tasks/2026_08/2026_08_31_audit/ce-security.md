# CE Review: goumies-creative-laivel-up — ce-security-reviewer

## Verdict

**ship** — Aucune vulnérabilité P0/P1 identifiée. Le projet présente une posture de sécurité solide pour un outil CLI hackathon. Les défenses sont en place : validation JSON Schema (additionalProperties:false), escaping HTML systématique, subprocess sans shell=True, atomic writes, RGPD (opt-out/purge/HMAC-SHA256). Quelques améliorations mineures sont documentées en dessous.

## Findings

| Sev | Location | Issue | Suggested fix | Effort |
|-----|----------|-------|---------------|--------|
| P2 | `scripts/demo.py:47-52` | `subprocess.run(cmd.split())` sans timeout — si le CLI attend un TTY, le process bloque indéfiniment | Ajouter `timeout=60` au `subprocess.run()` | XS |
| P3 | `pyproject.toml:159` | Skip B601 (subprocess shell) sans justification — aucun `shell=True` dans le codebase | Supprimer `"B601"` des skips ou documenter que c'est un filet de sécurité défensif | XS |
| P3 | `aidd-eval.yml:102-106` | L'escaping JS (`replace(/`/g, '\\`')`) ne couvre pas les séquences `</script>` dans le verdict Markdown — risque théorique si un nom de repo contient du HTML | Ajouter `replace(/<\//g, '<\\/')` ou sanitizer le contenu du verdict avant interpolation | XS |
| P3 | `tests/security/` | Absence de test d XSS pour les exports `team.export_html()` avec des noms de membre contenant du HTML/malicious payload | Ajouter un test qui crée un membre `<script>alert(1)</script>` et vérifie que `export_html()` l'échappe | S |

## Scénarios d'attaque testés

### 1. Profil JSON malveillant (prototype pollution)
**Testé via** : `tests/security/test_json_injection.py` + lecture `schema.py`

- `__proto__: {admin: true}` → **Bloqué** : le schema a `additionalProperties: false` sur la racine (profile.schema.json:93). jsonschema rejette les clés inconnues. Le fallback `_validate_minimal()` n'est pas sensible au prototype pollution car Python `dict` ne propage pas `__proto__` comme clé spéciale.
- `constructor.prototype` → **Bloqué** : même mécanisme.
- Types erronés (`retries_after_fact: "NOT_A_NUMBER"`) → **Bloqué** : schema exige `type: number` (profile.schema.json:51) + `normalize_profile()` valide les types (scoring.py:96-105).
- Valeurs négatives (`parallel_projects: -1`) → **Bloqué** : schema exige `minimum: 0` (profile.schema.json:63) + `normalize_profile()` (scoring.py:126).
- Clé-value de 10 Ko → **Bloqué** : taille max 2 Mo (cli.py:83-86).

### 2. Path traversal via --out
**Testé via** : `tests/security/test_path_traversal.py` + lecture `report.py`

- `--out ../../tmp/evil` → **Bloqué** : `write_reports()` vérifie `md.resolve().is_relative_to(out_dir_resolved)` (report.py:1011-1012). Un `..` dans le chemin résolu sort du répertoire cible → `ValueError`.
- Team name `../../etc` → **Bloqué** : `_validate_team_name()` restreint à `[a-zA-Z0-9_-]{1,64}` (team.py:36).

### 3. Injection PR via verdict.md dans aidd-eval.yml
**Scénario** : Un attaquant crée un repo avec un nom malveillant (ex: `repo$(malicious)`) et ouvre une PR.

- `generate_profile.py:_sanitize_email()` nettoie le handle git (line 241) mais pas le nom du repo (`repo_path.name`).
- Cependant, dans le contexte CI GitHub Actions, le nom du repo est contrôlé par le propriétaire du repo (pas par un tiers).
- Le verdict.md est échappé pour les template literals JS (backticks, `$`, `\`) dans le workflow (line 102-106).
- Le contenu est rendu en Markdown par GitHub, qui sanitarise le HTML dans les commentaires.
- **Risque résiduel** : Très faible — nécessiterait un repo avec nom malveillant contrôlé par l'attaquant.

### 4. XSS dans les rapports HTML
**Testé via** : Lecture de tous les chemins de rendu HTML

- `report.py` : Toutes les sorties utilisateur passent par `html.escape()` — `verdict.name` (line 494), `level_label()` (line 438), `axis_label()` (line 445), `evidence` (line 286), `f.titre/constat/source/question` (lines 454-456), `next_steps` (line 467), `data_errors` (line 450), glossaire terms/definitions (lines 99, 101-102, 407-409), references (lines 418-419).
- `team.py` : `html_escape()` sur `m.name`, `team_slug`, `level`, `axis_label()` (lines 351-353, 366-367, 370).
- `calibrate_dashboard.py` : `escape()` sur tous les noms de profils et labels (lines 56-59, 86-93, 106, 109).
- Les couleurs CSS proviennent de `LEVEL_COLORS` (dictionnaire hardcodé), pas de données utilisateur.
- **Résultat** : Aucune injection XSS trouvée.

### 5. Subprocess injection
**Tous les scripts analysés** :

- `generate_profile.py:25-33` : `subprocess.run(['git', '-C', str(repo), *args], timeout=30)` — `shell=False`, args en liste, timeout=30.
- `benchmark.py:34-38` : `subprocess.run([sys.executable, '-m', 'laivelup.cli', *cmd], timeout=30)` — idem.
- `version_bump.py:48-56` : `subprocess.run(['git', ...])` — commands hardcodées, pas de shell.
- `demo.py:47-52` : `subprocess.run(cmd.split(), ...)` — cmd est un literal string, pas user-controlled.
- **Aucun `shell=True`** dans tout le codebase. Le skip B601 est inutile mais pas dangereux.

### 6. RGPD — Données personnelles
**Vérifié dans** : `team.py`, `utils.py`

- **Opt-out (Art. 21)** : `set_opt_out()` (team.py:242-246) + `evaluate_member()` vérifie `member.opt_out` avant évaluation (line 180-181) + tous les exports filtrent les membres opt-out (lines 251, 266-270, 293-296, 326-327, 356-358).
- **Effacement (Art. 17)** : `remove_member(team, slug, purge=True)` supprime le membre ET son historique (line 231-232).
- **Pseudo-anonymisation** : HMAC-SHA256 avec sel par équipe (`generate_team_salt()` → `os.urandom(16).hex()`) — résistant dictionnaire (utils.py:22-27).
- **Aucune donnée sensible stockée** : pas d'email, pas d'IP, pas de neurotype. Le profil contient uniquement des traces techniques (commits, PR, contexte).
- **Exports montrent le nom réel** (team.py:291, 331, 351) : par design — le chef d'équipe voit les noms dans les rapports locaux. Le slug est l'identifiant partagé.

### 7. Secrets en dur
**Aucun secret trouvé** dans le code source :
- `release.yml:68` : `${{ secrets.PYPI_API_TOKEN }}` — utilise GitHub Secrets correctement.
- Aucune clé API, token ou mot de passe hardcodé dans `src/`, `scripts/`, ou config.

### 8. DoS via fichier volumineux
**Testé via** : `tests/security/test_dos_profil_giant.py`

- `cli.py:83-86` : `MAX_JSON_MB = 2` — vérifié avant chargement.
- `team.py:101-102` : `MAX_TEAM_FILE_MB = 1` — vérifié avant chargement.
- Les deux utilisent `path.stat().st_size` (pas le chargement en mémoire).

## Couverture

| Catégorie | Couvert | Notes |
|-----------|---------|-------|
| XSS (HTML injection) | ✅ | Toutes les sorties HTML échappées via `html.escape()` |
| Path traversal | ✅ | `is_relative_to()` dans report.py + validation regex team names |
| Prototype pollution | ✅ | JSON Schema `additionalProperties: false` + jsonschema validator |
| Subprocess injection | ✅ | Aucun `shell=True`, tous les args en liste, timeouts |
| DoS (taille fichier) | ✅ | Guard 2 Mo (profiles) + 1 Mo (teams) avant chargement |
| Secrets en dur | ✅ | Aucun trouvé, GitHub Secrets utilisé pour PyPI |
| RGPD opt-out/purge | ✅ | Art. 21 + Art. 17 couverts, exports filtrent opt-out |
| Bandit B110 skip | ✅ | Justifié (graceful degradation encoding.py, utils.py) |
| aidd-eval.yml injection | ⚠️ | Escaping JS couvre les template literals ; risque résiduel HTML dans Markdown (faible) |
| Export HTML XSS (team) | ⚠️ | Pas de test spécifique pour noms malveillants dans exports |

## Message final

**Verdict : ship** — 0 P0, 0 P1, 1 P2 (démonstration, timeout subprocess), 3 P3 (theoriques/minimes).

**Top 3 findings :**

1. **`scripts/demo.py:47-52`** — Subprocess sans timeout, risque de blocage si le CLI attend un TTY (P2, démo script, pas en CI).
2. **`tests/security/` (gap)** — Absence de test XSS pour les exports `team.export_html()` avec des noms de membre contenant du HTML (P3, test manquant).
3. **`pyproject.toml:159`** — Skip Bandit B601 (subprocess shell) sans `shell=True` dans le codebase — inutile mais inoffensif (P3, nettoyage).

**Résumé de la posture** : Le projet a une approche défensive mature pour son périmètre (CLI hackathon). La validation d'entrée est en deux couches (JSON Schema + normalize_profile), les sorties HTML sont systématiquement échappées, les subprocess n'utilisent jamais `shell=True`, et les fonctionnalités RGPD (opt-out, purge, pseudo-anonymisation HMAC-SHA256) sont correctement implémentées. La couverture de test security est bonne (5 classes de tests) avec des fixtures dédiées (profils malveillants, géants, injection). Les seuls gaps identifiés sont théoriques ou concernent des scripts de démonstration hors CI.
