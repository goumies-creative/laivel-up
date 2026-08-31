# Copy française intégrale · LAIVEL UP

> Copy affichée et exportée pour les utilisateurs et personnes évaluées :
> CLI, rapports exportés (MD · HTML), exports équipe, dashboard, démo,
> documentation du repo. Chaque entrée : `fichier:ligne` · avant → après.
>
> Prompt compagnon : `docs/prompts/revue-copy-francaise.md` (3 passes
> Humanizer · La Plume · Le Miroir) pour la relecture fine, une fois la
> présente copy implémentée.

---

## 1 · Sources officielles et références fiables

| Source | Emplacement | Ce qu'elle fixe |
|---|---|---|
| Sujet officiel | `hackathons/laivel-up/SUJET.md` | « Une sortie qu'on comprend : le niveau, pourquoi, comment progresser » · les 4 critères jury |
| Grille officielle | `hackathons/laivel-up/levels/aidd.md` | Noms de niveaux (White… Gold), 4 axes, vocabulaire officiel (features, PR, context engineering, behavior, boucles) |
| Profils officiels | `hackathons/laivel-up/profiles/README.md` | Les 4 pièges : croire le déclaratif · s'arrêter aux métriques · confondre richesse et niveau |
| Copie locale de la grille | `grille/aidd.md` | Même contenu, versionnée dans le repo |
| Copie locale du sujet | `grille/README-OFFICIEL.md` | Même contenu, versionnée dans le repo |
| Méthode | `METHODE.md` | Règle AND, refus de deviner, équité structurelle |
| Transparence | `TRANSPARENCE.md` | Données utilisées, droit d'explication, limites |

---

## 2 · Règles de terminologie (décisions validées)

| Catégorie | Règle | Exemples |
|---|---|---|
| Noms de niveaux officiels | **EN gardé**, verbatim grille | `White`, `Red`, `Blue`, `Green`, `Copper`, `Silver`, `Gold` |
| Statut interne | **FR** | `UNDECIDED` → `Undécis` |
| Contrats machine | **EN gardé** | clés JSON (`name`, `level`, `axes`, `next_steps`…), en-têtes CSV `name,slug,level,limiting_axis,confidence,timestamp` |
| Textes humains | **FR intégral** | evidence, messages d'erreur, labels, exports MD/HTML |
| Vocabulaire de la grille | **EN gardé + glossaire FR** | `Harness`, `context engineering`, `behavior`, `Retry Loops` (officiel), `boucles de relance` (officiel), `PR`, `features` |
| Inventions internes | **FR** | `Red flags` → `Alertes` · `FAIL:` → `ÉCHEC :` · `ping` → `signal` · `dashboard` → `tableau de bord` · `SKIP` → `IGNORÉ` · `Slug` (helps humains) → `pseudo (slug)` · `Ratio` → `Proportion` |
| Exception documentée | **EN gardé, avec gloss FR** | `opt-out` : terme RGPD d'usage courant, gloss « (droit d'opposition) » à la première occurrence |
| Déco pixel NES | **EN gardé, assumé** | `>>> WORLD MAP <<<`, `>>> PROGRESS <<<` (pseudo-éléments CSS, flavour 8-bit) |

**Convention typographie** (AGENTS.md) : accents corrects partout · `·` en
titre/label, `:` en description, jamais `—` comme séparateur · espaces autour
de `/` dans le texte visible.

---

## 3 · Copy intégrale par surface

### A. Console CLI · verdict et entretien · `src/laivelup/cli.py`

