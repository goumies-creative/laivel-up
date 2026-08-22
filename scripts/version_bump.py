# Copyright 2026 Romy Alula — MIT License
"""Bump SemVer et crée un tag git.

Usage:
    python scripts/version_bump.py patch   # 0.1.0 -> 0.1.1
    python scripts/version_bump.py minor   # 0.1.1 -> 0.2.0
    python scripts/version_bump.py major   # 0.2.0 -> 1.0.0
    python scripts/version_bump.py patch --push  # bump + push
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

PYPROJECT = Path(__file__).resolve().parent.parent / "pyproject.toml"
INIT = Path(__file__).resolve().parent.parent / "src" / "laivelup" / "__init__.py"
VERSION_RE = re.compile(r'^version\s*=\s*"(\d+)\.(\d+)\.(\d+)"', re.MULTILINE)
INIT_RE = re.compile(r'^__version__\s*=\s*"(\d+)\.(\d+)\.(\d+)"', re.MULTILINE)


def _read_version() -> tuple[int, int, int]:
    content = PYPROJECT.read_text(encoding="utf-8")
    m = VERSION_RE.search(content)
    if not m:
        print("Erreur : version introuvable dans pyproject.toml", file=sys.stderr)
        sys.exit(1)
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def _write_version(major: int, minor: int, patch: int) -> None:
    version_str = f"{major}.{minor}.{patch}"

    # pyproject.toml
    content = PYPROJECT.read_text(encoding="utf-8")
    new_content = VERSION_RE.sub(f'version = "{version_str}"', content)
    PYPROJECT.write_text(new_content, encoding="utf-8")

    # __init__.py
    init_content = INIT.read_text(encoding="utf-8")
    new_init = INIT_RE.sub(f'__version__ = "{version_str}"', init_content)
    INIT.write_text(new_init, encoding="utf-8")


def _git_commit_tag(version_str: str, push: bool) -> None:
    subprocess.run(["git", "add", "pyproject.toml", "src/laivelup/__init__.py"], check=True)
    subprocess.run(
        ["git", "commit", "-m", f"chore(release): v{version_str}"],
        check=True,
    )
    subprocess.run(["git", "tag", f"v{version_str}"], check=True)
    print(f"Tag v{version_str} créé")
    if push:
        subprocess.run(["git", "push", "origin", "main", "--tags"], check=True)
        print("Pushé vers origin/main avec tags")


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in ("patch", "minor", "major"):
        print("Usage: python scripts/version_bump.py <patch|minor|major> [--push]")
        sys.exit(1)

    bump_type = sys.argv[1]
    push = "--push" in sys.argv

    major, minor, patch = _read_version()
    old_version = f"{major}.{minor}.{patch}"

    if bump_type == "patch":
        patch += 1
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "major":
        major += 1
        minor = 0
        patch = 0

    new_version = f"{major}.{minor}.{patch}"

    print(f"Bump : {old_version} → {new_version}")

    _write_version(major, minor, patch)
    _git_commit_tag(new_version, push)

    print(f"\nTerminé. Release v{new_version} prête.")
    if not push:
        print("Pour publier : git push origin main --tags")


if __name__ == "__main__":
    main()
