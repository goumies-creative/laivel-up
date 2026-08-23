# Guide .gitignore — Artefacts Générés

Ce document explique les patterns d'ignorance pour les artefacts générés localement ou en CI, et comment les modifier si vous souhaitez versionner certains types.

## Patterns Actuels

| Pattern | Fichiers Concernés | Origine |
|---------|-------------------|---------|
| `correctness_review.json` | Rapport de code review (racine) | `ce-code-review` / reviewers |
| `*.verdict.md` / `verdict.md` | Verdicts d'évaluation CI | `scripts/ci_evaluate.py`, workflow `aidd-eval.yml` |
| `benchmark-results.json` | Résultats de benchmark | `scripts/benchmark.py` |
| `profil.json` / `profil-*.json` | Profils AIDD générés | `scripts/generate_profile.py` |
| `rapports/` | Rapports d'entretien (MD/HTML) | CLI `laivelup evaluate` |

## Comment Versionner un Type d'Artefact

### Option 1 : Versionner un Type Spécifique (ex: verdicts)

Éditez `.gitignore` et **commentez ou supprimez** la ligne concernée :

```gitignore
# Generated artifacts (CI, benchmarks, local runs)
# *.verdict.md          ← décommentez pour versionner les verdicts
# verdict.md
benchmark-results.json
profil.json
profil-*.json
```

Puis ajoutez les fichiers souhaités :
```bash
git add verdict.md mon-verdict.verdict.md
git commit -m "chore: versionner les verdicts d'évaluation"
```

### Option 2 : Versionner Tous les Artefacts Générés

Supprimez tout le bloc `# Generated artifacts...` :

```gitignore
# Generated artifacts (CI, benchmarks, local runs)
# *.verdict.md
# verdict.md
# benchmark-results.json
# profil.json
# profil-*.json
```

Puis ajoutez tout :
```bash
git add verdict.md benchmark-results.json profil.json
git commit -m "chore: versionner tous les artefacts générés"
```

## Règle Générale

> **Ne versionnez que ce qui a valeur de référence pour les juges / la revue.**
> Les artefacts CI (verdicts, benchmarks, profils auto-générés) sont reproductibles — ils n'ont pas leur place dans l'historique sauf cas d'audit explicite.

## Fichiers Qui DOIVENT Rester Versionnés

- `exemples/profil-maison-1.json` — exemples de référence pour les juges
- `exemples/profil-maison-2.json` — exemples de référence pour les juges
- `schemas/profile.schema.json` — schéma JSON Schema (contrat immuable)
- `grille/aidd.md` — grille d'évaluation officielle

## Vérification

Testez qu'un pattern ignore bien un fichier :
```bash
git check-ignore verdict.md        # doit afficher "verdict.md"
git check-ignore exemples/profil-maison-1.json  # doit ne RIEN afficher (versionné)
```