# Transparence · LAIVEL UP

Transparence du moteur d'évaluation AIDD, pensée pour rester conforme et
pitche-able face à la CNIL et à l'AI Act.

## Finalité

Évaluer le niveau d'**adoption de l'IA** dans le workflow des développeurs,
selon la grille officielle du hackathon LAIVEL UP (7 niveaux, 4 axes). La
finalité est unique, déclarée et limitée : aucune donnée n'est collectée pour
un autre usage.

## Données utilisées

- **Uniquement des traces techniques** déclarées par l'utilisateur : tailles de
  PR, mémoire projet versionnée, règles et agents, boucles de relance, ratio de
  reprise, chantiers menés en parallèle.
- **Aucune donnée personnelle** : pas de nom réel exploité (le fichier de sortie
  porte un slug pseudo-anonymisé via HMAC-SHA-256 avec sel par équipe), pas d'adresse, pas de
  localisation, pas de profil personnel.
- **Aucun neurotype demandé ni inféré** : le neurotype est hors périmètre, et
  aucune déduction (hyperfocus, etc.) n'est transformée en pénalité. Un pic est
  signalé en preuve, jamais utilisé pour fixer un niveau.
- Les données restent sur la machine de l'utilisateur ; le CLI n'appelle aucun
  service externe.
- **Opt-out RGPD** : un membre peut demander l'exclusion via `team opt-out` ;
  ses données sont filtrées de tous les exports et de l'historique.

## Droit d'explication

Le rapport restitue toujours :

1. le **niveau** attribué (ou le refus de trancher) ;
2. les **éléments observés** qui l'ont amené là, par axe ;
3. l'**axe plancher / faible** qui fixe le niveau ;
4. le **mode d'emploi pour monter d'un cran** sur cet axe ;
5. les **red flags** portés comme hypothèses à vérifier, avec la question à poser.

C'est un droit d'explication par design : la décision est déterministe,
documentée dans la sortie, et reproductible.

## Opposition (opt-out) et effacement

Le Team Tracker donne deux leviers distincts, alignés sur le RGPD :

| Levier | Commande | Article | Effet |
|--------|----------|---------|-------|
| **Opposition (opt-out)** | `team opt-out <équipe> <slug>` | Art. 21 | Le membre refuse tout nouveau traitement : `team evaluate` refuse l'évaluation, le membre et son historique disparaissent des exports partagés (MD · HTML · CSV · JSON). Son slug reste dans le fichier d'équipe local : `--disable` réactive le traitement. |
| **Effacement (purge)** | `team remove <équipe> <slug> --purge` | Art. 17 | Le membre **et** tout son historique évalué sont supprimés du fichier d'équipe. Aucune trace restante. |

Le pseudo (slug) est le seul identifiant présent dans les exports : le nom
réel est protégé par un HMAC salé stocké uniquement dans le fichier d'équipe
local (cf. `METHODE.md`, équité structurelle).

## Mécanisme de refus (équité structurelle)

- Le moteur **refuse de trancher** plutôt que de deviner quand les données sont
  insuffisantes, contradictoires ou non corrélées (ex. reprise auto-déclarée non
  triangulée).
- La **confiance par axe** est affichée ; sous le seuil, pas de verdict.
- En l'absence de preuve, l'outil ne rend **jamais** un niveau plus bas que ce
  que les données prouvent : l'erreur par défaut est le refus + la question, pas
  la note arbitraire.

## Argument clé (CNIL / AI Act)

> Un outil qui évite trois pièges réglementaires : pas de données sensibles
> traitées (aucun neurotype, aucune donnée personnelle exploitable — les slugs
> sont pseudo-anonymisés via HMAC-SHA-256 avec sel par équipe, résistants à la
> re-identification par dictionnaire), pas de décision automatique opaque (chaque
> niveau s'explique, le développeur peut demander pourquoi et comment), pas
> d'auto-pénalité biaisée (le moteur refuse plutôt que de juger bas). La
> sobriété des données rend le projet minimalement assujetti et factuellement
> démontrable.

## Limites connues

- La séniorité, la qualité du code et le neurotype ne sont **pas mesurés** :
  un niveau reflète une adoption observée, pas une valeur humaine.
- Tout ce qui est auto-déclaré (ratio de reprise, chantiers menés au bout) est
  corroboré par des questions, jamais pris pour argent comptant.