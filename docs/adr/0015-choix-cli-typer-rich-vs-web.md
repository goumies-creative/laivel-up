# ADR-0015 : Choix CLI (Typer + Rich) vs Application Web

**Status** : Accepted  
**Date** : 2026-08-22  
**Décideurs** : Romy Alula

## Contexte

Le hackathon AIDD impose un livrable « outil d'évaluation ». Le site officiel mentionne plusieurs formats possibles (CLI, web, API). Ce choix impacte l'architecture, l'UX, et la stratégie marketing.

## Contexte personnel

> « J'aime interagir avec mon PC via CLI depuis toute petite quand mon père ingénieur en informatique m'a appris des commandes basiques en réponse à mes questions. Pratique pour interagir avec le filesystem avec ou sans IA. Preuve de cet attrait = GC CLI. »

CLI = interaction naturelle avec le filesystem, avec ou sans IA. Pas de serveur, pas de DB, pas d'auth. `pip install` + `laivelup evaluate` = friction zéro.

## Décision

**CLI Typer + Rich** comme interface unique.

### Critères techniques validés

| Critère | Typer | Click | argparse |
|---------|-------|-------|----------|
| Type hints natifs | ✅ | ❌ | ❌ |
| Auto-completion shell | ✅ | ✅ | ❌ |
| Intégration Rich | ✅ | Partiel | ❌ |
| Validation `--help` | ✅ | ✅ | Basique |

| Critère | Rich | textual | plain |
|---------|------|---------|-------|
| Markdown rendering | ✅ | ✅ | ❌ |
| Tables | ✅ | ✅ | ❌ |
| Progress bars | ✅ | ✅ | ❌ |
| Emoji handling | ✅ | ✅ | ❌ |
| Sortie HTML | Via report | ❌ | ❌ |

### Sous-commandes

- `laivelup evaluate` : évaluation standard
- `laivelup interrogate` : mode entretien guidé (La Décodeuse)
- `laivelup team create|evaluate|export` : suivi d'équipe

### Sortie duale MD + HTML

- **HTML** : humains, lecture confortable (navigateur), styles
- **Markdown** : devs, IA (ingestion LLM), archivage git, diff lisible
- **Raison** : « Lire des fichiers .md en grande quantité est épuisant. »

### Mode `interview` (La Décodeuse)

- **Justifié** : implémente le pattern « refus > deviner », questions ciblées, rotation anti-boucle
- **Stratégie marketing** : point d'entrée découverte La Décodeuse + Goumies Creative
- **Risque assumé** : peut être demandé de retirer post-hackathon → repo privé conservé

### Stratégie repo

- Repo privé (`goumies-creative-laivel-up`) : working copy, historique complet
- Repo public (même nom) : version finale propre pour hackathon + suite
- `git filter-repo` ou rebase si nettoyage nécessaire

## Conséquences

### Positives
- Zéro dépendance externe (pas de serveur, DB, auth)
- Portable : `pipx install laivelup` / `uv tool install laivelup`
- Intégrable CI/CD, scripts, hooks git
- Démo vidéo asciinema native
- Marketing premium : calling card technique

### Négatives / Risques (mitigés)

| Risque | Mitigation |
|--------|------------|
| Courbe apprentissage pour non-CLI | `--help` riche, docs, MODELS.md |
| Pas d'UI visuelle « sexy » pour juges non-tech | Sortie HTML soignée |
| Mode interview = complexité code | Isolé en commande séparée |
| Marketing Décodeuse = risque de retrait | Repo privé conservé |

**Note** : les conséquences négatives sont mitigées par le **profil technique du jury** (Lead Tech) et l'**ICP de cet outil** (Lead Tech, devs AIDD).

## Alternatives rejetées

| Alternative | Raison |
|-------------|--------|
| Web (FastAPI + React) | Sur-ingénierie, déploiement, maintenance, hors scope hackathon |
| Click | Pas de type hints natifs, moins d'intégration Rich |
| Textual | TUI complète = overkill, pas de sortie HTML native |
| Argument parsing manuel | Réinventer la roue, pas de validation |

## Liens

- Code : `src/laivelup/cli.py`, `src/laivelup/encoding.py`
- Tests : `tests/test_cli*.py`, `tests/test_encoding.py`
- Docs : `README.md`, `docs/asciinema-cli-demo-workflow.md`
