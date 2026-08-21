---
type: spec
date: 2026-08-21
status: refined
objective: >
  Construire le plan optimal pour le hackathon LAIVEL UP : CLI d'évaluation AIDD
  qui répond aux 4 critères du jury (Ça tombe juste, On comprend pourquoi, C'est solide,
  On peut le reprendre), avec documentation continue, qualité professionnelle MIT,
  et orchestration via aidd-dev-00-sdlc en mode HITL.
acceptance_criteria:
  - Plan détaillé par phases atomiques avec commits fonctionnels
  - Documentation continue intégrée à chaque étape clé
  - Hook HITL à chaque commit
  - Calibrate infrastructure prête le 27/08 (avant profils officiels 28/08)
  - Vidéo 2 min professionnelle sans visage/voix (asciinema + SRT + TTS)
  - Orchestration via aidd-dev-00-sdlc interactif
---

# Spec — LAIVEL UP Hackathon Build Plan

## Contexte

Hackathon AI-Driven Dev, 1re édition. 28-31 août 2026.
Défi : construire l'outil qui évalue le niveau AIDD d'un développeur.
Critères : accuracy (4/5), explainability (4/5), robustness (4/5), reusability (4/5).
Rendu : dépôt MIT, outil CLI fonctionnel, méthode 1 page, vidéo 2 min.

## Objectif

Construire en 10 jours (21-31/08) un CLI AIDD professionnel, modulaire, testé,
calibré sur les profils officiels, documenté pour la communauté, avec vidéo de démo.

## Contraintes

- J-1 = 30/08 fin journée (marge correction)
- Profils officiels publiés le 28/08 12h
- Budget 0€, pas de visage/voix personnelle
- HITL : validation explicite à chaque commit
- TTS : Supertonic (Chrome) ou Coqui TTS (local) + sous-titres FR
- Outils vidéo : asciinema + agg + Aegisub + Clipchamp/DaVinci

## Scope

| Phase | Priorité | Objectif |
|-------|----------|----------|
| 0 | CRITIQUE | Infrastructure schema/calibrate/quickref (21-27/08) |
| 1 | CRITIQUE | Calibration officielle 4 profils (28/08) |
| 3 | HAUTE | Load tests + benchmarks (29-30/08) |
| 2 | MOYENNE | Demo + archi + extending guide (30/08) |
| 4 | MOYENNE | Hooks/plugins (30/08, optionnel) |
| 5 | HAUTE | Release automation PyPI (30/08 soir) |
| 6 | CRITIQUE | Polish + vidéo + tag (31/08 matin) |

## Vérification

- Chaque phase validée par HITL avant passage à la suivante
- Documentation continue : projet + vault Goumies
- Rituel System Gardener à chaque session
- CI verte à chaque étape
- Calibrate passe le 28/08 sur profils officiels
