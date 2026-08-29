# CLI Ergonomics Evaluation — LAIVEL UP

## Summary

**Score : 7.5 / 10**

La CLI LAIVEL UP est bien structurée avec une hiérarchie de commandes claire (verb-noun), un bon support français, et des erreurs colorées via Rich. Les conventions sont globalement respectées (flags `--snake-case`, exit codes documentés, `NO_COLOR` supporté). Cependant, plusieurs lacunes limitent l'ergonomie professionnelle : pas de `__main__.py` (impossible de lancer via `python -m`), une exception non interceptée dans `team create` pour les noms invalides, un `--fail-on` silencieux quand le verdict est `null`, et l'absence d'option `--no-html` sur `team evaluate`.

## Findings

| # | Category | Severity | Issue | Location | Suggested fix |
|---|----------|----------|-------|----------|---------------|
| 1 | error-handling | P1 | `team create` crash avec un traceback quand le nom d'équipe contient des espaces (ex: "Equipe Test"). La `ValueError` levée par `_validate_team_name` n'est pas interceptée par le CLI layer. | `cli.py:414` → `team.py:36` | Ajouter un `try/except ValueError` dans `team_create` avec `error_console.print()` + `raise typer.Exit(code=2)` |
| 2 | missing-module | P1 | Absence de `__main__.py` — `python -m laivelup` échoue avec "No module named laivelup.__main__". Incompatible avec les patterns de debug standard (`python -m laivelup --help`). | `src/laivelup/` | Créer `src/laivelup/__main__.py` contenant `from laivelup.cli import app; app()` |
| 3 | error-handling | P2 | `--fail-on` avec un nom de niveau inconnu (ex: `WHITES`) est silencieux quand le verdict est `null` (level=None). La condition `if fail_on and verdict.level is not None` ignore le cas où le verdict n'est pas décidé. | `cli.py:317-332` | Ajouter un avertissement quand `fail_on` est fourni mais `verdict.level is None` : "Avertissement : verdict non décidé, --fail-on ignoré" |
| 4 | inconsistency | P2 | `team evaluate` ne dispose pas de l'option `--no-html` alors que `evaluate` l'a. Les deux commandes génèrent des rapports Markdown+HTML. | `cli.py:423-453` | Ajouter `--html/--no-html` à `team_evaluate` |
| 5 | ux | P2 | `team create help` crée accidentellement une équipe nommée "help". L'argument positionnel `name` n'a pas de validation pour les mots-clés de commande. | `cli.py:406` | Documenter que le nom est valide tant qu'il passe la regex alphanumérique, ou ajouter un warning pour les noms collant à des sous-commandes |
| 6 | error-handling | P2 | Le message d'erreur "Membres disponibles :" dans `team evaluate` affiche une liste vide quand l'équipe n'existe pas (fichier JSON absent). | `cli.py:438-440` | Conditionner l'affichage sur `team.members.items()` non vide, ou afficher "Aucun membre" |
| 7 | conventions | P3 | Le `--help` racine affiche "Show this message and exit." en anglais alors que tout le reste est en français. C'est un comportement par défaut de Typer. | `cli.py:65-68` | Passer `rich_markup_mode="rich"` et/ou traduire via `app = typer.Typer(..., ...)`. Vérifier si Typer supporte `help_strings` |
| 8 | conventions | P3 | `--fail-on` ne propose pas de validation parmi les valeurs connues (RED, BLUE, GREEN, etc.) dans le help text. L'utilisateur doit deviner les noms valides. | `cli.py:286-287` | Ajouter la liste des valeurs valides dans le help : `"Fail si niveau inférieur (valeurs : RED, BLUE, GREEN, COPPER, SILVER, GOLD)"` |
| 9 | conventions | P3 | Le paramètre `format` dans `team_export` utilise un `str` au lieu d'un `typer.Enum` pour les choices. | `cli.py:459` | Utiliser `format: str = typer.Option("md", ...)` avec `typer.Choice(["md", "html", "csv", "json"])` pour auto-validation |
| 10 | conventions | P3 | `--verbose` et `--quiet` sont mutuellement exclusifs mais pas vérifiés. `--json --quiet` est redondant (les deux activent JSON). | `cli.py:295` | Documenter dans le help que `--quiet` implique `--json`, ou ajouter une validation |
| 11 | consistency | P3 | La description de `schema` dans `--help` racine affiche "schema" sans article, mais dans le schema JSON c'est "schema". Cohérent, mais "schema" pourrait être "schema" avec un accent si c'est le choix français. | `cli.py:76`, help output | Conserver "schema" (anglicisme technique accepté) ou passer à "schéma" — choisir une convention et la tenir |
| 12 | accessibility | P3 | `--help` ne mentionne pas `NO_COLOR` ni `FORCE_COLOR` bien qu'ils soient supportés en interne. | `cli.py` module docstring | Ajouter une note dans la docstring ou le help sur le support `NO_COLOR` / `FORCE_COLOR` |

