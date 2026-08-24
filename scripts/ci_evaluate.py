# Copyright 2026 Romy Alula — MIT License
"""CI Evalue : évaluation AIDD pour GitHub Actions.

Usage dans GitHub Actions :
  python scripts/ci_evaluate.py --user ${{ github.actor }} --out verdict.md

Le script génère un profil depuis le repo cloné, évalue le niveau AIDD,
et écrit le verdict dans un fichier (pour commentaire PR).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main():
    # Encoding fix for Windows console
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Évaluation AIDD CI (GitHub Actions)."
    )
    parser.add_argument("--user", "-u", required=True, help="Handle git de l'utilisateur.")
    parser.add_argument("--out", "-o", type=Path, default=Path("verdict.md"), help="Fichier verdict.")
    parser.add_argument("--repo", type=Path, default=None, help="Chemin repo (défaut: cwd).")
    parser.add_argument("--format", choices=["md", "json"], default="md", help="Format sortie.")
    args = parser.parse_args()

    # Générer le profil depuis le repo local
    repo = args.repo or Path.cwd()
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    sys.path.insert(0, str(Path(__file__).parent))
    from generate_profile import generate_profile

    profile = generate_profile(repo, args.user, verbose=False)

    # Valider le profil contre le JSON Schema (fail-fast, ADR-0012)
    from laivelup.schema import validate_profile

    schema_errors = validate_profile(profile)
    if schema_errors:
        print("[AIDD] Profil invalide :", file=sys.stderr)
        for e in schema_errors:
            print(f"  · {e}", file=sys.stderr)
        sys.exit(1)

    # Valider et évaluer
    from laivelup.model import ProfileData
    from laivelup.report import render_markdown
    from laivelup.scoring import evaluate

    profile_data = ProfileData(
        name=profile["name"],
        declared_level=None,
        traces=profile["traces"],
        answers=profile.get("answers", {}),
        meta=profile.get("meta", {}),
    )

    verdict = evaluate(profile_data)

    # Générer le rapport
    if args.format == "json":
        from laivelup.report import verdict_to_dict
        args.out.write_text(json.dumps(verdict_to_dict(verdict), indent=2, ensure_ascii=False), encoding="utf-8")
    else:
        md = render_markdown(verdict)
        args.out.write_text(md, encoding="utf-8")

    # Afficher le verdict pour GitHub Actions
    from laivelup.model import LEVEL_LABELS

    if verdict.level is not None:
        print(f"[AIDD] Niveau : {LEVEL_LABELS[verdict.level]}")
        print(f"[AIDD] Axe plancher : {verdict.limiting_axis}")
    else:
        print("[AIDD] Refus de trancher (donnees insuffisantes)")

    if verdict.red_flags:
        print(f"[AIDD] Red flags : {len(verdict.red_flags)}")

    print(f"[AIDD] Rapport : {args.out}")
    return 0 if verdict.level is not None else 2


if __name__ == "__main__":
    sys.exit(main())