| Ligne | Avant | Après |
|---|---|---|
| 315 | `VERDICT : {name}` | `VERDICT · {name}` (cohérence `·`) |
| 319-321 | `AXE` · `NIVEAU` · `CONFIANCE` | inchangé (déjà FR) |
| 339-340 | `!! DONNÉES INVALIDES !!` / `Refus de trancher.` | inchangé |
| 350 | `NIVEAU : {label}` | inchangé |
| 352 | `Axe plancher : {verdict.limiting_axis}` | inchangé |
| 356-365 | `!! REFUS DE TRANCHER !!` / `Données insuffisantes.` / `Questions à poser :` | inchangé |
| 370 | `!! ALERTE : {f.titre}` | inchangé (Alertes déjà FR côté CLI) |
| 378 | `--- Comment monter d'un cran ---` | inchangé |
| 393 | `source: {ev}` | `source · {ev}` |
| 395 | `variance: {a.variance}` | `variance · {a.variance}` |
| 397 | `donnees invalides:` ⚠ faute | `données invalides :` |
| 504 | docstring `...fusionne les réponses, re-score.` ⚠ | `...fusionne les réponses, ré-évalue.` |
| 517 | `Questions ouvertes > Réponses > Re-score` ⚠ | `Questions ouvertes · Réponses · Nouvelle évaluation` |
| 563 | `> QUESTION {turn}/{max_turns} ██` | inchangé |
| 570 | `> OK [dim]Réponse enregistrée.[/dim]` | inchangé |
| 584 | `*** NIVEAU DÉBLOQUÉ ***` | inchangé |
| 596-599 | `!! REFUS DE TRANCHER !!` / `Données insuffisantes.` / `Le refus est explicite.` | inchangé |

### B. Erreurs CLI · `src/laivelup/cli.py`

| Ligne | Avant | Après |
|---|---|---|
| 411-419 | epilog `... Exit 1 si niveau < RED` ⚠ | `... Code 1 si niveau < RED` |
| 432 | help `Fail si niveau inférieur (valeurs : RED, BLUE, GREEN...)` ⚠ | `Échoue si le niveau est inférieur (valeurs : RED, BLUE, GREEN...)` |
| 467 | `Avertissement : verdict non décidé (niveau=None), --fail-on ignoré` | inchangé (`None` = technique) |
| 482 | `FAIL: niveau {a} < {b}` ⚠ | `ÉCHEC : niveau {a} < {b}` |
| 679 | help `Slug du membre à évaluer.` ⚠ | `Pseudo anonymisé (slug) du membre à évaluer.` |
| 759 | help `Slug du membre.` ⚠ | `Pseudo anonymisé (slug) du membre.` |
| 761 | help `Activer ou désactiver l'opt-out.` | `Activer ou désactiver l'opt-out (droit d'opposition).` |
| 788 | help `Slug du membre à supprimer.` ⚠ | `Pseudo anonymisé (slug) du membre à supprimer.` |
| 828 | docstring `...génère un dashboard HTML.` ⚠ | `...génère un tableau de bord HTML.` |
| 844 | `UNDECIDED` ⚠ | `Undécis` |
| 859 | `Dashboard calibration : {path}` ⚠ | `Tableau de bord calibration : {path}` |

### C. `COMMAND_SCHEMA` (auto-découverte agent) · `src/laivelup/cli.py` l.81-149

| Ligne | Avant | Après |
|---|---|---|
| 103 | `Fail si niveau inférieur (ex: RED)` ⚠ | `Échoue si le niveau est inférieur (ex. : RED)` |
| 84-147 | autres descriptions | déjà FR, inchangées |
| 144-147 | `Succès / Erreur métier / Erreur de validation / Erreur outil` | inchangé |

### D. Questions · `src/laivelup/questions.py`

| Ligne | Avant | Après |
|---|---|---|
| 12 | `Quelle est la taille habituelle de tes features livrées avec l'IA (S, M, L, XL) ?` | inchangé (`features` officiel) |
| 14, 16-17, 23, 25, 27, 29 | déjà FR, `PR` officiel | inchangé |
| 20-21 | `Ratio de reprise indiqué sans métadonnées de PR : peux-tu fournir quelques PR typiques pour le corroborer ?` ⚠ | `Proportion de reprise indiquée sans PR à l'appui : peux-tu fournir quelques PR typiques pour la corroborer ?` |

### E. scoring.py · le plus gros bloc EN visible · `src/laivelup/scoring.py`

**E.1 Erreurs `normalize_profile` (l.82-135) · alignées sur le style `schema.py` :**