## Strengths

- **Hiérarchie verb-noun cohérente** : `evaluate`, `interrogate`, `team create/evaluate/export/opt-out/remove`. Convention bien tenue.
- **Exit codes documentés** : 0/1/2/3 avec signification claire dans la docstring et le schema JSON. Pratique pour le CI.
- **Support NO_COLOR complet** : `os.environ.get('NO_COLOR')` respecté, `Console(no_color=...)` propagé. Fallback ASCII pour Windows legacy.
- **Rich tables formatées** : Le verdict s'affiche dans une table Rich avec colonnes Axe/Niveau/Confiance. Lisible et esthétique.
- **Schema JSON auto-découverte** : `laivelup schema` expose un document machine-readable pour les agents IA. Design thought-through.
- **Gestion des accents français** : Toutes les sorties utilisent les bons accents (é, è, ê, à, ç). Le module `encoding.py` gère UTF-8 cross-platform.
- **Borne de taille fichier** : `_load_profile` vérifie `MAX_JSON_MB` (2 Mo) avant parsing. Protection DoS.
- **Tty-aware output** : `use_json = json_output or quiet or not TTY` — JSON en mode pipé/CI, Rich tables en mode interactif. Pattern correct.
- **Help text des sous-commandes** : Les descriptions de `team` sont claires et complètes.
- **Short flags** : `-v`, `-j`, `-q`, `-V`, `-f` disponibles pour les flags courants. Bonne ergonomie.

## Recommendations (ordered by priority)

1. **[P1] Intercepter les ValueError dans les commandes `team`** : La plupart des erreurs métier (`_validate_team_name`, `load_team` pour un fichier absent) lèvent des `ValueError` qui ne sont pas interceptées. Leur `try/except` manquant produit des tracebacks bruts. Pattern à appliquer :
   ```python
   try:
       team = create_team(name, member_list)
   except ValueError as e:
       error_console.print(f'[bold red]{e}[/bold red]')
       raise typer.Exit(code=2)
   ```

2. **[P1] Ajouter `__main__.py`** : `python -m laivelup` est un pattern standard pour le debug et les tests. Fichier minimal :
   ```python
   from laivelup.cli import app
   app()
   ```

3. **[P2] Avertir quand `--fail-on` est ignoré** : Quand le verdict est `null` et que `--fail-on` est fourni, ajouter un avertissement sur stderr pour éviter la confusion silencieuse.

4. **[P2] Unifier `--no-html` entre `evaluate` et `team evaluate`** : Les deux commandes génèrent des rapports. L'option devrait être disponible partout.

5. **[P3] Valider `--format` avec `typer.Choice`** : Remplacer le check manuel par `typer.Choice(["md", "html", "csv", "json"])` pour auto-validation et aide contextuelle.

6. **[P3] Traduire les strings Typer par défaut** : "Show this message and exit." pourrait être traduit en français via la configuration Typer.

## Coverage

- **Commands testées** : `--help`, `evaluate`, `evaluate --help`, `team`, `team --help`, `team create`, `team create --help`, `team evaluate`, `team evaluate --help`, `team export`, `team export --help`, `team remove`, `schema`
- **Flags testés** : `--version` / `-V`, `--help`, `--out`, `--html/--no-html`, `--verbose` / `-v`, `--json` / `-j`, `--fail-on`, `--fields`, `--quiet` / `-q`, `--format` / `-f`, `--purge`, `--enable/--disable`, `--max-turns`
- **Error paths testés** : fichier introuvable, JSON invalide, profil invalide (champ requis manquant), declared_level inconnu, --fail-on niveau inconnu, team introuvable, membre introuvable, nom d'équipe avec espaces, sous-commande inexistante
- **Non testé** : `--fields` (filtrage JSON), `interrogate` (mode interactif), `--verbose` en Rich mode, output sur terminal large/étroit, comportement Windows legacy, `NO_COLOR=1` avec Rich tables
