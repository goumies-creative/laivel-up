---
artifact_contract: aidd-dev-01-plan/v1
artifact_readiness: implementation-ready
product_contract_source: ce-brainstorm
date: 2026-08-23
status: confirmed
execution: code
---

# Plan — Intégration GitHub API (fetch profil distant)

## Objectif

Ajouter à LAIVEL UP la capacité de **générer un profil AIDD depuis un repo GitHub distant** (public ou privé) via API, pour que le lead tech puisse faire :
```bash
laivelup fetch github https://github.com/org/repo --user alice --out profil.json
laivelup evaluate-from github https://github.com/org/repo --user alice
```

Et intégrer l'évaluation en **GitHub Actions** (CI/CD).

---

## Contexte & Décisions

| Sujet | Décision | Rationale |
|-------|----------|-----------|
| **Plateforme** | GitHub seul (v1) | Priorité hackathon ; GitLab v2 |
| **Auth** | PAT (Personal Access Token) via env `GITHUB_TOKEN` | Simple, sécurisé, standard CLI ; GitHub App pour org/enterprise v2 |
| **API** | GraphQL (v4) | Moins d'appels, requêtes précises, pagination native ; expérience utilisateur |
| **Classification PR** | Seuils fixes configurables (`pr_size_thresholds`) | Prévisible, testable, sans LLM |
| **Données** | Repos publics + privés (selon token) | Couvre lead tech interne + externe |
| **CI/CD** | GitHub Action `laivelup/evaluate` | Auto-éval sur PR/push |
| **Scope hackathon** | **Core + générateur local + GitHub Action** | API complète = post-hackathon (complexité réseau/sécurité) |

> **Réalisme hackathon (J-8)** : L'algorithme d'évaluation est **fini et testé**. L'intégration API complète (HTTP, auth, cache, rate-limit, tests d'intégration) prend ~7 jours. Pour le 31/08, on livre : **générateur depuis clone local** (zéro réseau, démo crédible) + **GitHub Action** (CI/CD). L'API GraphQL complète est planifiée post-hackathon.

---

## Architecture Cible (Post-Hackathon)

```
src/laivelup/
├── http.py              # Client HTTP unifié (httpx) : timeout, retry, rate-limit, circuit-breaker
├── config.py            # Config centralisée (pyproject.toml + env)
├── secrets.py           # Gestion PAT : env > config file > keyring > prompt
├── cache.py             # Cache SQLite (~/.cache/laivelup/) TTL 24h
├── platforms/
│   ├── __init__.py
│   ├── base.py          # Protocol PlatformAdapter
│   └── github.py        # GraphQL GitHub + extracteurs traces
├── extractors.py        # Mapping API → ProfileData (PR sizes, harness, etc.)
└── cli.py               # Nouvelles commandes: fetch, evaluate-from
```

---

## Phase 1 — Hackathon (Semaine 1, livrable 31/08)

### P1.1 Générateur depuis clone local (`scripts/generate_profile.py`)
- **Input** : chemin repo local (déjà cloné)
- **Source** : `git log`, `git diff`, fichiers (`CLAUDE.md`, `.github/workflows/`, etc.)
- **Output** : `profil.json` valide (schéma existant)
- **Avantages** : Zéro réseau, zéro auth, démo immédiate, fonctionne hors-ligne

### P1.2 GitHub Action (`action.yml` + `scripts/ci_evaluate.py`)
```yaml
# .github/workflows/aidd-eval.yml
uses: laivelup/evaluate@v1
with:
  repo: ${{ github.repository }}
  user: ${{ github.actor }}
  token: ${{ secrets.GITHUB_TOKEN }}
```
- Récupère PRs/commits de l'auteur via `GITHUB_TOKEN` (permissions `contents: read`)
- Génère profil → évalue → poste commentaire PR avec verdict

### P1.3 Docs
- `docs/FETCHING.md` : Guide génération locale + API future
- `docs/CI_INTEGRATION.md` : Setup GitHub Action

---

## Phase 2 — Post-Hackathon (Semaines 2-3)

### P2.1 HTTP Core (`src/laivelup/http.py`)
- Client `httpx.AsyncClient` + sync wrapper
- Config : `timeout=30s`, `retries=3` (backoff exponentiel), `max_redirects=5`
- Rate limiting : lecture headers `X-RateLimit-Remaining`, `Retry-After`, sleep auto
- Circuit breaker : 5 erreurs 5xx → open 60s
- Logs structurés (JSON) + métriques (latence, erreurs)

### P2.2 Secrets (`src/laivelup/secrets.py`)
```python
def get_github_token() -> str:
    # 1. GITHUB_TOKEN (env)
    # 2. ~/.config/laivelup/credentials.toml [github] token
    # 3. keyring.get_password("laivelup", "github")
    # 4. Prompt interactif (mode interrogate uniquement)
```

