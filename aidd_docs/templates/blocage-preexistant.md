# Template — Blocage pre-commit/CI par une erreur pré-existante

## Quand utiliser ce template

Un hook (pre-commit, CI) bloque un commit ou une PR à cause d'erreurs qui
existaient déjà avant tes changements — pas introduites par toi. Le réflexe
à éviter : corriger la dette au passage et la mélanger avec le travail en
cours dans le même commit. Ce template sépare les deux, systématiquement.

Origine : issue #1 de `laivelup-rebuild/socle-qualite` (5 erreurs ruff
pré-existantes dans `src/laivelup/report.py`, hors scope du fix en cours).

---

## # Questions

**Contexte**
- Branche : `<branche>`
- Commande bloquée : `<ex. git commit>`
- Hook / outil : `<ex. pre-commit ruff, mypy, pytest>`
- Nombre d'erreurs : `<N>`
- Fichier(s) concerné(s) : `<liste>`

**Vérification de pré-existence**
Commande utilisée : `git stash && <commande de vérification, ex: ruff check src/laivelup/report.py> ; git stash pop`

Résultat (coller la sortie) :
```
<sortie>
```

- [ ] Confirmé : les erreurs existent sur HEAD, avant mes changements
- [ ] Mes fichiers modifiés/nouveaux sont propres — lesquels : `<liste>`

**Décision**
- [ ] Commiter avec `--no-verify` (fichiers du run propres, dette pré-existante non liée) → suite ci-dessous
- [ ] Corriger la dette avant de commiter (bloquant, lié à mes changements) → pas ce template
- [ ] Autre : `<préciser>`

---

## Actions si "commit --no-verify"

1. Commiter le travail propre :
   ```
   git commit --no-verify -m "<message du travail réellement fait, ex: fix(...): ... (issue #<N>)>"
   ```

2. Ouvrir l'issue de dette dédiée : `/skills → 04-issue-create`, avec ce corps :

   ```
   Titre : Corriger <N> erreurs <outil> pré-existantes dans <fichier(s)>

   Détectées en résolvant l'issue #<N précédent>, lors d'un commit bloqué par
   le hook <outil>. Vérifiées comme pré-existantes sur HEAD via :
   git stash && <commande> ; git stash pop

   Hors scope de l'issue #<N précédent> — ne pas mélanger les deux dans un
   même commit.

   Erreurs :
   <coller la sortie de l'outil>
   ```

3. Référencer l'issue de dette dans la description de la PR de l'issue en
   cours, pour que la revue sache qu'elle existe et pourquoi elle n'est pas
   traitée ici.