| Ligne | Avant (EN) | Après (FR) |
|---|---|---|
| 82 | `traces must be an object (dict).` | `traces : doit être un objet.` |
| 87 | `traces.pr_sizes must be a list.` | `traces.pr_sizes : doit être une liste.` |
| 92 | `traces.pr_sizes contains '{s}': allowed values {sorted}.` | `traces.pr_sizes contient '{s}' : valeurs = {sorted}.` |
| 98 | `traces.retries_after_fact must be a number (ratio 0-1).` | `traces.retries_after_fact : doit être un nombre (0-1).` |
| 103 | `traces.retries_after_fact must be a ratio between 0 and 1.` | `traces.retries_after_fact : doit être entre 0 et 1.` |
| 105 | idem 98 | idem 98 |
| 111 | `traces.{key} must be a non-negative integer.` | `traces.{key} : entier >= 0 requis.` |
| 117-119 | `... must be an integer, not {value}. Use int({value}) = {int} if truncation is intended.` | `traces.{key} : entier requis, pas {value}. Utilisez int({value}) = {int} si la troncature est voulue.` |
| 126 | idem 111 | idem 111 |
| 128 | `traces.{key} must be an integer.` | `traces.{key} : entier requis.` |
| 131 | `declared_level '{x}': unknown level.` | `declared_level '{x}' : niveau inconnu.` |
| 135 | `traces.{key} must be a boolean.` | `traces.{key} : booléen requis.` |

**E.2 Evidence strings (l.172-260) · visibles console + colonne `Éléments observés` MD + cartes HTML :**

| Ligne | Avant (EN) | Après (FR) |
|---|---|---|
| 172 | `{n} PR {s}` | inchangé (`PR` officiel) |
| 178, 183 | déjà FR | inchangé |
| 206 | `context + behavior + retry loops` | `contexte + behavior + boucles de relance` |
| 208 | `context + versioned agent rules` | `contexte + règles agent versionnées` |
| 210 | `project memory present and maintained` | `mémoire projet présente et maintenue` |
| 211 | `direct prompts, no context` | `prompts directs, pas de contexte` |
| 227 | `never, framing included (autonomous agents)` | `jamais, cadrage compris (agents autonomes)` |
| 229 | `never, once task is framed` | `jamais, une fois la tâche cadrée` |
| 231 | `intervention at key steps` | `intervention aux étapes clés` |
| 233 | `retry after the fact, on a portion` | `reprise après coup, sur une partie` |
| 235 | `retry after the fact, on majority` | `reprise après coup, sur la majorité` |
| 253 | `no parallel projects` | `aucun chantier en parallèle` |
| 255 | `{n} parallel projects` | `{n} chantiers en parallèle` |
| 257 | `{n} parallel projects, all completed` | `{n} chantiers en parallèle, tous menés au bout` |
| 259 | `{n} parallel projects (completion to confirm)` | `{n} chantiers en parallèle (complétude à confirmer)` |
| 260 | `{n} open projects but {c} completed` | `{n} chantiers ouverts mais {c} menés au bout` |

**E.3 Red flags (l.266-295) :**

| Ligne | Avant | Après |
|---|---|---|
| 277 | `Déclare {LEVEL} avec un ratio de reprise de {x%}.` | `Déclare {LEVEL} avec une proportion de reprise de {x%}.` |
| 276, 278-292 | titres/constats/sources/questions | déjà FR, inchangé |

**E.4 progress_for_axis (l.298-332) et Silver extra (l.421-425) :**

| Ligne | Avant | Après |
|---|---|---|
| 301-332 | next steps par axe | déjà FR, vocabulaire officiel, inchangé |
| 424 | `...en autonomie plusieurs fois par jour (ping pour Gold) ?` ⚠ | `...en autonomie plusieurs fois par jour (signal pour Gold) ?` |

**E.5 Variance (l.390-391) · bug réel :**

| Ligne | Avant | Après |
|---|---|---|
| 391 | `pic {X} intervenant, habituel plus bas (niveau sur l'habituel)` ⚠ | `pic {X} isolé, habituel plus bas (niveau sur l'habituel)` |

