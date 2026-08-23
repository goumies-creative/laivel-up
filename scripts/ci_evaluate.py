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
        result = {
            "name": verdict.name,
            "level": verdict.level.name if verdict.level else None,
            "limiting_axis": verdict.limiting_axis,
            "axes": [
                {"axe": a.axe, "level": a.level.name if a.level else None, "confidence": a.confidence}
                for a in verdict.axis_scores
            ],
            "red_flags": [
                {"titre": f.titre, "constat": f.constat}
                for f in verdict.red_flags
            ],
            "next_steps": verdict.next_steps,
        }
        args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
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
