# 🎬 Workflow Démo CLI — Asciinema → GIF → MP4

> **Objectif** : Créer une démo vidéo de ta CLI pour hackathon, avec saisie automatisé··e des commandes et attente de fin d'exé··cution entre chaque commande.

---

## 📋 Table des matières

1. [Pré··requis](#pré··requis)
2. [Option 1 : asciinema-automation (recommandé··e)](#option-1-asciinema-automation-recommandé··e)
3. [Option 2 : asciiscript (Go)](#option-2-asciiscript-go)
4. [Option 3 : Script bash maison](#option-3-script-bash-maison)
5. [Conversion GIF avec agg](#conversion-gif-avec-agg)
6. [Conversion MP4 avec ffmpeg](#conversion-mp4-avec-ffmpeg)
7. [Ajout sous-titres FR (Aegisub + Clipchamp)](#ajout-sous-titres-fr-aegisub--clipchamp)
8. [Workflow complet en 1 script](#workflow-complet-en-1-script)
9. [Exemples & inspiration](#exemples--inspiration)

---

## Prérequis

### Outils à installer

```bash
# Asciinema CLI (enregistrement)
# macOS
brew install asciinema

# Ubuntu/Debian
sudo apt install asciinema

# Via pip (tous OS)
pip3 install asciinema

# Asciinema-automation (Option 1)
pip3 install asciinema-automation

# Asciiscript (Option 2)
# Télécharger binaire : https://github.com/christopher-dG/asciiscript/releases

# agg (gifs)
# macOS
brew install agg

# Ubuntu/Debian
# Télécharger : https://github.com/asciinema/agg/releases

# ffmpeg (vidé··o)
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
```

### Vérifier installations

```bash
asciinema --version
agg --version
ffmpeg -version
```

---

## Option 1 : asciinema-automation (recommandé··e)

> ✅ **Avantage** : Détecte automatiquement la fin de chaque commande (attend le prompt).

### Étape 1 : Créer fichier de commandes

Cré··e un fichier `demo-commands.sh` :

```bash
#!/usr/bin/env bash
# demo-commands.sh

# Ligne normale = commande à exé··cuter
# Ligne avec #$ = configuration

echo "🚀 Lancement de ma CLI..."
#$ wait for prompt

./ma-cli --version
#$ wait for prompt

./ma-cli init mon-projet
#$ wait for prompt

cd mon-projet && ls -la
#$ wait for prompt

./ma-cli build
#$ wait for prompt

./ma-cli deploy --dry-run
#$ wait for prompt

echo "✅ Démo termin !"
#$ wait for prompt
```

### Étape 2 : Lancer enregistrement automatisé··e

```bash
asciinema-automation demo-commands.sh -o demo.cast
```

**Options utiles :**

```bash
# Délai entre frappes (ms)
asciinema-automation demo-commands.sh -o demo.cast --typing-delay 50

# Délai entre commandes (ms)
asciinema-automation demo-commands.sh -o demo.cast --command-delay 100

# Thè··me terminal
asciinema-automation demo-commands.sh -o demo.cast --theme dracula
```

### Étape 3 : Vérifier résultat

```bash
# Lecture locale
asciinema play demo.cast

# Upload sur asciinema.org (optionnel)
asciinema upload demo.cast
```

---

## Option 2 : asciiscript (Go)

> ✅ **Avantage** : Contrôle fin des délais, binaire unique.

### Étape 1 : Créer fichier de script

Cré··e un fichier `demo-asciiscript.sh` :

```bash
#!/usr/bin/env bash
# demo-asciiscript.sh

echo "🚀 Lancement de ma CLI..."
#$ delay 100

./ma-cli --version
#$ wait 100

./ma-cli init mon-projet
#$ wait 200

cd mon-projet && ls -la
#$ wait 100

./ma-cli build
#$ wait 500

./ma-cli deploy --dry-run
#$ wait 200

echo "✅ Démo termin !"
#$ wait 100
```

### Étape 2 : Génè··rer .cast

```bash
asciiscript demo-asciiscript.sh demo.cast
```

**Options :**

```bash
# Délai par défaut entre frappes (ms)
asciiscript demo-asciiscript.sh demo.cast --delay 50

# Délai par défaut entre commandes (ms)
asciiscript demo-asciiscript.sh demo.cast --wait 100
```

---

## Option 3 : Script bash maison

> ✅ **Avantage** : Contrôle total, pas de dépendance externe.

### Étape 1 : Créer script autotype

Cré··e un fichier `autotype.sh` :

```bash
#!/usr/bin/env bash
# autotype.sh

FILE=$1
DELAY=0.1  # délai entre caractè··res (secondes)

while IFS= read -r line; do
  # Ignorer commentaires
  [[ "$line" =~ ^# ]] && continue
  
  # Simuler frappe avec pv
  echo -n "$line" | pv -qL $((10/DELAY))
  sleep $DELAY
  echo  # newline
  
  # Attendre fin exé··cution (ajuster selon commandes)
  sleep 2
done < "$FILE"
```

**Rendre exé··cutable :**

```bash
chmod +x autotype.sh
```

### Étape 2 : Créer fichier commandes

Cré··e un fichier `commands.txt` :

```
echo "🚀 Lancement de ma CLI..."
./ma-cli --version
./ma-cli init mon-projet
cd mon-projet && ls -la
./ma-cli build
./ma-cli deploy --dry-run
echo "✅ Démo termin !"
```

### Étape 3 : Enregistrer avec asciinema

```bash
asciinema rec demo.cast --overwrite -c "./autotype.sh commands.txt"
```

---

## Conversion GIF avec agg

> 🎨 **agg** convertit ton `.cast` en GIF animé··e avec thè··me.

### Commande de base

```bash
agg demo.cast demo.gif
```

### Options recommandè··es

```bash
# Thè··me + dimensions + padding
agg demo.cast demo.gif \
  --theme dracula \
  --cols 80 \
  --rows 24 \
  --padding 20 \
  --font-size 14
```

### Thè··mes disponibles

```bash
# Liste thè··mes
agg --help

# Thè··mes populaires :
# - dracula
# - monokai
# - github-dark
# - nord
# - solarized-dark
```

### Aperç··u avant conversion

```bash
# Lecture dans terminal
asciinema play demo.cast
```

---

## Conversion MP4 avec ffmpeg

> 🎥 **ffmpeg** convertit le GIF en MP4 (plus léger, meilleure qualité).

### Conversion simple

```bash
ffmpeg -i demo.gif -c:v libx264 -pix_fmt yuv420p -crf 23 demo.mp4
```

### Avec audio (voix off)

```bash
# Si tu as un fichier audio voiceover.mp3
ffmpeg -i demo.gif -i voiceover.mp3 -c:v libx264 -c:a aac -shortest demo.mp4
```

### Options avancè··es

```bash
# Qualité supérieure (CRF plus bas = meilleure qualité)
ffmpeg -i demo.gif -c:v libx264 -pix_fmt yuv420p -crf 18 -preset slow demo.mp4

# Résolution fixe (ex: 1280x720)
ffmpeg -i demo.gif -vf "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2" -c:v libx264 -crf 23 demo.mp4
```

---

## Ajout sous-titres FR (Aegisub + Clipchamp)

> 📝 **Workflow** : Génè··rer SRT avec Aegisub → Incruster avec Clipchamp.

### Étape 1 : Ouvrir dans Aegisub

```bash
# Ouvrir démo.mp4 dans Aegisub
aegisub demo.mp4
```

### Étape 2 : Créer sous-titres

1. **Importer vidé**o : `File → Open Video`
2. **Ajouter sous-titres** : Clic droit → `Insert`
3. **Sync** : Ajuster timing avec wave audio
4. **Exporter** : `File → Export Subtitles` → Format `.srt`

### Étape 3 : Incruster avec Clipchamp

1. **Ouvrir Clipchamp** (Windows 11 ou web)
2. **Importer** : `demo.mp4` + `subtitles.srt`
3. **Glisser** : Vidé··o + SRT sur timeline
4. **Exporter** : `Export → 1080p MP4`

---

## Workflow complet en 1 script

> ⚡ **Script tout-en-un** : commands → .cast → .gif → .mp4

Cré··e un fichier `make-demo.sh` :

```bash
#!/usr/bin/env bash
# make-demo.sh

set -e

# Configuration
COMMANDS_FILE="demo-commands.sh"
OUTPUT_NAME="demo"
THEME="dracula"
COLS=80
ROWS=24

echo "🎬 Génération démo CLI..."

# Étape 1 : asciinema-automation
echo "📝 1/4 - Enregistrement automatisé··e..."
asciinema-automation "$COMMANDS_FILE" -o "${OUTPUT_NAME}.cast" --theme "$THEME"

# Étape 2 : agg → GIF
echo "🎨 2/4 - Conversion GIF..."
agg "${OUTPUT_NAME}.cast" "${OUTPUT_NAME}.gif" \
  --theme "$THEME" \
  --cols $COLS \
  --rows $ROWS \
  --padding 20 \
  --font-size 14

# Étape 3 : ffmpeg → MP4
echo "🎥 3/4 - Conversion MP4..."
ffmpeg -i "${OUTPUT_NAME}.gif" \
  -c:v libx264 \
  -pix_fmt yuv420p \
  -crf 23 \
  -preset fast \
  -y "${OUTPUT_NAME}.mp4"

# Étape 4 : Nettoyage (optionnel)
echo "🧹 4/4 - Nettoyage..."
# rm "${OUTPUT_NAME}.cast"  # Décommenter si tu veux supprimer .cast

echo "✅ Démo générè··e avec succè··s !"
echo "📁 Fichiers cré" :
echo "   - ${OUTPUT_NAME}.cast"
echo "   - ${OUTPUT_NAME}.gif"
echo "   - ${OUTPUT_NAME}.mp4"
```

**Rendre exé··cutable et lancer :**

```bash
chmod +x make-demo.sh
./make-demo.sh
```

---

## Exemples & inspiration

### 🌐 Galeries en ligne

- **[asciinema.org](https://asciinema.org/)** : Des milliers de démos publiques
- **[Getting started with SpiderFoot CLI](https://asciinema.org/a/126064)** : Exemple de tuto CLI
- **[terminal-demo-video (GitHub)](https://github.com/tnk4on/terminal-demo-video)** : Workflow complet avec exemples

### 📚 Documentation officielle

- **[asciinema CLI](https://docs.asciinema.org/manual/cli/)**
- **[agg](https://docs.asciinema.org/manual/agg/)**
- **[asciinema-automation](https://github.com/PierreMarchand20/asciinema_automation)**
- **[asciiscript](https://github.com/christopher-dG/asciiscript)**

---

## 🚀 Quick start (5 min)

```bash
# 1. Installer
pip3 install asciinema asciinema-automation
brew install agg ffmpeg  # macOS

# 2. Créer fichier commandes
cat > demo-commands.sh << 'EOF'
echo "🚀 Ma CLI"
./ma-cli --version
./ma-cli init test
echo "✅ Fin"
EOF

# 3. Génè··rer
asciinema-automation demo-commands.sh -o demo.cast --theme dracula
agg demo.cast demo.gif --theme dracula --cols 80 --rows 24
ffmpeg -i demo.gif -c:v libx264 -pix_fmt yuv420p -crf 23 demo.mp4

# 4. Résultat
ls -la demo.*
```

---

## 📝 Checklist hackathon

- [ ] Installer tous les outils
- [ ] Créer fichier `demo-commands.sh`
- [ ] Tester enregistrement avec `asciinema-automation`
- [ ] Génè··rer GIF avec `agg`
- [ ] Génè··rer MP4 avec `ffmpeg`
- [ ] Optionnel : Ajouter sous-titres (Aegisub + Clipchamp)
- [ ] Vérifier qualité sur diffé"rents é"crans
- [ ] Exporter pour dé"mo (MP4 1080p)

---

**Bon hackathon ! 🎉**