### F. Rapport Markdown · `src/laivelup/report.py`

| Ligne | Avant | Après |
|---|---|---|
| 100 | `# Verdict AIDD · {name}` | inchangé |
| 102, 106, 108, 110, 112-120 | labels | déjà FR, inchangé |
| 123 | `## Red flags (hypothèses à vérifier)` ⚠ | `## Alertes (hypothèses à vérifier)` |
| 129 | `## Comment monter d'un cran / point de levée d'incertitude` | inchangé |
| 133-143 | `## Transparence` | déjà FR, inchangé |

### G. Rapport HTML · `src/laivelup/report.py`

| Ligne | Avant | Après |
|---|---|---|
| 167 | `NIVEAU DÉBLOQUÉ` | inchangé |
| 218 | `UNDECIDED` ⚠ | `Undécis` |
| 239 | `Progression · {current_name}` | inchangé |
| 428, 434 | badges `Données invalides/insuffisantes : refus de trancher` | inchangé |
| 438 | `Axe plancher / faible : {axis}` | inchangé |
| 447 | `⚠ Vigilance · {titre} · {constat} ({source})` | inchangé |
| 454 | `<h2>Red flags (hypothèses à vérifier)</h2>` ⚠ | `<h2>Alertes (hypothèses à vérifier)</h2>` |
| 460 | `→ Piste · {next}` | inchangé |
| 293 | `Données insuffisantes pour trancher sur cet axe.` | inchangé |
| 315 | `L'humain cadrage, l'IA exécute.` ⚠ faute | `L'humain cadre, l'IA exécute.` |
| 331 | `Niveau maintenu.` | inchangé |
| 392, 418-420 | `Comment progresser vers le niveau suivant` / `Pour aller plus loin` / `Glossaire AIDD` / `Références curatées` | inchangé |
| 45 | `Un pic isolé ne compte pas — c'est la pratique régulière.` ⚠ | `Un pic isolé ne compte pas : c'est la pratique régulière.` |
| 67 | `La grille complète : 4 axes x 7 niveaux, règles et examples.` ⚠ | `La grille complète : 4 axes × 7 niveaux, règles et exemples.` |
| 608, 729 | CSS `>>> WORLD MAP <<<` / `>>> PROGRESS <<<` | **gardé** (flavour NES assumée, cf. §2) |
| 983-985 | footer `Généré par LAIVEL UP · Référentiel AIDD officiel` | inchangé |

### H. Équipe · `src/laivelup/team.py`

| Ligne | Avant | Après |
|---|---|---|
| 38-39 | `...sont autorisés (1-64 chars).` ⚠ | `...sont autorisés (de 1 à 64 caractères).` |
| 56 | `Refus : le répertoire parent est un symlink : {path}` ⚠ | `Refus : le répertoire parent est un lien symbolique (symlink) : {path}` |
| 100, 158, 175, 227, 243 | erreurs | déjà FR, inchangé |
| 179 | `a activé l'opt-out RGPD — évaluation refusée.` ⚠ | `a activé l'opt-out RGPD : évaluation refusée.` |
| 281 (MD) | `\| Membre \| Slug \| Niveau \|...` ⚠ | `\| Membre \| Pseudo (slug) \| Niveau \|...` |
| 278 | `*Exporté le {date} *` (espace parasite) | `*Exporté le {date}.*` |
| 309-311 | footer RGPD | déjà FR, inchangé |
| 323 (CSV) | `name,slug,level,limiting_axis,confidence,timestamp` | **gardé EN** (contrat machine, cf. §2) |
| 393 (HTML) | `<th>Slug</th>` ⚠ | `<th>Pseudo (slug)</th>` |
| 375-404 | titres export HTML | déjà FR, inchangé |

### I. Dashboard calibration · `src/laivelup/calibrate_dashboard.py`