### P2.3 Config (`src/laivelup/config.py`)
```toml
# pyproject.toml
[tool.laivelup]
default_platform = "github"
cache_ttl_hours = 24
rate_limit_buffer = 0.1
pr_size_thresholds = { "S": 50, "M": 200, "L": 600, "XL": 9999 }  # lignes changées
```

### P2.4 GitHub Adapter (`src/laivelup/platforms/github.py`)
**GraphQL Queries** (exemples) :

```graphql
# PRs de l'auteur dans le repo (pagination 100)
query($owner: String!, $repo: String!, $author: String!, $cursor: String) {
  repository(owner: $owner, name: $repo) {
    pullRequests(first: 100, author: $author, after: $cursor, states: [MERGED, CLOSED]) {
      pageInfo { hasNextPage, endCursor }
      nodes {
        number, title, additions, deletions, changedFiles
        author { login }
        mergedAt, closedAt
        commits(first: 50) { nodes { commit { additions, deletions } } }
        reviews(first: 10) { nodes { state, author { login } } }
        timelineItems(first: 20, itemTypes: [COMMITTED_EVENT]) { nodes { ... } }
      }
    }
  }
}

# Workflows runs (retry loops, agents)
query($owner: String!, $repo: String!, $actor: String!) {
  repository(owner: $owner, name: $repo) {
    workflowRuns(first: 100, actor: $actor) {
      nodes { conclusion, createdAt, workflow { name }, rerunCount }
    }
  }
}
```

**Extracteurs** (`src/laivelup/extractors.py`) :

| Trace | Logique extraction |
|-------|-------------------|
| `pr_sizes` | `additions + deletions` par PR → seuils config |
| `context_versioned` | Présence `CLAUDE.md` / `AGENTS.md` / `.github/instructions/` |
| `agent_rules_versioned` | Workflows utilisant `actions/` + patterns agents |
| `retry_loops` | `workflowRun.rerunCount > 0` ou re-run check-suite |
| `retries_after_fact` | Commits post-merge / fixup / "fix" dans message / total PRs |
| `retries_triangulated` | `True` si données API corroborent (vs auto-déclaré) |
| `parallel_projects` | PRs/issues ouverts simultanés (fenêtre 30j) |
| `projects_completed` | PRs merged + issues closed (fenêtre 30j) |
| `agents_autonomous` | Workflows `schedule` / `workflow_dispatch` / `repository_dispatch` |
| `prompts` | Fallback si pas context/agents |

### P2.5 Cache (`src/laivelup/cache.py`)
- SQLite `~/.cache/laivelup/github.db`
- Table : `(platform, repo_url, user, fetched_at, data_json)`
- TTL configurable, invalidation `--force-refresh`

### P2.6 CLI Commands (`src/laivelup/cli.py`)
```python
@app.command()
def fetch(
    platform: Platform = typer.Argument(..., help="github"),
    repo_url: str = typer.Argument(..., help="URL repo GitHub"),
    user: str = typer.Option(..., "--user", "-u", help="Handle utilisateur"),
    out: Path = typer.Option(Path("profil.json"), "--out", "-o"),
    force_refresh: bool = typer.Option(False, "--force-refresh"),
) -> None: ...

@app.command()
def evaluate_from(
    platform: Platform = typer.Argument(...),
    repo_url: str = typer.Argument(...),
    user: str = typer.Option(..., "--user", "-u"),
    out: Path = typer.Option(Path("rapports"), "--out"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None: ...
```

### P2.7 Tests d'intégration
- Mocks GraphQL (`tests/mocks/github_graphql.py`)
- Repos test publics (ex: `github/github-docs`, `microsoft/vscode`)
- Snapshots profils générés
- Tests rate-limit, auth expired, repo not found, private sans token

---

## Unités d'Implémentation (IU)

| IU | Description | Fichiers | Dépendances | Durée |
|----|-------------|----------|-------------|-------|
| **IU1** | HTTP Core + Config + Secrets | `http.py`, `config.py`, `secrets.py` | — | 1.5j |
| **IU2** | Cache SQLite | `cache.py` | IU1 | 0.5j |
| **IU3** | GitHub GraphQL Adapter | `platforms/github.py` | IU1, IU2 | 2j |
| **IU4** | Extracteurs traces | `extractors.py` | IU3 | 1.5j |
| **IU5** | CLI fetch / evaluate-from | `cli.py` (modif) | IU1-IU4 | 1j |
| **IU6** | Tests intégration + mocks | `tests/test_github_adapter.py`, `tests/mocks/` | IU3-IU5 | 1j |
| **IU7** | GitHub Action | `.github/workflows/aidd-eval.yml`, `scripts/ci_evaluate.py` | IU5 | 0.5j |
| **IU8** | Docs | `docs/FETCHING.md`, `docs/CI_INTEGRATION.md` | IU1-IU7 | 0.5j |

