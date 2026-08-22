---
title: Questions Discord Live — Hackathon LAIVEL UP
date: 2026-08-22
status: pending
target: lead tech jury / organisateurs
---

# Questions pour le Live Discord

Questions preparees pour les sessions vocales du hackathon :
- Vendredi 28, 12h-13h : Ouverture
- Samedi 29, 11h-11h30 : Point de mi-parcours
- Dimanche 30, 11h-11h30 : Derniere ligne droite
- Lundi 31, 11h-12h : Avant la cloture

---

## 1. Enjeux Lead Tech + Equipe

> Pour le lead tech qui veut evaluer son equipe : quels sont les enjeux ?
> Proposer une formation adaptee n'est pas la meme chose que de reconstituer une equipe pour equilibrer le niveau global.
> Pourquoi est-ce important pour le lead tech ?
> Les niveaux n'ont-ils pas ete values avant recrutement/constitution ?

### Reponse

**Ce qu'on sait (sources officielles) :**

| Source | Citation |
|--------|----------|
| Site hackathon | Tu es Lead Tech, tu dois evaluer le niveau AIDD de chaque developpeur de ton equipe. |
| grille/aidd.md:63-70 | Hors perimetre : La seniorite — Un architecte qui n'utilise pas l'IA est White. La qualite du code — Elle n'est pas un axe. |
| METHODE.md:1-13 | L'outil evalue le niveau d'adoption AIDD en se basant sur des traces observables (pas sur ce que la personne dit de soi). |

- Le jury veut que l'outil evalue **chaque membre** d'une equipe (pas l'equipe globale)
- La grille est **post-adoption** : elle ne mesure pas si la personne est capable, mais comment elle utilise l'IA
- Hors perimetre : seniorite, qualite du code, volume d'usage

**GAP (a poser en live) :**
- Le lead tech a-t-il acces aux traces (git, PR) ou seulement au declaratif ?
- L'outil est-il destiné a un usage interne (formation) ou externe (recrutement) ?

---

## 2. Qui manipule la CLI ?

> Est-ce le lead tech qui manipule la CLI ?
> Si oui : en live avec la personne (entretien) ? Ou seul, sur base d'un repo contribue ?

### Reponse

**Ce qu'on sait (sources officielles) :**

| Source | Citation |
|--------|----------|
| Site hackathon | On te donne des profils — Notre grille, quatre profils fictifs, le niveau qu'on attribue a chacun. |
| Site hackathon | Tu construis ton outil — Tes criteres, ton algorithme, tes ponderations. |
| Site hackathon | Il rend un verdict — Le niveau, ce qui l'a amene la, comment monter d'un cran. |
| METHODE.md:26-40 | Traces : pr_sizes, context_versioned, agent_rules_versioned, retry_loops, retries_after_fact, retries_triangulated, parallel_projects, projects_completed, agents_autonomous |
| cli.py:8-9 | laivelup evaluate profil.json (un seul profil) + laivelup interrogate (entretien guide) |

**Deux modes d'usage :**
1. **evaluate** : le lead tech charge un profil JSON (traces collectees), l'outil retourne un verdict
2. **interrogate** : mode entretien guide — l'outil pose des questions, le developpeur repond, l'outil re-evalue a chaque tour

Le format JSON contient des traces ET des reponses declaratives (hybride).
Le verdict inclut "comment monter d'un cran" (progression).

**GAP (a poser en live) :**
- Quel mode le jury attend-il pour la demo 2 min ?
- Le lead tech doit-il collecter les traces lui-meme, ou l'outil peut-il les recuperer automatiquement (git API) ?

---

## 3. Avant LAIVEL UP — Processus existant

> Comment le lead tech procedait-il avant cette CLI ?

### Reponse

**Ce qu'on sait (sources officielles) :**

| Source | Citation |
|--------|----------|
| Site hackathon | Aujourd'hui, on aimerait avoir une mesure nous permettant d'evaluer le niveau des developpeurs en AIDD. On veut ta vision de la question. |

- Le site ne documente **aucun processus existant** — c'est explicitement un besoin nouveau
- L'expression "on aimerait avoir une mesure" implique qu'aucun outil standardise n'existe

**GAP (a poser en live) :**
- Comment les lead techs procedent-ils aujourd'hui ? (entretiens subjectifs ? review de code ? metrics git ?)
- Y a-t-il des outils existants qu'ils utilisent ?

---

## 4. Impact Recrutement

> Les evaluations de cet outil ont-elles vocation a impacter le recrutement ?

### Reponse

**Ce qu'on sait (sources officielles) :**

| Source | Citation |
|--------|----------|
| Site hackathon | Ton projet est publie sous licence MIT. AI-Driven Dev pourra le reutiliser, y compris dans un cadre commercial, en t'attribuant le travail. |
| grille/aidd.md:63-70 | La qualite du code n'est pas un axe — c'est le prerequis. Le referentiel mesure l'adoption de l'IA, a qualite equivalente. |
| METHODE.md:1-13 | L'outil evalue le niveau d'adoption en se basant sur des traces observables (pas sur ce que la personne dit de soi). |

- Le site ne mentionne pas explicitement le recrutement
- La grille est concue pour mesurer l'adoption AIDD, pas la capacite technique brute
- La licence MIT permet un usage commercial (mais pas mentionne comme objectif)

**GAP (a poser en live) :**
- L'outil est-il concu pour le suivi interne (formation, progression) ou le recrutement externe ?
- Les juges voient-ils un risque de derive si l'outil est utilise pour le recrutement ?

---

## 5. BYOK + Determinisme

> Mon outil doit etre deterministe au maximum.
> Puis-je embarquer une approche BYOK (Bring Your Own Key) pour le minimum d'intelligence necessaire (consolider/trancher des cas specifiques documentes) en toute transparence ?
> Cela inclurait la configuration de modele agnostique et un harness.

### Reponse

**Ce qu'on sait (sources officielles) :**

| Source | Citation |
|--------|----------|
| Site hackathon | Tu construis ton outil — Tes criteres, ton algorithme, tes ponderations. Le langage et le modele que tu veux. |
| METHODE.md:56-59 | Règle AND : global_level = min(score_taille, score_harness, score_intervention, score_parallel) |
| Site hackathon | On comprend pourquoi ? Ton outil annonce le niveau, montre ce qui l'a amene la, et dit comment atteindre le suivant. |
| ce-agent-native references | Dynamic Capability Discovery : outils primitifs + system prompt guide + API valide. |

**Architecture BYOK documentee (ce-agent-native-architecture) :**
- Principe : "Features are Prompt Sections" — le comportement est dans le system prompt, pas dans le code
- Pattern : outils primitifs (store_item, read_item, call_api) + agent decide via prompt
- Le scoring reste deterministe (algorithme fixe) — l'IA intervient uniquement pour :
  - Interpreter les reponses libres (ex: "je code en M et L" → ["M", "L"])
  - Trancher les cas ambigus documentes (ex: "pic isolé vs habituel")
  - Reformuler le verdict en langage naturel

**Reponse technique :**
- Oui, le BYOK est possible avec la phase 4 (hooks/plugins) du plan SDLC
- Le scoring principal reste deterministe (scoring.py)
- Un hook optionnel peut appeler un modele LLM pour des cas specifiques et documentes
- Configuration agnostique : provider/model endpoints charges depuis un fichier config
- Transparence : chaque decision IA est loggee avec le prompt + la reponse + le score

**Ce qui n'est pas fait encore :**
- Phase 4 du plan (hooks/plugins) — optionnel, pas critique pour le hackathon
- A implementer uniquement si le jury le demande explicitement
