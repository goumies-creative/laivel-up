# Générer un profil depuis un repo

LAIVEL UP peut générer un profil AIDD **depuis un clone local** (zéro réseau, zéro token).

## Usage rapide

```bash
# Depuis le repo cloné
python scripts/generate_profile.py /chemin/vers/repo --user alice --out profil.json

# Puis évaluer
laivelup evaluate profil.json
```

## Commande complète

```bash
python scripts/generate_profile.py \
  --user "alice" \
  --repo "/chemin/vers/mon-projet" \
  --out "profil-alice.json" \
  --verbose
```

### Options

| Option | Description | Défaut |
|--------|-------------|--------|
| `--user`, `-u` | Handle git de l'utilisateur (requis) | — |
| `--out`, `-o` | Fichier de sortie | `profil.json` |
| `--verbose`, `-v` | Affiche les détails d'extraction | false |
| `repo` | Chemin vers le dépôt git cloné (positional) | — |

## Ce qui est analysé

Le script examine le dépôt git pour extraire les **traces AIDD** :

| Trace | Source | Logique |
|-------|--------|---------|
| `pr_sizes` | Git log (merges) | Nombre de fichiers modifiés → S/M/L/XL |
| `context_versioned` | Fichiers du repo | `CLAUDE.md`, `AGENTS.md`, `.cursorrules`, etc. |
| `agent_rules_versioned` | Dossiers du repo | `.github/workflows/`, `.agents/`, `skills/`, etc. |
| `retry_loops` | Fichiers CI | Patterns `retry`, `rerun`, `continue-on-error` |
| `retries_after_fact` | Messages de commit | Ratio commits "fix" / total |
| `retries_triangulated` | Auto | `True` si données API corroborent |
| `parallel_projects` | Branches git | Branches actives non-merged |
| `projects_completed` | Branches git | Branches merged |
| `agents_autonomous` | Workflows CI | Patterns `schedule`, `dispatch` |
| `prompts` | Fichiers du repo | `prompts/`, `.cursorrules`, etc. |

## Limites

- **PR sizes** : Basé sur le nombre de fichiers modifiés (pas lignes). Moins précis que l'API GitHub.
- **Repos sans merges** : Si l'utilisateur n'a pas de commits de merge, `pr_sizes` sera vide.
- **Forks** : Le script analyse le clone local, pas les forks distants.

## Exemple de sortie

```json
{
  "name": "mon-projet-alice",
  "declared_level": null,
  "traces": {
    "pr_sizes": ["M", "M", "L", "S"],
    "context_versioned": true,
    "agent_rules_versioned": false,
    "retry_loops": false,
    "retries_after_fact": 0.16,
    "retries_triangulated": true,
    "parallel_projects": 1,
    "projects_completed": 1,
    "agents_autonomous": false,
    "prompts": false
  },
  "answers": {},
  "meta": {
    "source": "local_repo",
    "repo_path": "/chemin/vers/repo",
    "user": "alice",
    "generated_by": "generate_profile.py"
  }
}
```

## API GraphQL (v2)

Une intégration GitHub API GraphQL est prévue post-hackathon pour :
- Extraire les PR sizes précises (additions/deletions)
- Détecter les retry loops via workflow runs
- Corréler les données avec l'API (retries_triangulated)
- Supporter les repos distants sans clone local

Voir `docs/plans/2026-08-23-github-api-integration-plan.md` pour le plan complet.
