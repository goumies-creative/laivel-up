---
id: aidd
version: 1
# Bloc machine : seule source que charge la bibliothèque (laivelup.grid_doc).
# Les tableaux ci-dessous sont la même grille, en français, pour les humains ;
# le chargement échoue si les deux divergent.
#
# `requirements[axe]` liste les exigences de cet axe de la plus faible à la plus
# forte. L'indice dans cette liste est l'ordre de l'exigence. Invariant vérifié
# au chargement : un niveau n'exige jamais moins que celui du dessous.
machine: |
  {
    "levels": [
      {"id": "white", "label": "❖ White", "rank": 0},
      {"id": "red", "label": "🔺 Red", "rank": 1},
      {"id": "blue", "label": "🔹 Blue", "rank": 2},
      {"id": "green", "label": "🟢 Green", "rank": 3},
      {"id": "copper", "label": "🥉 Copper", "rank": 4},
      {"id": "silver", "label": "🥈 Silver", "rank": 5},
      {"id": "gold", "label": "🥇 Gold", "rank": 6}
    ],
    "axes": [
      {"id": "size", "label": "Taille"},
      {"id": "harness", "label": "Harness"},
      {"id": "intervention", "label": "Intervention"},
      {"id": "parallel", "label": "En parallèle"}
    ],
    "requirements": {
      "size": ["—", "S", "M", "L", "L-XL"],
      "harness": [
        "rien",
        "prompts",
        "context engineering",
        "context engineering, behavior",
        "context engineering, behavior, boucles"
      ],
      "intervention": [
        "—",
        "après coup, sur la majorité",
        "après coup, sur une partie",
        "aux étapes clés",
        "jamais, une fois la tâche cadrée",
        "jamais, cadrage compris"
      ],
      "parallel": ["0", "1", "3"]
    },
    "cells": {
      "white": {"size": "—", "harness": "rien", "intervention": "—", "parallel": "0"},
      "red": {"size": "S", "harness": "prompts", "intervention": "après coup, sur la majorité", "parallel": "1"},
      "blue": {"size": "M", "harness": "context engineering", "intervention": "après coup, sur une partie", "parallel": "1"},
      "green": {"size": "L", "harness": "context engineering, behavior", "intervention": "aux étapes clés", "parallel": "1"},
      "copper": {"size": "L-XL", "harness": "context engineering, behavior", "intervention": "aux étapes clés", "parallel": "3"},
      "silver": {"size": "L-XL", "harness": "context engineering, behavior, boucles", "intervention": "jamais, une fois la tâche cadrée", "parallel": "3"},
      "gold": {"size": "L-XL", "harness": "context engineering, behavior, boucles", "intervention": "jamais, cadrage compris", "parallel": "3"}
    }
  }
---
# Référentiel AIDD

Sept niveaux d'adoption de l'IA dans le workflow des développeurs.

**Les niveaux se cumulent.** Chaque niveau garde ce que le précédent apporte.

La qualité attendue est la même qu'en codant sans IA.

## Les axes


| Axe | Ce qu'il mesure |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Taille** | La taille habituelle des features livrées avec l'IA, pas la plus grosse jamais faite. **S** peu de complexité · **M** complexité moyenne · **L** multi-étapes · **XL** multi-modules |
| **Harness** | Ce que la personne a mis en place autour du modèle. **Context engineering** : ce que l'IA sait (mémoire, architecture, conventions, etc). **Behavior** : comment elle agit (règles, agents, hooks, guardrails, etc). **Boucles** : un script relance l'IA tant qu'une commande du projet échoue, jusqu'à ce qu'elle passe |
| **Intervention** | Quand la personne intervient dans le travail de l'IA. Cadrer, c'est choisir la tâche et dire ce qui est attendu. La qualité attendue est la même qu'en codant à la main : monter d'un niveau, c'est reprendre moins pour l'atteindre |
| **En parallèle** | Combien de chantiers avancent en même temps, habituellement. Un pic isolé ne compte pas |


## La grille


| Niveau | Taille | Harness | Intervention | En parallèle | Ce qu'on observe |
| ----------- | ------ | -------------------------------------- | --------------------------- | ------------ | ---------------------------------------------------------------------------------------------------------------------------- |
| `❖ White` | — | rien | — | 0 | Aucun fichier de contexte, aucun commit signé par un assistant |
| `🔺 Red` | S | prompts | après coup, sur la majorité | 1 | PR de taille S, beaucoup de commits correctifs après ouverture, pas de fichier de contexte |
| `🔹 Blue` | M | context engineering | après coup, sur une partie | 1 | PR de taille M, quelques commits correctifs par PR, mémoire projet présente et maintenue |
| `🟢 Green` | L | context engineering, behavior | aux étapes clés | 1 | PR de taille L, presque aucun commit correctif, règles et agents versionnés dans le dépôt |
| `🥉 Copper` | L-XL | context engineering, behavior | aux étapes clés | 3 | PR de taille L et XL, presque aucun commit correctif, plusieurs branches ouvertes le même jour et menées jusqu'au bout |
| `🥈 Silver` | L-XL | context engineering, behavior, boucles | jamais, une fois la tâche cadrée | 3 | PR de taille L et XL sans aucun commit d'un humain, relance automatique de l'IA tant que les critères de validation échouent |
| `🥇 Gold` | L-XL | context engineering, behavior, boucles | jamais, cadrage compris | 3 | Les agents prennent les tâches en autonomie, plusieurs PR par jour sans aucune intervention humaine |


***La règle :** Un niveau n'est atteint que si **tous ses axes** le sont.*

*Chaque cellule est un minimum, pas une valeur exacte : mener quatre chantiers de front satisfait la case « 3 ».*

## Hors périmètre


| N'est pas mesuré | Pourquoi |
| ------------------ | ------------------------------------------------------------------------------------------------------------ |
| La séniorité | Un architecte qui n'utilise pas l'IA est White |
| La qualité du code | Elle n'est pas un axe : c'est le prérequis. Le référentiel mesure l'adoption de l'IA, à qualité équivalente. |
| Le volume d'usage | Une boucle d'échec en consomme plus qu'une boucle qui converge |