**Total Phase 2 : ~8.5 jours** (parallélisable IU1+IU2, IU3+IU4)

---

## Phase 1 Hackathon — Unités (Livrable 31/08)

| IU | Description | Fichiers | Durée |
|----|-------------|----------|-------|
| **H1** | Générateur local `scripts/generate_profile.py` | `scripts/generate_profile.py` | 1j |
| **H2** | GitHub Action `laivelup/evaluate` | `.github/workflows/aidd-eval.yml`, `scripts/ci_evaluate.py` | 0.5j |
| **H3** | Docs | `docs/FETCHING.md`, `docs/CI_INTEGRATION.md` | 0.5j |

**Total Phase 1 : ~2 jours** — compatible deadline.

---

## Critères de Succès

### Phase 1 (Hackathon)
- [ ] `python scripts/generate_profile.py /path/to/repo --user alice` → `profil.json` valide
- [ ] GitHub Action poste verdict sur PR test
- [ ] `docs/FETCHING.md` explique les deux approches (local + API future)

### Phase 2 (Post-Hackathon)
- [ ] `laivelup fetch github https://github.com/org/repo --user alice` → profil.json
- [ ] `laivelup evaluate-from github https://github.com/org/repo --user alice` → verdict
- [ ] Rate limit respecté (pas de 403 sur usage normal)
- [ ] Cache fonctionne (2e appel < 100ms)
- [ ] Tests d'intégration passent (mocks + 2 repos publics)
- [ ] Couverture ≥ 85% sur nouveaux modules

---

## Risques & Mitigations

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| GraphQL breaking changes | Faible | Casser adapter | Tests sur repos publics, versionning queries |
| Rate limit GitHub (5000/h) | Moyenne | Échec fetch gros repos | Cache agressif, pagination, buffer 10% |
| Repos privés sans token | Moyenne | Erreur 404 | Message clair : "Token requis pour repo privé" |
| Permissions `GITHUB_TOKEN` Actions | Faible | Action échoue | Doc permissions minimales (`contents: read`) |
| Classification PR sizes imparfaite | Moyenne | Score biaisé | Seuils config, tests sur repos variés, override manuel |

---

## Questions Ouvertes (pour validation finale Phase 2)

1. **GitHub App vs PAT** : Pour org/enterprise, migrer vers GitHub App (installation, permissions fines, rotation auto) ?
2. **GraphQL vs REST hybride** : Certains endpoints (ex: `git/trees` pour fichiers) plus simples en REST ?
3. **Multi-utilisateurs** : `laivelup fetch --all-contributors` pour évaluer toute l'équipe d'un coup ?
4. **Webhooks** : GitHub App webhook `pull_request` → auto-éval push vs polling Actions ?

---

## Fichiers à Créer / Modifier

### Nouveaux (Phase 2)
- `src/laivelup/http.py`
- `src/laivelup/config.py`
- `src/laivelup/secrets.py`
- `src/laivelup/cache.py`
- `src/laivelup/platforms/__init__.py`
- `src/laivelup/platforms/base.py`
- `src/laivelup/platforms/github.py`
- `src/laivelup/extractors.py`
- `scripts/generate_profile.py` (Phase 1)
- `scripts/ci_evaluate.py` (Phase 1)
- `tests/test_github_adapter.py`
- `tests/mocks/github_graphql.py`
- `docs/FETCHING.md`
- `docs/CI_INTEGRATION.md`

### Modifiés
- `src/laivelup/cli.py` (nouvelles commandes)
- `pyproject.toml` (dépendances: `httpx`, `keyring`, `sqlite3` stdlib, config)
- `.github/workflows/aidd-eval.yml` (Phase 1)

---

## Dépendances Externes (nouvelles)

```toml
# pyproject.toml [project.optional-dependencies]
dev = [
    # ... existants
    "httpx>=0.27",      # HTTP client async/sync
    "keyring>=24.0",    # Stockage sécurisé secrets
    "tenacity>=8.2",    # Retry logic (optionnel, httpx a le sien)
]
```

---

## Note sur le Périmètre Hackathon

**Ce plan Phase 2 est HORS périmètre hackathon** (deadline 31/08, J-8).  
Seule la **Phase 1** (générateur local + GitHub Action + docs) est dans le scope.

La Phase 2 est documentée pour :
- Traçabilité décision architecture
- Reprise immédiate post-hackathon
- Alignement équipe / reviewers

**Validation requise** : Confirmer que Phase 1 suffit pour le hackathon, et que Phase 2 est acceptée comme roadmap post-hackathon.