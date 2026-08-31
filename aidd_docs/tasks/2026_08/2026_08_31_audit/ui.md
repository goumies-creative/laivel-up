# Codebase Audit: ui — goumies-creative-laivel-up

CLI Python Typer/Rich + rapports Markdown/HTML statiques. Pas de frontend web → a11y runtime SKIPPED. L'audit couvre : sorties terminal (messages, aide, erreurs), rapports HTML générés (hiérarchie, sémantique, contraste), cohérence linguistique.

- **Date**: 2026-08-31
- **Scope**: `src/laivelup/cli.py`, `src/laivelup/report.py`, `src/laivelup/calibrate_dashboard.py`, `src/laivelup/team.py`
- **Health**: good
- **Findings**: 0 critical, 3 warning, 5 minor

## Findings

| Sev | Category | Location | Issue | Suggested fix | Effort |
| --- | --- | --- | --- | --- | --- |
| 🟡 | ui | `src/laivelup/calibrate_dashboard.py:108` | Cartes axes calibration : `<div class="axis-card">` sans `role="listitem"` ni `aria-label` — navigation landmarks/pour lecteur d'écran impossible sur les données de calibration. (Contrairement à `report.py:280` qui utilise `role="listitem"` + `aria-label` correctement.) | Ajouter `role="listitem"` et `aria-label` synthétique sur chaque `.axis-card`, comme dans `report.py` | S |
| 🟡 | ui | `src/laivelup/team.py:371-408` | Export HTML équipe : pas de `<meta name="viewport">` ni `<meta charset>` — rendu non responsive sur mobile, encodage non garanti. (Calibrate dashboard et verdict report ont ces balises.) | Ajouter `<meta charset="utf-8">` et `<meta name="viewport" ...>` dans le `<head>` | S |
| 🟡 | ui | `src/laivelup/team.py:341-412` | Export HTML équipe : thème light (fond blanc, `#ddd` borders) vs dark theme des deux autres dashboards — incohérence visuelle si les rapports sont consultés ensemble. | Unifier le thème ou documenter le choix intentionnel | M |
| 🟢 | ui | `src/laivelup/calibrate_dashboard.py:305-308` | Tableau preuve calibration : pas de `<caption>` ni `scope="col"` sur `<th>` — repère sémantique manquant pour les lecteurs d'écran. | Ajouter `<caption>Tableau de preuve calibration</caption>` et `scope="col"` sur les `<th>` | S |
| 🟢 | ui | `src/laivelup/team.py:729-761` | `--format` dans `team export` accepte n'importe quelle string — validation manuelle dans le code. Un Typer `Enum` donnerait une auto-validation + aide intégrée. | Remplacer `format: str` par un Enum Typer `FormatChoice` | S |
| 🟢 | ui | `src/laivelup/cli.py:280-291` | `_nes_box` n'échappe pas les crochets dans les lignes d'entrée — si un futur appelant passe une string avec `[test]`, Rich l'interprèterait comme markup. Aujourd'hui toutes les chaînes sont hardcodées (pas de bug actuel), mais c'est un piège latent. | Échapper les crochets ou documenter la contrainte | S |
| 🟢 | ui | `src/laivelup/team.py:280,390` | Horodatage export MD/JSON équipe : `datetime.now()` sans timezone — résultat dépend du timezone système. L'export JSON utilise `.isoformat()` (plus informatif) mais les deux manquent de timezone explicite. | Utiliser `datetime.now(timezone.utc)` ou documenter la convention | S |
| 🟢 | ui | `src/laivelup/cli.py:492-508` | Help `interrogate` : pas d'exemple montrant `--max-turns` avec une valeur concrète dans l'epilog. Le help standard montre la valeur par défaut (6) mais pas un cas d'usage. | Ajouter un exemple `--max-turns 3` dans l'epilog (déjà dans la docstring mais pas dans l'epilog Typer) | S |

## Top actions

1. **Aligner la sémantique ARIA du calibrate_dashboard** sur celle du verdict report (finding 🟡 `calibrate_dashboard.py:108`) — même pattern, même niveau d'effort, cohérence d'accessibilité entre les deux dashboards HTML.
2. **Ajouter les balises `<meta>` manquantes dans l'export HTML équipe** (finding 🟡 `team.py:371`) — le viewport et charset sont déjà présents dans les deux autres templates, c'est un oubli de copie.
3. **Unifier ou documenter le thème** des exports équipe vs rapports (finding 🟡 `team.py:341`) — si l'intention est de distinguer les "rapports officiels" (dark) des "exports partagés" (light), le documenter ; sinon harmoniser.

## Coverage

- **Scanned**: cli.py (retours console, messages d'aide/erreur, Rich markup, encoding fallback), report.py (HTML généré — hiérarchie headings, contraste, sémantique ARIA, `<main>`), calibrate_dashboard.py (HTML calibration — sémantique, structure), team.py (exports HTML/MD/JSON — balises, cohérence thème)
- **Skipped**: no url provided, runtime a11y pass skipped, static inspection only. Pas de frontend web : heuristiques responsive/breakpoints non applicables. Le fallback ASCII (`encoding.py`) est un point positif (dégradation propre sur terminaux legacy) — noté ici plutôt qu'en finding.

### Résolution audit 2026-08-23

| Finding précédent | Statut |
| --- | --- |
| `report.py` sans `<main>` | ✅ Corrigé — `<main>` présent (ligne 973) |
| `team export` succès sur équipe vide | ✅ Corrigé — vérification `not team.members` avant export (ligne 753) |
| Message succès `team create` trompeur | ⚠️ Toujours présent — le message "Équipe créée" n'indique pas si la persistance a réussi (racine code-quality) |
