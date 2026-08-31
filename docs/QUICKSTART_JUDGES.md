# QUICKSTART_JUDGES.md — Commandes 1-ligne pour les juges

> Pour évaluer LAIVEL UP en 2 minutes. Aucune installation requise si Python 3.11+ est disponible.

## Démo vidéo

Voir la démo de 2 min : [goumies-creative-laivel-up-demo.mp4](../goumies-creative-laivel-up-demo.mp4)

## Installation

```bash
pip install laivelup
```

> Depuis un clone local (sans passer par PyPI) : `pip install .`

## Commandes essentielles

### Vérifier l'installation

```bash
laivelup --help
```

### Évaluer un profil

```bash
laivelup evaluate exemples/profil-maison-1.json --no-html
```

### Évaluer avec rapport HTML

```bash
laivelup evaluate exemples/profil-maison-1.json --out rapports
```

### Mode entretien guidé

```bash
laivelup interrogate --max-turns 6
```

### Créer une équipe

```bash
laivelup team create Equipe-Alpha "Alice,Bob,Charlie"
```

### Évaluer un membre

```bash
laivelup team evaluate Equipe-Alpha alice exemples/profil-maison-1.json
```

### Exporter les résultats

```bash
laivelup team export Equipe-Alpha --format md --out rapports
```

## Validation de la calibration

```bash
python scripts/calibrate.py --template
python scripts/calibrate.py --expected grille/profils-officiels/expected.json --diff --fix
```

## Vérification de qualité

```bash
pytest -q                    # 533 tests
ruff check src/ tests/       # 0 errors
mypy src/                    # 0 errors
bandit -r src/               # 0 issues
```

## Structure du projet

```
laivel-up/
  src/laivelup/          # Code source (CLI + scoring + team)
  exemples/              # Profils JSON d'exemple
  grille/                # Grille officielle AIDD
  schemas/               # JSON Schema pour validation
  scripts/               # Scripts utilitaire (calibrate, demo)
  docs/                  # Documentation
  tests/                 # Tests (unit + property + snapshot)
```

## Critères d'évaluation du jury

Libellés repris tels quels du sujet officiel (`SUJET.md`) — à vous de juger, pas à nous.

| Critère | Preuve à vérifier |
|---------|-------------------|
| 🎯 Le bon niveau ? | `python scripts/calibrate.py --expected grille/profils-officiels/expected.json --diff` — refuse un niveau (`UNDECIDED`) plutôt que d'en deviner un quand les données manquent |
| 💬 On comprend pourquoi ? | `laivelup evaluate <profil> --verbose` + rapports MD/HTML |
| 🔧 Comment tu l'as construit ? | `aidd_docs/` (sessions, audits, ADR) |
| ✨ La qualité est là ? | 533 tests, ruff/mypy/bandit ✅, CI matrix 3OS × 3Python — voir `QUALITY.md` |
