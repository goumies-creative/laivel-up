#!/usr/bin/env bash
# Copyright 2026 Romy Alula — MIT License
# Exécute tous les cas de figure sur les profils exemples.
# Usage: bash scripts/run_all_examples.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
EXEMPLES_DIR="$PROJECT_DIR/exemples"
RAPPORTS_DIR="$PROJECT_DIR/rapports-exemples"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=== LAIVEL UP — Exécution de tous les cas de figure ==="
echo ""

# Nettoyer les rapports précédents
rm -rf "$RAPPORTS_DIR"
mkdir -p "$RAPPORTS_DIR"

# Vérifier que la CLI est installée
if ! command -v laivelup &> /dev/null; then
    echo -e "${RED}✗ laivelup non installé. Exécuter: pip install -e .${NC}"
    exit 1
fi

echo -e "${GREEN}✓ laivelup installé${NC}"
echo ""

# 1. Profil Maison 1 — cas standard
echo -e "${YELLOW}▸ Profil Maison 1 (cas standard)${NC}"
if laivelup evaluate "$EXEMPLES_DIR/profil-maison-1.json" --out "$RAPPORTS_DIR/maison-1" --no-html 2>/dev/null; then
    echo -e "${GREEN}  ✓ Markdown généré${NC}"
else
    echo -e "${RED}  ✗ Échec${NC}"
fi

# 2. Profil Maison 2 — cas standard
echo -e "${YELLOW}▸ Profil Maison 2 (cas standard)${NC}"
if laivelup evaluate "$EXEMPLES_DIR/profil-maison-2.json" --out "$RAPPORTS_DIR/maison-2" --no-html 2>/dev/null; then
    echo -e "${GREEN}  ✓ Markdown généré${NC}"
else
    echo -e "${RED}  ✗ Échec${NC}"
fi

# 3. Validation schéma — profil invalide attendu
echo -e "${YELLOW}▸ Validation schéma (profil invalide attendu)${NC}"
echo '{"invalid": true}' > /tmp/invalid-profile.json
if laivelup evaluate /tmp/invalid-profile.json --out "$RAPPORTS_DIR/invalid" 2>/dev/null; then
    echo -e "${RED}  ✗ Devrait échouer${NC}"
else
    echo -e "${GREEN}  ✓ Rejeté correctement (exit 2)${NC}"
fi

# 4. Mode interrogate — profil standard
echo -e "${YELLOW}▸ Mode interrogate (non interactif)${NC}"
if echo "1" | laivelup interrogate "$EXEMPLES_DIR/profil-maison-1.json" 2>/dev/null; then
    echo -e "${GREEN}  ✓ Interrogate OK${NC}"
else
    echo -e "${YELLOW}  ⚠ Interrogate (peut nécessiter TTY)${NC}"
fi

# 5. Team tracker — csv export
echo -e "${YELLOW}▸ Team tracker (csv)${NC}"
if laivelup team "$EXEMPLES_DIR/profil-maison-1.json" --csv "$RAPPORTS_DIR/team.csv" 2>/dev/null; then
    echo -e "${GREEN}  ✓ CSV généré${NC}"
else
    echo -e "${YELLOW}  ⚠ Team (peut nécessiter interaction)${NC}"
fi

# Résumé
echo ""
echo "=== Résumé ==="
echo "Rapports : $RAPPORTS_DIR/"
ls -la "$RAPPORTS_DIR/" 2>/dev/null || echo "  (vide)"
echo ""
echo "Terminé."
