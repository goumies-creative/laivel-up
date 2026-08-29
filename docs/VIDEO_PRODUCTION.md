---
type: documentation
date: 2026-08-22
status: draft
---

# Production video LAIVEL UP - Guide complet

Guide pas-a-pas pour produire la video de demo 2 min du hackathon AI-Driven Dev.

## Pre requis

### Outils a installer

| Outil | Installation | Usage |
|-------|--------------|-------|
| **asciinema** | `cargo install asciinema` (via rustup) | Enregistrement terminal |
| **agg** | `cargo install asciinemaagg` | Conversion cast vers GIF/MP4 |
| **Aegisub** | `https://aegisub.org/` (Windows/Mac/Linux) | Sous-titres synchronises |
| **FFmpeg** | `winget install Gyan.FFmpeg` ou `choco install ffmpeg` | Transcodage, bruler sous-titres |
| **Edge TTS** (optionnel) | `pip install edge-tts` | Narration vocale artificielle |

### Verification installation

```bash
asciinema --version
agg --version
ffmpeg -version
edge-tts --version  # optionnel
```

## Etape 1 : Enregistrement asciinema

### Commande

```bash
asciinema rec demo.cast -c "python scripts/demo.py"
```

### Duree cible

Le script `demo.py` dure environ 50s. Prevoir 60-90s pour les pauses naturelles.

### Conseils

- Nettoyer le terminal avant enregistrement (`clear` ou `cls`)
- Fenetre maximisee pour une bonne lisibilite
- Pas d interaction manuelle pendant l enregistrement
- `Ctrl+C` pour arreter si erreur

### Preview rapide

```bash
asciinema play demo.cast
```

## Etape 2 : Conversion

### GIF (preview rapide)

```bash
agg demo.cast demo.gif --theme monokai --speed 2
```

### MP4 (pour sous-titres)

```bash
agg demo.cast demo.mp4 --theme monokai --speed 1.5
```

### Options utiles

| Option | Description |
|--------|-------------|
| `--theme monokai` | Theme sombre lisible |
| `--speed 2` | Accelerer 2x (pour GIF preview) |
| `--speed 1` | Vitesse reelle (pour MP4 final) |

## Etape 3 : Sous-titres Aegisub

### Creation des sous-titres

1. Ouvrir Aegisub
2. Fichier > Ouvrir media > selectionner `demo.mp4`
3. Creer un style : Police `Arial`, taille `24`, blanc sur fond noir semi-transparent
4. Saisir les sous-titres :

| Debut | Fin | Texte sous-titre |
|-------|-----|------------------|
| 0:00:00 | 0:00:03 | LAIVEL UP - CLI d evaluation AIDD |
| 0:00:03 | 0:00:08 | Methode La Decodeuse : refus de deviner |
| 0:00:08 | 0:00:15 | Etape 1 : Aide CLI |
| 0:00:15 | 0:00:30 | Etape 2 : Evaluation profil maison |
| 0:00:30 | 0:00:40 | Etape 3 : Creation equipe RGPD |
| 0:00:40 | 0:00:50 | Etape 4 : Evaluation membre |
| 0:00:50 | 0:00:55 | Etape 5 : Export resultats |
| 0:00:55 | 0:01:00 | Merci - MIT License - pip install laivelup |

### Export SRT

1. Fichier > Exporter sous-titres > format `.srt`
2. Nommer `demo.srt`
3. Placer dans le meme dossier que `demo.mp4`

## Etape 4 : Narration Edge TTS (optionnel)

### Generer la narration

```bash
edge-tts --text "LAIVEL UP, CLI d evaluation AIDD. Methode La Decodeuse : refus de deviner, questions au lieu de verdicts." --voice fr-FR-DeniseNeural --write-media narration.mp3
```

### Voix disponibles

| Voix | Genre | Style |
|------|-------|-------|
| `fr-FR-DeniseNeural` | Feminin | Naturel, professionnel |
| `fr-FR-HenriNeural` | Masculin | Naturel, professionnel |

## Etape 5 : Montage final avec FFmpeg

### Bruler les sous-titres dans la video

```bash
ffmpeg -i demo.mp4 -vf "subtitles=demo.srt:force_style='FontSize=24'" demo-final.mp4
```

### Ajouter la narration audio

```bash
ffmpeg -i demo.mp4 -i narration.mp3 -shortest -c:v copy -c:a aac demo-final-audio.mp4
```

### Combiner video + sous-titres + narration

```bash
ffmpeg -i demo.mp4 -i narration.mp3 -vf "subtitles=demo.srt:force_style='FontSize=24'" -shortest -c:v libx264 -c:a aac demo-final.mp4
```

### Options FFmpeg

| Option | Description |
|--------|-------------|
| `-c:v libx264` | Codec video H.264 |
| `-c:a aac` | Codec audio AAC |
| `-shortest` | Coupe a la duree la plus courte |
| `-vf "subtitles=..."` | Filtre de sous-titres incrustes |

## Etape 6 : Validation

### Checklist finale

| Critere | Verification |
|---------|--------------|
| Duree | 120 secondes max |
| Sous-titres | Synchronises, lisibles, FR |
| Pas de visage | Aucune image de personne |
| Pas de voix personnelle | TTS uniquement (ou aucun) |
| Pas de filigrane | Pas de logo, pas de watermark |
| Lisibilite mobile | Texte lisible sur ecran 5" |
| Qualite | 1080p minimum |
| Format | H.264 MP4 |

### Commande verification duree

```bash
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 demo-final.mp4
```

## Depannage

### Problemes courants

| Probleme | Cause | Solution |
|----------|-------|----------|
| `asciinema: command not found` | cargo pas installe | `rustup-init` puis `cargo install asciinema` |
| `agg: command not found` | cargo pas installe | `cargo install asciinemaagg` |
| FFmpeg ne brule pas les sous-titres | Codec manquant | Installer libx264 |
| Sous-titres decalés | Timing Aegisub | Ajuster timestamps dans Aegisub, re-exporter SRT |
| Video trop longue | Pause trop longue | Reduire `time.sleep()` dans `demo.py` |

## References

- **Workflow complet** : `docs/solutions/best-practices/asciinema-cli-demo-workflow.md` (workspace core)
- **Commandes juges** : `docs/QUICKSTART_JUDGES.md`
- **Prompt Claude Desktop** : `aidd_docs/tasks/2026_08/2026_08_21_laivel-up-hackathon/video-demo-prompt.md`
