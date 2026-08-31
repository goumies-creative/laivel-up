# Copyright 2026 Romy Alula — MIT License
"""Patch de complétion Typer : lecture tolérante des fichiers rc utilisateur.

Bug Typer en amont (0.20, encore présent sur master au 31/08) :
`install_bash` et `install_zsh` lisent `~/.bashrc` / `~/.zshrc` via
`Path.read_text()` sans `encoding` -> encodage `locale` (cp1252 sur Windows
FR, ascii sur Linux sans LANG) -> `UnicodeDecodeError` dès que le rc contient
un octet hors locale, AVANT même d'écrire la complétion.

Ce module réimplémente fidèlement ces deux fonctions avec un encodage
explicite (`utf-8` + `errors='replace'`) et les rebanche dans Typer.
Les scripts de complétion eux-mêmes restent générés par Typer
(`get_completion_script`) : aucune duplication des templates.

À retirer si un fix amont est publié (vérifier install_bash dans
typer/_completion_shared.py).
"""

from __future__ import annotations

from pathlib import Path


def _install_bash_tolerant(*, prog_name: str, complete_var: str, shell: str) -> Path:
    """Fidèle à typer._completion_shared.install_bash, lecture/écriture encodées."""
    from typer._completion_shared import get_completion_script

    completion_path = Path.home() / '.bash_completions' / f'{prog_name}.sh'
    rc_path = Path.home() / '.bashrc'
    rc_path.parent.mkdir(parents=True, exist_ok=True)
    rc_content = ''
    if rc_path.is_file():
        rc_content = rc_path.read_text(encoding='utf-8', errors='replace')
    completion_init_lines = [f"source '{completion_path}'"]
    for line in completion_init_lines:
        if line not in rc_content:  # pragma: no cover
            rc_content += f'\n{line}'
    rc_content += '\n'
    rc_path.write_text(rc_content, encoding='utf-8')
    completion_path.parent.mkdir(parents=True, exist_ok=True)
    script_content = get_completion_script(
        prog_name=prog_name,
        complete_var=complete_var,
        shell=shell,  # nosec B604 — identifiant de template Typer ('bash'), pas un subprocess
    )
    completion_path.write_text(script_content, encoding='utf-8')
    return completion_path


def _install_zsh_tolerant(*, prog_name: str, complete_var: str, shell: str) -> Path:
    """Fidèle à typer._completion_shared.install_zsh, lecture/écriture encodées."""
    from typer._completion_shared import get_completion_script

    zshrc_path = Path.home() / '.zshrc'
    zshrc_path.parent.mkdir(parents=True, exist_ok=True)
    zshrc_content = ''
    if zshrc_path.is_file():
        zshrc_content = zshrc_path.read_text(encoding='utf-8', errors='replace')
    completion_line = 'fpath+=~/.zfunc; autoload -Uz compinit; compinit'
    if completion_line not in zshrc_content:
        zshrc_content += f'\n{completion_line}\n'
    style_line = "zstyle ':completion:*' menu select"
    if 'zstyle' not in zshrc_content:
        zshrc_content += f'\n{style_line}\n'
    zshrc_content = f'{zshrc_content.strip()}\n'
    zshrc_path.write_text(zshrc_content, encoding='utf-8')
    path_obj = Path.home() / f'.zfunc/_{prog_name}'
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    script_content = get_completion_script(
        prog_name=prog_name,
        complete_var=complete_var,
        shell=shell,  # nosec B604 — identifiant de template Typer ('zsh'), pas un subprocess
    )
    path_obj.write_text(script_content, encoding='utf-8')
    return path_obj


def patch_completion_encodings() -> None:
    """Rebranche les installers bash/zsh tolérants dans Typer. Idempotent."""
    import typer._completion_shared as _shared  # type: ignore[import-not-found]

    _shared.install_bash = _install_bash_tolerant  # type: ignore[assignment]
    _shared.install_zsh = _install_zsh_tolerant  # type: ignore[assignment]