| Ligne | Avant | Après |
|---|---|---|
| 50 | `UNDECIDED` ⚠ | `Undécis` |
| 63-65 | badges `CALIBRÉ ✅` / `{n} erreur(s)` | inchangé |
| 102, 280-308 | colonnes et titres | déjà FR, inchangé |

### J. Schema · `src/laivelup/schema.py`

| Ligne | Avant | Après |
|---|---|---|
| 45-51 | messages jsonschema bruts en anglais (`{path}: {error.message}`) ⚠ | ajouter un mapping de traduction des erreurs jsonschema courantes (type/enum/required/minLength/minimum/maximum/additionalProperties) vers le style FR de `_validate_minimal`, fallback message brut si non mappé |
| 59-109 | `_validate_minimal` | déjà FR, inchangé |

Exemples de mapping : `is not of type 'string'` → `doit être une chaîne` ·
`is not one of [...]` → `valeur invalide : attendu parmi [...]` ·
`is a required property` → `propriété requise manquante` ·
`is too short` → `trop court`.

### K. Démo · copy intégrale (commentaires + voix + tout texte affiché) · `scripts/demo.py`

> Contexte : scénario de la vidéo jury (2 min, muette, sous-titres = texte
> affiché). Phrases courtes, lisibles à l'écran, pas de jargon non introduit.
> Renvoi : `docs/VIDEO_PRODUCTION.md`.

| Ligne | Avant | Après | Rôle |
|---|---|---|---|
| 3 | docstring `scénario 2 min pour enregistrement asciinema` | inchangé | doc dev |
| 23 | `Profil 1 : contexte + rules` ⚠ | `Profil 1 : contexte + règles` | label étape 2a |
| 24 | `Contexte versionné, règles agent : signal de rigueur` | `Contexte versionné, règles agents : des fondations solides.` | voix |
| 28 | `Profil 2 : boucles de relance` | inchangé (vocabulaire officiel) | label étape 2b |
| 29 | `Retries après coup : le moteur ne triche pas la lecture` ⚠ | `Reprises après coup : le moteur ne croit pas le déclaratif.` | voix (écho du piège officiel) |
| 53 | `[ERREUR] Commande échouée : {cmd}` | inchangé | erreur |
| 59 | `LAIVEL UP — Démo CLI d'évaluation AIDD` ⚠ | `LAIVEL UP · Démo CLI d'évaluation AIDD` | titre écran |
| 60 | `Méthode : refus de deviner, questions au lieu de verdicts.` | `Refus de deviner : des questions, jamais de verdicts arrachés.` | voix d'ouverture (3 s pour capter) |
| 65 | `Étape 1 : Aide CLI` + `Découvrir les commandes disponibles` | `Étape 1 · Découvrir l'outil` + `Toutes les commandes, en un écran.` | label + voix |
| 74 | `Étape 2 : {description}` | `Étape 2 · Évaluer les profils` (le label par profil devient le commentaire) | label |
| 83 | `Étape 3 : Création équipe (RGPD)` + `Le nom n'apparaît jamais en clair dans les rapports` | `Étape 3 · Créer une équipe` + `Pseudo-anonymisation RGPD : les noms ne sortent jamais en clair.` | label + voix |
| 93 | `Étape 4 : Évaluation membre` + `Même moteur, agrégé au niveau équipe` | `Étape 4 · Évaluer un membre` + `Même moteur, au service de l'équipe.` | label + voix |
| 103 | `Étape 5 : Export résultats` + `Rapport exportable, prêt à partager` | `Étape 5 · Exporter` + `Un rapport prêt à partager.` | label + voix |
| 79 | `[SKIP] Profil absent : {profil}` ⚠ | `[IGNORÉ] Profil absent : {profil}` | message |
| 110 | `FIN DE LA DÉMO` | inchangé | fin |
| 112 | `Rapports générés dans : {dir}` | inchangé | fin |

