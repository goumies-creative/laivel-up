# QUICKSTART_JUDGES.md — Commandes 1-ligne pour les juges

> Pour évaluer LAIVEL UP en 2 minutes. Aucune installation requise si Python 3.11+ est disponible.

## Installation

```bash
pip install .
```

## Commandes essentielles

### Vérifier l'installation

```bash
laivelup --help
```

### Evaluer un profil

```bash
laivelup evaluate exemples/profil-maison-1.json --no-html
```

### Evaluer avec rapport HTML

```bash
laivelup evaluate exemples/profil-maison-1.json --out rapports
```

### Mode entretien guide

```bash
laivelup interrogate --max-turns 6
```

### Creer une equipe

```bash
laivelup team create Equipe-Alpha "Alice,Bob,Charlie"
```

### Evaluer un membre

```bash
laivelup team evaluate Equipe-Alpha alice exemples/profil-maison-1.json
```

### Exporter les resultats

```bash
laivelup team export Equipe-Alpha --format md --out rapports
```

## Validation de la calibration

```bash
python scripts/calibrate.py --template
python scripts/calibrate.py --expected grille/profils-officiels/expected.json --diff --fix
```

## Verification de qualite

```bash
pytest -q                    # 85+ tests
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

| Critère | Score attendu | Vérification |
|---------|---------------|--------------|
| Accuracy | 4/5 | `calibrate.py --diff` |
| Explainability | 4/5 | `--verbose` + rapports MD |
| Robustness | 4/5 | 344 tests, CI matrix 3OS x 3Py, benchmarks p50/p95 (si disponibles) |
| Reusability | 4/5 | MIT, `pip install`, hooks |
