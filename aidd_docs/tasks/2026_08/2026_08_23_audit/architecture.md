# Codebase Audit: architecture — goumies-creative-laivel-up

Le point le plus grave de tout l'audit vit ici : la résolution du schéma JSON casse `evaluate`/`interrogate` dès qu'on installe le package comme le recommande le README (`pip install laivel-up`), en violation directe de l'ADR-0011.

- **Date**: 2026-08-23
- **Scope**: codebase entière, conformité aux ADR (`docs/adr/`) et à `docs/architecture.mmd`
- **Health**: poor
- **Findings**: 1 critical, 2 warning

## Findings

| Sev | Category | Location | Issue | Suggested fix | Effort |
| --- | --- | --- | --- | --- | --- |
| 🔴 | architecture | `src/laivelup/schema.py:13` | Violation de conformité ADR-0011 (« pip / pipx / uv install »). `_SCHEMA_PATH = Path(__file__).parent.parent.parent / "schemas" / "profile.schema.json"` n'est valide qu'en install éditable. Après `pip install .`, `pipx install laivelup` ou `uv tool install laivelup` — les 3 méthodes documentées dans le README et l'ADR-0011, et celle recommandée aux juges du hackathon (« Pour les juges » → `pip install laivel-up`) — le fichier n'est plus au chemin relatif attendu : `_load_schema()` lève `RuntimeError`, non rattrapé dans `cli.py:_load_profile`, et `laivelup evaluate` plante dès la première commande. `tests/test_schema_compat.py:1-7` documente déjà ce problème connu (« Contourne le problème de path schema.py installé globalement ») sans jamais le corriger côté production. | Déplacer `schemas/` sous `src/laivelup/schemas/`, référencer via `importlib.resources`, et le déclarer en `package-data` (cf. finding dependencies) | M |
| 🟡 | architecture | `docs/architecture.mmd` | Le diagramme officiel omet 5 des 10 scripts réels de `scripts/` (`generate_profile.py`, `ci_evaluate.py`, `benchmark.py`, `release_hackathon.sh`, `run_all_examples.sh`) — dont les deux qui alimentent `aidd-eval.yml` (commentaire automatique sur les PR), une fonctionnalité visible du produit. | Mettre à jour `docs/architecture.mmd` avec les composants CI-facing manquants | S |
| 🟡 | architecture | `src/laivelup/team.py` (module entier) | Aucune fonction `load_team`/`save_team` : le domaine `Team` n'a pas de couche de persistance, alors que `cli.py` instancie un `Team` neuf à chaque commande. `docs/adr/0007-team-tracker-rgpd-slug-sha256.md` documente le slug RGPD mais ne traite jamais du stockage — la frontière CLI ↔ domaine n'est pas actée par une décision. | Ajouter une ADR dédiée + `load_team`/`save_team` (JSON local, cohérent avec l'approche « zéro réseau ») | M |

## Top actions

1. Corriger la résolution du schéma (`schema.py:13`) avant toute publication — c'est la fonctionnalité principale (`evaluate`) qui est en jeu, pour tout utilisateur passant par une install standard.
2. Documenter une ADR pour la persistance du Team Tracker, puis l'implémenter (cf. code-quality).
3. Rafraîchir `docs/architecture.mmd` pour qu'il reflète les scripts CI réellement utilisés.

## Coverage

- **Scanned**: architecture (conformité `docs/adr/*.md` vs code, `docs/architecture.mmd` vs `scripts/`, `src/`)
- **Skipped**: none
