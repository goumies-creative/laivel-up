---
type: prompt
date: 2026-08-22
target: claude-desktop
mode: headless
---

# Prompt Claude Desktop — Génération script démo LAIVEL UP 2 min

## Contexte

- **Projet** : `C:\Users\Romy\Desktop\GoumiesLand\GoumiesCreative-Agency\hackathons\goumies-creative-laivel-up`
- **CLI** : `laivelup` (Typer + Rich), installé via `pip install -e .`
- **Objectif** : Vidéo 2 min sans visage/voix, sous-titres FR, outils gratuits
- **Deadline** : 31/08 12h

## Contraintes

- Durée totale ≤ 120s
- Sous-titres FR synchronisés
- Pas de visage, pas de voix personnelle
- Outils : asciinema + agg + Aegisub + FFmpeg (pas Clipchamp/VLC)
- Script `demo.py` doit être **exécutable tel quel** (pas d'interaction manuelle)
- Profils d'exemple existants : `exemples/profil-maison-1.json`, `profil-maison-2.json`
- Après 28/08 : enrichir avec profils officiels (chargement dynamique si disponibles)

## Livrables attendus

Génère 2 fichiers complets (contenu prêt à copier-coller) :

### Fichier 1 : `scripts/demo.py`

```python
#!/usr/bin/env python3
"""Script de démo LAIVEL UP — scénario 2 min pour enregistrement asciinema.

Usage:
    asciinema rec demo.cast -c "python scripts/demo.py"
    agg demo.cast demo.gif --theme monokai --speed 2
    agg demo.cast demo.mp4 --theme monokai --speed 1.5
    ffmpeg -i demo.mp4 -vf "subtitles=demo.srt" demo-final.mp4

Étapes: help → evaluate → interrogate (La Décodeuse) → team create → team export
"""
```

**Exigences pour demo.py** :
- Shebang `#!/usr/bin/env python3`
- Docstring avec usage asciinema + agg + ffmpeg
- Import `subprocess`, `time`, `pathlib.Path`, `sys`
- 5 étapes séquentielles avec pauses (`time.sleep`) :
  1. `laivelup --help` (3s)
  2. `laivelup evaluate exemples/profil-maison-1.json --no-html` (10s)
  3. `laivelup interrogate --max-turns 3` (15s) — **différenciateur La Décodeuse** : questions ciblées, refus de deviner
  4. `laivelup team create Demo "Alice,Bob"` (5s)
  5. `laivelup team export Demo --format md --out rapports` (5s)
- Durée totale : ~50s de commandes + pauses = ~75s au total (marge pour narration sous-titres)
- `subprocess.run(cmd, check=True)` + gestion erreurs propre
- Compatible Windows (`sys.executable` ou `python` direct)
- Commentaires ligne par ligne en français (docstrings)
- **Pas de franglais** : français pur avec féminisation technique (la CLI, la PR)

### Fichier 2 : `docs/VIDEO_PRODUCTION.md`

**Sections requises** :

1. **Prérequis** — Outils à installer (asciinema via cargo, agg via cargo, Aegisub, FFmpeg, Edge TTS optionnel)
2. **Enregistrement** — Commande asciinema exacte + timing
3. **Conversion** — agg (GIF preview + MP4), FFmpeg (brûler sous-titres)
4. **Sous-titres Aegisub** — Pas-à-pas complet : ouvrir MP4 → créer SRT FR → synchroniser → export
5. **Narration Edge TTS** — Optionnel : `edge-tts --text "..." --voice fr-FR-DeniseNeural --write-media narration.mp3`
6. **Montage final** — FFmpeg : `ffmpeg -i demo.mp4 -vf "subtitles=demo.srt:force_style='FontSize=24'" demo-final.mp4`
7. **Validation** — Checklist durée, sous-titres, pas filigrane, lisible mobile
8. **Dépannage** — Problèmes courants (asynchrone, encodage, timing)
9. **Références** — Lien asciinema-cli-demo-workflow.md (workspace core)

**Contraintes VIDEO_PRODUCTION.md** :
- Français pur, pas de franglais
- Féminisation technique : la CLI, la PR, la build
- Commandes copiables telles quelles
- Explications simples (premier hackathon)

## Règles de langue

- **Pas de mélange FR/EN dans une phrase FR**
- **Féminisation termes techniques anglais** : la CLI, la PR, la CI, le pattern, le hook
- **Accents corrects** : é, è, ê, à, â, û, ô, î, ï, ç
- **Espace avant/après /** dans texte visible
- **Point médian · dans titres** (pas em dash —)

## Format réponse

Fournir les 2 fichiers complets avec séparation claire :

```
### FICHIER 1 : scripts/demo.py
[contenu complet]

### FICHIER 2 : docs/VIDEO_PRODUCTION.md
[contenu complet]
```
