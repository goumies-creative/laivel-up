# ADR-0017 : Axe bonus Industrialisation — hors de la règle AND

**Status** : Accepted
**Date** : 2026-08-31
**Décideurs** : Romy Alula

## Contexte

Un 5e axe est envisagé (« Professionnalisation / Industrialisation ») pour
capturer des signaux au-delà des 4 axes officiels de la grille AIDD (Size,
Harness, Intervention, Parallel) : CI/CD, outillage qualité, discipline de
release. Risque identifié : les 4 profils officiels (arthur, bohort,
leodagan, perceval) sont calibrés 4/4 sans écart sur la grille officielle
(cf. plan `2026-08-28-001-chore-finalisation-hackathon-plan.md` §1.1) — un
axe supplémentaire qui entrerait dans la règle AND (`min()`) pourrait faire
chuter leur niveau sur des données d'industrialisation qu'ils ne fournissent
pas forcément, menaçant la preuve « 4/4, zéro écart » du pitch.

## Décision

- L'axe Industrialisation est **optionnel**, calculé et affiché **à part**
- Il est **hors de la règle AND** : il n'entre jamais dans le `min()` qui
  détermine `Verdict.level`
- Il vit dans un champ dédié (`Verdict.bonus_axis_scores`), séparé de
  `axis_scores` (les 4 axes officiels), lui-même alimenté par un tuple
  séparé `BONUS_AXES` (pas `AXES`)
- Même philosophie refus > deviner que les 4 axes officiels (cf. ADR-0004) :
  confiance basse ou données absentes → axe non tranché, jamais un niveau
  inventé — mais un axe bonus non tranché ne dégrade jamais le verdict
  principal
- Recette d'implémentation généralisée dans `docs/EXTENDING.md`
  (« Ajouter un axe bonus (hors règle AND) »), réutilisable pour tout futur
  axe optionnel, pas seulement Industrialisation
- Signaux pistés, **vérifiés sur les 4 profils officiels réels (31/08)** :
  qualité outillée (`sonar-measures.json` — présent sur les 4 profils,
  pas une pièce partielle), discipline CI (`git-activity.json → ci` :
  `failure_rate` / `median_runs_to_green`, déjà présent dans un fichier
  déjà lu par l'extracteur, aucune nouvelle source), tendance de
  couverture (`git-activity.json → tests` : `coverage_start` /
  `coverage_end` / `prs_with_tests_ratio`, sert de corroboration au chiffre
  statique de Sonar). Chacun corroboré par une seconde source plutôt que
  pris seul, même piège que « s'arrêter aux métriques » déjà identifié sur
  les 4 axes officiels. **Piste abandonnée** : « CI/CD configuré via
  fichiers de workflow dans `repo-context/` » — vérifié absent des 4
  profils, aucune donnée réelle à lire
- **Risque de régression identifié et à traiter dans la même passe** :
  `traces` a `"additionalProperties": false` dans
  `schemas/profile.schema.json` — toute nouvelle clé (`industrialisation`)
  doit y être déclarée explicitement comme propriété optionnelle, sinon le
  validateur `jsonschema` la rejette (le fallback `_validate_minimal()` de
  `schema.py`, lui, ne vérifie pas `additionalProperties` et laisserait
  passer sans le signaler — asymétrie à corriger des deux côtés si le
  chemin `jsonschema` est mis à jour)

## Conséquences

### Positives

- Aucun risque sur la calibration actuelle des 4 profils officiels (4/4,
  zéro écart)
- Le pitch garde sa preuve la plus forte intacte
- Ouvre la porte à d'autres axes optionnels futurs sans retoucher la règle
  AND ni les seuils historiques

### Négatives

- Deux chemins de scoring à maintenir en parallèle (axes officiels vs bonus)
- Risque de confusion visuelle si l'affichage CLI/rapport ne sépare pas
  clairement les deux blocs (point de vigilance explicite en implémentation)
- Barème (seuils, pondération) non arrêté à ce stade — chantier de
  conception à part entière, volontairement hors scope avant le rendu du
  31/08

## Liens

- Plan détaillé (cas d'usage complet de `EXTENDING.md`) :
  `docs/plans/2026-08-28-001-chore-finalisation-hackathon-plan.md` §11.7
- Recette générique : `docs/EXTENDING.md` § « Ajouter un axe bonus (hors
  règle AND) »
- Code (à venir, non implémenté à la date de cet ADR) : `src/laivelup/model.py`,
  `src/laivelup/scoring.py`, `src/laivelup/scoring_defaults.py`,
  `schemas/profile.schema.json`, `scripts/extract_official_profile.py`
  (extraction `sonar-measures.json` + `git-activity.json → ci`/`tests`)
- Référence axes existants : ADR-0004 (grille 4 axes), `GRID_QUICKREF.md`
