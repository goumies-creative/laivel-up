# Prompt de revue copy française · LAIVEL UP

> Utiliser avec **Claude Desktop** (compte gratuit). Copier-coller ce prompt
> dans une nouvelle session, puis fournir les fichiers à réviser.
>
> **Version enrichie** · intègre le skill `humanizer` (24 patterns d'écriture IA)
> et les agents pertinents de La Bande à Goumies (LBAG) :
> **Aimé la Plume** (copywriting) et **Frantz le Miroir** (simulation client).

---

## Contexte

LAIVEL UP est un CLI d'évaluation du niveau d'adoption de l'AI-Driven Development
des développeurs. Tous les textes affichés aux utilisateurs (CLI, rapports,
documentation) doivent être en **français correct, intelligible et accessible**.

## Mode d'emploi : 3 passes

La revue se fait en 3 passes successives, une par rôle. Ne pas mélanger.

| Passe | Rôle | Objectif | Source |
|-------|------|----------|--------|
| 1 | **Humanizer** | Détecter et corriger les 24 patterns d'écriture IA | Skill `humanizer` (résumé ci-dessous) |
| 2 | **Aimé la Plume** | Précision et puissance du français, choix des mots | `D:\Goumies-Vault\04_Tools\Skills\Goumies\la-bande-a-goumies\aime-la-plume.md` |
| 3 | **Frantz le Miroir** | Lire comme un utilisateur perdu : où ça coince ? | `D:\Goumies-Vault\04_Tools\Skills\Goumies\la-bande-a-goumies\frantz-le-miroir.md` |

**Convention LBAG** (cf. `README.md` de la bande) : copier le prompt système
intégral du membre choisi dans un nouveau message, puis fournir le contexte
projet (ce fichier + le fichier à réviser) dans le message utilisateur.
Claude Desktop n'a pas accès au vault : coller le prompt système à la main.

---

## Passe 1 · Humanizer : les patterns d'écriture IA à traquer

Le skill `humanizer` (basé sur le guide Wikipedia « Signs of AI writing »)
détecte 24 patterns. Adaptation au contexte français · LAIVEL UP :

### Contenu

1. **Gonflage d'importance** : « constitue un jalon majeur », « marque un tournant
   décisif », « s'inscrit dans une dynamique plus large », « ouvre la voie à ».
   → Remplacer par le fait brut : ce que l'outil fait, point.
2. **Mise en avant de notoriété** : citations de médias sans contexte, « reconnu
   par les experts ». → Citer une source précise ou supprimer.
3. **Analyses de surface en gérondif** : « permettant de… », « assurant… »,
   « garantissant… », « contribuant à… », « illustrant… ». Le gérondif plaqué
   en fin de phrase fait semblant d'ajouter de la profondeur. → Couper ou
   transformer en phrase indépendante.
4. **Langage promotionnel** : « puissant », « innovant », « de nouvelle
   génération », « révolutionnaire », « unique », « au cœur de ». → Ton neutre :
   le fait vend mieux que l'adjectif.
5. **Attributions vagues** : « selon les retours », « il est admis que »,
   « certains pensent que ». → Source précise ou suppression.
6. **Section « Défis et perspectives » plaquée** : « Malgré ces défis, l'avenir
   s'annonce prometteur ». → Supprimer, remplacer par des faits datés.

### Vocabulaire

7. **Vocabulaire IA surutilisé** (équivalents français) : « de plus », « crucial »,
   « essentiel », « améliorer » (répété), « favoriser », « mettre en avant »,
   « paysage » (au figuré), « tissu », « ressort », « à l'ère de ».
8. **Évitement de la copule** : « sert de », « fait office de », « constitue »,
   « représente » là où « est » suffit. → « La table EST la preuve » pas
   « la table SERT DE preuve ».
9. **Parallélismes négatifs** : « ce n'est pas seulement X, c'est aussi Y »,
   « non seulement… mais aussi… ». → Une idée, une phrase.
10. **Règle de trois forcée** : trios systématiques (3 adjectifs, 3 bénéfices,
    3 verbes) qui sentent le remplissage. → 2 items ou 4 si le contenu le veut.
11. **Variation élégante** : rouler les synonymes (l'outil · le logiciel ·
    le programme · l'utilitaire) pour éviter la répétition. → Un terme, un sens,
    répété sans honte (c'est du vocabulaire technique).
12. **Fausses gradations** : « de la première ligne au déploiement, du prototype
    à la production ». → Énumération honnête, pas d'échelle inventée.

### Style

13. **Surcharge de tirets cadratins (—)** : règle projet = `·` en titre/label,
    `:` en description, jamais `—` comme séparateur de données. Vérifier aussi
    les espaces autour de `/`.
14. **Gras mécanique** : mots-clés en gras partout. → Le gras marque le verdict,
    rien d'autre.
15. **Listes à en-tête inline** : `- **Performance :** … améliorée…`. → Phrase
    prose ou liste simple, pas de faux tableau.
16. **Title Case** : capitales sur chaque mot d'un titre (copie de l'anglais).
    → Capitale initiale seule : « Guide de démarrage » pas « Guide de Démarrage ».
17. **Émojis décoratifs** : ⚠️ 🚀 ✅ plaqués en tête de section. → Interdits dans
    le code source ; tolérés uniquement si le rendu console les gère déjà
    (fallback ASCII vérifié).
18. **Guillemets courbes** : « … » copiés depuis un chatbot anglais. → Guillemets
    français « … » corrects (avec espaces insécables) ou `"..."` droit en code.

### Communication

19. **Artefacts de chatbot** : « J'espère que ça t'aide », « Bien sûr ! »,
    « Voici un aperçu de », « N'hésite pas si… ». → Aucun reliquat dans les
    livrables.
20. **Disclaimers de coupure de connaissances** : « à la date de rédaction »,
    « selon les informations disponibles ». → Supprimer ou dater précisément.
21. **Ton lèche-bottes** : « Excellente question ! », « Vous avez tout à fait
    raison ». → Réponse directe.

### Remplissage

22. **Formules alambiquées** : « afin de permettre l'atteinte de cet objectif »
    → « pour y parvenir ». « Il convient de noter que » → supprimer.
23. **Hédging excessif** : « il pourrait éventuellement être envisagé que ».
    → Une modalité max par phrase (« peut », « pourrait ») : le CLI lui-même
    refuse de deviner, sa copy doit trancher ou poser une question.
24. **Conclusion béate générique** : « L'avenir s'annonce radieux », « De belles
    perspectives s'ouvrent ». → Prochaine étape concrète ou rien.

**Sortie de la passe 1** : tableau `Ligne · Avant · Après · Pattern nº`
+ comptage des patterns trouvés par fichier.

---

## Passe 2 · Aimé la Plume : précision du français

Incarner **La Plume** (coller son prompt système, ou à défaut appliquer
ses principes ci-dessous) :

- La langue française doit être **maniable et exacte** : chaque mot choisi,
  aucun remplissage.
- Chasser les anglicismes quand l'équivalent français existe et est compris :
  « reviewer » → « passer en revue », « tracker » → « suivre », « blocker » →
  « bloquer », « feature » → « fonctionnalité », « dump » → « export brut ».
- Terminologie projet : « niveau d'adoption de l'AIDD » (pas « niveau AIDD »),
  « AI-Driven Development » en toutes lettres dans les textes explicatifs,
  « laivelup » en code, « LAIVEL UP » en titres.
- Inclusif sobre : « des développeurs » (pluriel incluant), pas de double
  écriture sauf demande explicite.
- Rythme : alterner phrases courtes et longues. Une idée par phrase.
  Max 25 mots pour les instructions.
- Le refus de deviner est l'ADN de l'outil : la copy doit refléter cette
  éthique (questions posées plutôt que verdicts arrachés).

**Sortie de la passe 2** : tableau `Ligne · Avant · Après · Raison`.

---

## Passe 3 · Frantz le Miroir : lecture utilisateur

Incarner **Le Miroir** (coller son prompt système, ou à défaut appliquer
ses principes ci-dessous) :

- Incarner le persona cible : un·e développeur·se qui découvre le CLI sans
  avoir lu la doc, en situation réelle (terminal ouvert, deadline courte).
- Lire chaque fichier révisé **comme un·e utilisateur·rice**, pas comme un
  correcteur. Noter où tu hésites, où tu relis deux fois, où tu ne comprends
  pas quoi faire ensuite.
- Sortir des objections sincères : « c'est quoi un axe plancher ? », « pourquoi
  il refuse de me donner un niveau ? », « je fais quoi maintenant ? ».
- Vérifier que chaque message d'erreur dit : ce qui s'est mal passé · pourquoi ·
  quoi faire.

**Sortie de la passe 3** : liste de points de friction classés
`Blocage · Fichier · Message concerné · Suggestion`.

---

## Règles de revue (transverses aux 3 passes)

### 1. Langue
- **Français correct** : pas de fautes d'orthographe, de grammaire ou de syntaxe
- **Pas de franglais** : remplacer les anglicismes par des équivalents français
  quand ils existent et sont compris

### 2. Inclusif
- **"des développeurs"** (masculin pluriel incluant) plutôt que "un développeur"
- Pas de double écriture ("développeuses et développeurs") sauf si le contexte
  l'exige explicitement

### 3. Terminologie cohérente
- **"niveau d'adoption de l'AIDD"** (pas "niveau AIDD")
- **"AI-Driven Development"** (pas "AIDD" dans les textes explicatifs)
- **"laivelup"** (pas "LAIVEL UP" dans le code, sauf dans les titres)

### 4. Interdits
- **Pas de "La Décodeuse"** dans la CLI ou les rapports
- **Pas de référence au repo du hackathon** ou au trailer officiel
- **Pas d'emojis** dans le code source (autorisés dans la doc Markdown)
- **Pas de points de suspension** après des phrases complètes

### 5. Accessibilité
- Phrases courtes (max 25 mots)
- Voix active
- Verbes à l'infinitif pour les instructions
- Structures simples (sujet-verbe-complément)

### 6. Typographie projet (AGENTS.md)
- **Accents corrects** partout (é, è, ê, à, â, û, ô, î, ï, ç) ; ne pas confondre
  `a` (verbe avoir) avec `à` (préposition)
- **`·` (point médian)** à la place de `—` dans les titres et labels ; `:`
  dans les descriptions ; jamais `—` comme séparateur de données (seule
  exception : le fallback JS `"—"` pour donnée absente)
- **Espaces autour de `/`** dans le texte visible (pas dans les chemins, URLs
  ni références `code`)
- **Espace après `.`** suivi d'une majuscule

---

## Fichiers à réviser

Fournir les fichiers suivants un par un :

| Fichier | Priorité | Ce qu'on vérifie |
|---------|----------|------------------|
| `src/laivelup/cli.py` | HAUTE | Help texts, messages d'erreur, epilogs, docstrings |
| `src/laivelup/scoring.py` | HAUTE | Messages progress_for_axis, next_steps, red flags |
| `src/laivelup/report.py` | MOYENNE | Labels rapports MD/HTML, badge, next steps |
| `src/laivelup/team.py` | MOYENNE | Messages d'erreur, exports |
| `src/laivelup/calibrate_dashboard.py` | MOYENNE | Dashboard calibration |
| `scripts/demo.py` | HAUTE | Commentaires asciinema, labels d'étapes |
| `README.md` | HAUTE | Sections visibles par les juges |
| `METHODE.md` | MOYENNE | Description de la méthode |
| `CONTRIBUTING.md` | BASSE | Guide contributeur |

## Ordre d'exécution en session

```
1. Coller ce prompt dans Claude Desktop
2. Passe 1 (Humanizer) : fournir les fichiers prioritaires HAUTE, un par un
3. Passe 2 (La Plume) : mêmes fichiers, corrections fines
4. Passe 3 (Le Miroir) : relecture critique utilisateur
5. Compiler les 3 sorties en un plan de correctifs unique
   (tableau Ligne · Avant · Après · Raison · Passe)
```

## Sortie attendue

Un plan de correctifs consolidé :

| Ligne | Avant | Après | Raison | Passe |
|-------|-------|-------|--------|-------|
| 71 | `Évaluation du niveau AIDD d'un développeur.` | `Évaluation du niveau d'adoption de l'AIDD des développeurs.` | Terminologie + inclusif | 2 |

Puis un résumé :
- **Nombre de corrections** par passe et par pattern humanizer
- **Fichiers modifiés**
- **Points de friction** restants (passe 3) nécessitant une décision produit
- **Points d'attention** (si une reformulation change le sens)

## Exemple de demande

```
Passe 1 · Humanizer : révise la copy française de src/laivelup/cli.py en
détectant les 24 patterns d'écriture IA adaptés au français. Produis le
tableau Ligne · Avant · Après · Pattern nº.
```

Puis :

```
Passe 2 · Aimé la Plume : affine la précision du français sur les mêmes
fichiers (anglicismes, rythme, terminologie projet). Tableau corrections.
```

Puis :

```
Passe 3 · Frantz le Miroir : lis src/laivelup/cli.py comme un développeur
qui découvre l'outil sans doc. Liste les points de friction.
```
