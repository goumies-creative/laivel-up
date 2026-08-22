# ADR-0016 : Sortie double format Markdown + HTML

**Status** : Accepted  
**Date** : 2026-08-22  
**Décideurs** : Romy Alula

## Contexte

L'évaluation produit un verdict structuré. Deux audiences cibles : humains (juges, clients) + machines (IA, CI, archivage).

## Décision

Générer **les deux formats** à chaque évaluation.

### Implémentation

| Format | Fonction | Usage |
|--------|----------|-------|
| Markdown | `render_markdown()` | Base, lisible, diff-friendly, archivage git |
| HTML | `render_html()` | Navigateur, styles, lecture confortable |
| JSON | (team export) | API, ingestion programme |

### Raison humaine

> « Lire des fichiers .md en grande quantité est épuisant. » — HTML = confort lecture (navigateur, styles, scroll)

### Raison machine

> « Devs + IA → MD » — parsing trivial, diff git, embedding LLM

### Rendu

- **MD** : tableaux ASCII, emojis Rich, sections structurées
- **HTML** : CSS inline, badges colorés, tableaux stylés, sections transparence

### Commandes

```bash
laivelup evaluate profil.json              # MD + HTML
laivelup evaluate profil.json --no-html    # MD seul
laivelup team export Alpha --format html   # HTML seul
```

## Conséquences

### Positives
- Lecture confortable pour les juges (HTML)
- Archivage et diff git (MD)
- Ingestion IA (MD)
- Export multi-format (team export)

### Négatives
- Double rendering = 2x le travail (mitigé : fonctions séparées)

## Liens

- Code : `src/laivelup/report.py`
- Tests : `tests/test_report.py`