**Note fonctionnelle (hors copy, à vérifier pendant l'implémentation) :**
l'étape 4 appelle `team evaluate DemoEquipe alice` alors que le slug réel
créé à l'étape 3 est pseudo-anonymisé (`alice-xxxxxxxx`). Récupérer le slug
affiché à l'étape 3, sinon la commande échoue.

### L. Balayage fautes ponctuelles (vérification finale)

Récapitulatif des fautes corrigées via les surfaces ci-dessus :

| Fichier:ligne | Faute | Correction |
|---|---|---|
| `cli.py:397` | `donnees invalides:` | `données invalides :` |
| `scoring.py:391` | `intervenant` | `isolé` |
| `report.py:45` | `—` en description | `:` |
| `report.py:67` | `x`, `examples` | `×`, `exemples` |
| `report.py:315` | `L'humain cadrage` | `L'humain cadre` |
| `team.py:179` | `—` en erreur | `:` |
| `team.py:278` | espace parasite | `.` |
| `cli.py:541-550` | mots-clés filtre interne : `verifier` sans accent, à aligner avec les textes réels (`vérifier`) | vérifier le matching, test interactif |

### M. Documentation du repo · corrections ciblées

| Fichier:ligne | Avant | Après |
|---|---|---|
| `docs/QUICKSTART_JUDGES.md:19` | `### Evaluer un profil` ⚠ | `### Évaluer un profil` |
| `:25` | `### Evaluer avec rapport HTML` ⚠ | `### Évaluer avec rapport HTML` |
| `:31` | `### Mode entretien guide` ⚠ | `### Mode entretien guidé` |
| `:37` | `### Creer une equipe` ⚠ | `### Créer une équipe` |
| `:43` | `### Evaluer un membre` ⚠ | `### Évaluer un membre` |
| `:49` | `### Exporter les resultats` ⚠ | `### Exporter les résultats` |
| `:62` | `## Verification de qualite` ⚠ | `## Vérification de qualité` |
| `CONTRIBUTING.md:101` | `## Pull Requests` ⚠ | `## Pull requests (PR)` |
| `:109` | `## Release Process` ⚠ | `## Processus de release` |
| `TRANSPARENCE.md:52` | `## Argument pitche-able (CNIL / AI Act)` ⚠ | `## Argument clé (CNIL / AI Act)` |
| `README.md`, `METHODE.md`, `QUALITY.md` | déjà conformes | vérification visuelle seulement |

---

## 4 · Glossaire cible · intégral (HTML, `report.py` GLOSSARY l.18-55)

Termes officiels EN gardés · définitions FR complètes :

- **Context Engineering** : La mémoire que l'IA lit avant de coder. Ce que
  l'IA sait : architecture, conventions, décisions. Versionné dans le dépôt,
  pas dans la tête.
- **Behavior** : Les règles et agents qui contrôlent comment l'IA agit :
  code review, hooks, garde-fous. Ce que l'IA a le droit de faire, et ce
  qu'elle refuse de faire.
- **Retry Loops** : Un script relance l'IA tant qu'une commande du projet
  échoue, jusqu'à ce qu'elle passe. La machine boucle, l'humain dort.
- **Harness** : L'ensemble du harnais autour du modèle : Context Engineering
  + Behavior + Retry Loops. Ce qui reste quand la conversation est fermée.
- **Intervention** : Quand l'humain intervient dans le travail de l'IA.
  Cadrer : choisir la tâche et dire ce qui est attendu. La qualité attendue
  est la même qu'en codant à la main : monter d'un niveau, c'est reprendre
  moins pour l'atteindre.
- **Taille (Size)** : La taille habituelle des features livrées avec l'IA :
  S (petite ou triviale), M (complexité moyenne), L (multi-étapes), XL
  (multi-modules). L'habituel, pas la plus grosse jamais faite.
- **En parallèle** : Combien de chantiers avancent en même temps,
  habituellement. Un pic isolé ne compte pas : c'est la pratique régulière.
- **Règle AND** : Un niveau n'est atteint que si TOUTES ses cellules sont
  satisfaites. L'axe le plus bas décide : l'axe plancher.
- **Refus de deviner** : Quand les données manquent ou se contredisent,
  l'outil refuse de trancher et pose des questions. Un niveau arraché ne
  vaut rien.

---

## 5 · Checklist d'implémentation

Ordre recommandé : chaque bloc invalide des tests connus, listés au §6.

- [ ] **1. `scoring.py`** : E.1 erreurs FR · E.2 evidence FR · E.3 red flag
      `proportion` · E.4 `signal pour Gold` · E.5 `isolé`
      → se propage console + MD + HTML + JSON
- [ ] **2. `report.py` MD** : F `Alertes`
- [ ] **3. `report.py` HTML** : G `Undécis`, `Alertes`, faute l.315,
      glossaire l.45, références l.67 (garder déco CSS NES)
- [ ] **4. `cli.py` console** : A l.397 faute, l.517, l.504, `·` l.393/395
- [ ] **5. `cli.py` erreurs/helps** : B epilog `Code 1`, `Échoue si`,
      `ÉCHEC :`, `pseudo (slug)` ×3, `droit d'opposition`, l.844 `Undécis`,
      `tableau de bord` ×2
- [ ] **6. `cli.py` schema** : C l.103
- [ ] **7. `questions.py`** : D l.20-21 `Proportion`
- [ ] **8. `team.py`** : H `caractères`, lien symbolique, `:` l.179,
      `Pseudo (slug)` MD+HTML, l.278 (CSV EN gardé)
- [ ] **9. `calibrate_dashboard.py`** : I l.50 `Undécis`
- [ ] **10. `schema.py`** : J mapping jsonschema → FR
- [ ] **11. `scripts/demo.py`** : K copy intégrale (labels + voix + `[IGNORÉ]`)
      + vérifier la note fonctionnelle du slug étape 4
- [ ] **12. Doc ciblée** : M QUICKSTART (7 accents) · CONTRIBUTING (2 titres)
      · TRANSPARENCE (1 titre)
- [ ] **13. Balayage L** : re-grep `donnees`, `intervenant`, `examples`,
      `chars`, `SKIP`, `Red flags`, `UNDECIDED`, `FAIL`, `dashboard`,
      `pitche-able` dans `src/` et `scripts/` → zéro occurrence hors gardées
- [ ] **14. Tests** : appliquer §6 (snapshots + assertions)
- [ ] **15. Validation** : pytest complet · ruff · mypy · générer un rapport
      de contrôle (`evaluate exemples/profil-maison-1.json`) et relire
      MD + HTML visuellement

---

## 6 · Impact tests et validation

### Snapshots (recapture obligatoire)
`tests/snapshots/` : `evaluate_profil_maison_1/2`, `interrogate_verdict_atteint`,
`interrogate_sans_verdict`, `help_main/evaluate/interrogate/team`.
Après implémentation : `python -m pytest tests/test_snapshots.py --snapshot-update`
puis relire chaque snapshot à l'œil (c'est la copy finale).

