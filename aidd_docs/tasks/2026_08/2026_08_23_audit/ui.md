# Codebase Audit: ui — goumies-creative-laivel-up

Produit sans frontend web (CLI Typer/Rich + rapports Markdown/HTML statiques). Les heuristiques classiques (responsive, WCAG runtime) sont peu applicables ; l'audit se concentre sur la cohérence des retours utilisateur en CLI et sur les rapports HTML générés.

- **Date**: 2026-08-23
- **Scope**: `src/laivelup/cli.py`, `src/laivelup/report.py`
- **Health**: fair
- **Findings**: 0 critical, 2 warning, 1 minor

## Findings

| Sev | Category | Location | Issue | Suggested fix | Effort |
| --- | --- | --- | --- | --- | --- |
| 🟡 | ui | `src/laivelup/cli.py:215` | Le message de succès `"Équipe '{team.name}' créée"` (vert, ton positif) laisse croire que l'équipe est persistée et réutilisable, alors que rien n'est sauvegardé (racine du problème : code-quality/architecture). | Ajuster le message pour signaler l'absence de persistance tant que le fix n'est pas livré, ou livrer le fix | S |
| 🟡 | ui | `src/laivelup/cli.py:268` | `team export` affiche `"Export : {out_file}"` en vert même quand le fichier exporté est vide (0 membre, 0 historique) — aucun état « équipe vide » n'est signalé. | Ajouter une vérification et un message distinct si `not team.members` avant l'export | S |
| 🟢 | ui | `src/laivelup/report.py:99-149` (`render_html`) | Le rapport HTML généré n'a pas de repère sémantique (`<main>`) autour du contenu ; navigation par landmarks limitée pour un lecteur d'écran. | Envelopper le contenu dans `<main>` | S |

## Top actions

1. Corriger les messages de succès trompeurs sur les commandes `team` — cosmétique mais aggrave la confusion pendant une démo live (cf. finding critique code-quality).

## Coverage

- **Scanned**: ui — inspection statique des retours console (`rich`) dans `cli.py` et des rapports HTML générés par `report.py`/`team.py`.
- **Skipped**: no url provided, runtime a11y pass skipped, static inspection only. Pas de frontend web à proprement parler (produit CLI) : les heuristiques responsive/breakpoints ne s'appliquent pas ; le fallback ASCII (`encoding.py`, dégradation propre sur terminaux non-UTF-8) est un point positif noté ici plutôt qu'en finding.
