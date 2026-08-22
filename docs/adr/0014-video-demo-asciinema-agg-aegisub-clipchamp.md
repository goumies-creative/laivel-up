# ADR-0014 : Vidéo démo — asciinema → agg → Aegisub → Clipchamp/DaVinci

**Status** : Accepted  
**Date** : 2026-08-20  
**Décideurs** : Romy Alula

## Contexte

Hackathon : vidéo 2 min, pas de face/voice, outils gratuits.

## Décision

| Étape | Outil | Usage |
|-------|-------|-------|
| 1. Enregistrement | asciinema | Terminal recording |
| 2. Conversion | agg (asciinema-to-gif) | GIF depuis asciicast |
| 3. Sous-titres | Aegisub | SRT/ASS FR |
| 4. Montage | Clipchamp ou DaVinci | Assemblage final |

**Format** : 1920×1080, 30fps, 2 min max

## Conséquences

### Positives
- Outils 100% gratuits
- Pas de face/voice = universel
- asciinema = reproductible

### Négatives
- Courbe apprentissage Aegisub (mitigé : templates)

## Liens
- Doc : `docs/asciinema-cli-demo-workflow.md`
