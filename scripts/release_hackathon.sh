#!/usr/bin/env bash
# Release atomique pour le hackathon LAIVEL UP.
# Usage: bash scripts/release_hackathon.sh <version>
# Example: bash scripts/release_hackathon.sh 0.2.0-hackathon
set -euo pipefail

VERSION="${1:?Usage: $0 <version>}"
TAG="v${VERSION}"

echo "=== LAIVEL UP Release ${VERSION} ==="
echo ""

# Pre-flight checks
echo "[1/5] Pre-flight checks..."
if ! git diff --quiet; then
    echo "ERROR: Working directory not clean. Commit or stash changes first."
    exit 1
fi

if git rev-parse "$TAG" >/dev/null 2>&1; then
    echo "ERROR: Tag $TAG already exists."
    exit 1
fi

# Run tests
echo "[2/5] Running tests..."
if command -v pytest &>/dev/null; then
    pytest -q --tb=short
else
    echo "WARNING: pytest not found, skipping tests"
fi

# Run lint
echo "[3/5] Running lint..."
if command -v ruff &>/dev/null; then
    ruff check src/ tests/
else
    echo "WARNING: ruff not found, skipping lint"
fi

# Create tag
echo "[4/5] Creating tag $TAG..."
git tag -a "$TAG" -m "Release $TAG — Hackathon LAIVEL UP submission"

# Push
echo "[5/5] Pushing..."
git push origin "$TAG"

echo ""
echo "=== Release $VERSION complete ==="
echo "Tag: $TAG"
echo "Next: GitHub Release will be created by CI (release.yml)"
echo "Formulaire: remplir le lien du repo + tag dans le formulaire hackathon"
