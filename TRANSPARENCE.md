# Transparence · LAIVEL UP

Transparence du moteur d'évaluation AIDD, pensée pour rester conforme et
pitche-able face à la CNIL et à l'AI Act.

## Finalité

Évaluer le niveau d'**adoption de l'IA** dans le workflow d'un développeur,
selon la grille officielle du hackathon LAIVEL UP (7 niveaux, 4 axes). La
finalité est unique, déclarée et limitée : aucune donnée n'est collectée pour
un autre usage.

## Données utilisées

- **Uniquement des traces techniques** déclarées par l'utilisateur : tailles de
  PR, mémoire projet versionnée, règles et agents, boucles de relance, ratio de
  reprise, chantiers menés en parallèle.
- **Aucune donnée personnelle** : pas de nom réel exploité (le fichier de sortie
  porte un slug haché), pas d'adresse, pas de localisation, pas de profil
  personnel.
- **Aucun neurotype demandé ni inféré** : le neurotype est hors périmètre, et
  aucune déduction (hyperfocus, etc.) n'est transformée en pénalité. Un pic est
  signalé en preuve, jamais utilisé pour fixer un niveau.
- Les données restent sur la machine de l'utilisateur ; le CLI n'appelle aucun
  service externe.

## Droit d'explication

Le rapport restitue toujours :

1. le **niveau** attribué (ou le refus de trancher) ;
2. les **éléments observés** qui l'ont amené là, par axe ;
3. l'**axe plancher / faible** qui fixe le niveau ;
4. le **mode d'emploi pour monter d'un cran** sur cet axe ;
5. les **red flags** portés comme hypothèses à vérifier, avec la question à poser.

C'est un droit d'explication par design : la décision est déterministe,
documentée dans la sortie, et reproductible.

## Mécanisme de refus (équité structurelle)

- Le moteur **refuse de trancher** plutôt que de deviner quand les données sont
  insuffisantes, contradictoires ou non corrélées (ex. reprise auto-déclarée non
  triangulée).
- La **confiance par axe** est affichée ; sous le seuil, pas de verdict.
- En l'absence de preuve, l'outil ne rend **jamais** un niveau plus bas que ce
  que les données prouvent : l'erreur par défaut est le refus + la question, pas
  la note arbitraire.

## Argument pitche-able (CNIL / AI Act)

> Un outil qui évite trois pièges réglementaires : pas de données sensibles
> traitées (aucun neurotype, aucune donnée personnelle), pas de décision
> automatique opaque (chaque niveau s'explique, le développeur peut demander
> pourquoi et comment), pas d'auto-pénalité biaisée (le moteur refuse plutôt
> que de juger bas). La sobriété des données rend le projet minimalement
> assujetti et factuellement démontrable.

## Limites connues

- La séniorité, la qualité du code et le neurotype ne sont **pas mesurés** :
  un niveau reflète une adoption observée, pas une valeur humaine.
- Tout ce qui est auto-déclaré (ratio de reprise, chantiers menés au bout) est
  corroboré par des questions, jamais pris pour argent comptant.