### Assertions sur textes à repérer (grep avant édition)
- `must be` · `unknown level` · `parallel projects` (evidence) : `test_scoring_edge.py`, `test_scoring.py`
- `UNDECIDED` : `test_calibrate_enhanced.py`, `test_calibrate_core_gaps.py`, `test_report*`
- `Red flags` : `test_report.py`, `test_report_enhanced.py`
- `FAIL` : `test_cli_extended.py` (fail-on)
- `Slug` : `test_team.py` (exports)
- labels démo : `test_demo.py`, `test_scripts.py`
- `ERREUR`/`Niveau`/`Refus` : `test_cli_extended.py`, `test_install_clean.py`

### Commandes de validation
```bash
python -m pytest tests/ -m "not install and not slow" --timeout=120 \
  --ignore=tests/security --no-header -q --no-cov
python -m ruff check src/ tests/ && python -m ruff format src/ tests/
python -m mypy src/laivelup/
laivelup evaluate exemples/profil-maison-1.json --no-html   # contrôle visuel MD
```

### Règles de non-régression
- Clés JSON (`verdict_to_dict`, CSV) : **aucun renommage** (contrat machine)
- Noms de niveaux EN : **aucune traduction**
- Déco CSS NES : **gardée**
- Exit codes : inchangés (0/1/2)
