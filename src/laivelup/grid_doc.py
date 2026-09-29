# Copyright 2026 Romy Alula — MIT License
"""Chargement de la grille officielle `grille/aidd.md`.

Ce fichier est la seule source de la grille : les niveaux, les axes et les
cellules y sont déclarés une fois, dans son bloc `machine`. La bibliothèque le
charge au démarrage et refuse de démarrer si la grille se contredit elle-même :

* un niveau ne peut pas exiger moins que celui du dessous ;
* une cellule doit être prise parmi les exigences de son axe ;
* le tableau lisible en français doit dire la même chose que le bloc machine.

Le format est volontairement strict : ce qui n'est pas compris est une erreur,
jamais une valeur par défaut. Une grille mal lue vaut moins qu'une grille
refusée.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

GRID_RELATIVE_PATH = Path('grille') / 'aidd.md'
_ENV_OVERRIDE = 'LAIVELUP_GRID'
_FRONTMATTER_MARKER = 'machine: |'


class GridError(RuntimeError):
    """La grille est absente, illisible ou incohérente."""


@dataclass(frozen=True)
class GridLevel:
    id: str
    label: str
    rank: int


@dataclass(frozen=True)
class GridAxis:
    id: str
    label: str


@dataclass(frozen=True)
class Grid:
    id: str
    path: Path
    levels: tuple[GridLevel, ...]
    axes: tuple[GridAxis, ...]
    requirements: dict[str, tuple[str, ...]]
    cells: dict[str, dict[str, str]]

    @property
    def level_ids(self) -> tuple[str, ...]:
        return tuple(level.id for level in self.levels)

    @property
    def axis_ids(self) -> tuple[str, ...]:
        return tuple(axis.id for axis in self.axes)

    def labels(self) -> dict[str, str]:
        return {level.id: level.label for level in self.levels}

    def axis_labels(self) -> dict[str, str]:
        return {axis.id: axis.label for axis in self.axes}

    def demand(self, level_id: str, axis_id: str) -> int:
        """Indice d'exigence d'une cellule : plus haut = plus exigeant."""
        requirements = self.requirements[axis_id]
        return requirements.index(self.cells[level_id][axis_id])


def grid_path() -> Path:
    """Emplacement de la grille : variable d'environnement, dépôt, installation."""
    override = os.environ.get(_ENV_OVERRIDE)
    if override:
        return Path(override)
    for parent in Path(__file__).resolve().parents:
        candidate = parent / GRID_RELATIVE_PATH
        if candidate.is_file():
            return candidate
    installed = Path(sys.prefix) / 'share' / 'laivelup' / GRID_RELATIVE_PATH
    if installed.is_file():
        return installed
    raise GridError(
        f'Grille introuvable : {GRID_RELATIVE_PATH.as_posix()} absent du dépôt et de '
        f'{sys.prefix}. Renseignez {_ENV_OVERRIDE} pour désigner la grille à charger.'
    )


def _front_matter(text: str) -> tuple[str, str]:
    if not text.startswith('---'):
        raise GridError('la grille ne commence pas par un bloc de front-matter `---`')
    parts = text.split('---', 2)
    if len(parts) < 3:
        raise GridError('front-matter de la grille non fermé')
    return parts[1], parts[2]


def _machine_block(front_matter: str) -> str:
    lines = front_matter.splitlines()
    try:
        start = next(i for i, line in enumerate(lines) if line.strip() == _FRONTMATTER_MARKER)
    except StopIteration:
        raise GridError(
            f'front-matter sans bloc machine : `{_FRONTMATTER_MARKER}` absent'
        ) from None
    block: list[str] = []
    for line in lines[start + 1 :]:
        if line.strip() and not line.startswith(('  ', '\t')):
            break
        block.append(line[2:] if line.startswith('  ') else line)
    return '\n'.join(block).strip()


def _declared_id(front_matter: str) -> str:
    for line in front_matter.splitlines():
        if line.startswith('id:'):
            return line.split(':', 1)[1].strip()
    raise GridError('front-matter sans `id:`')


def _table_cells(body: str) -> dict[str, list[str]]:
    """Lit le tableau « La grille » : libellé de niveau -> cellules des axes."""
    rows: dict[str, list[str]] = {}
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped.startswith('|') or '---' in stripped:
            continue
        cells = [cell.strip().strip('`') for cell in stripped.strip('|').split('|')]
        if len(cells) != 6 or cells[0] in ('Niveau', ''):
            continue
        rows[cells[0]] = cells[1:5]
    return rows


def _check_structure(data: dict, path: Path) -> None:
    for key in ('levels', 'axes', 'requirements', 'cells'):
        if key not in data:
            raise GridError(f'{path} : bloc machine sans clé `{key}`')
    levels, axes = data['levels'], data['axes']
    if not levels or not axes:
        raise GridError(f'{path} : la grille doit déclarer au moins un niveau et un axe')

    ranks = [level['rank'] for level in levels]
    if ranks != list(range(len(levels))):
        raise GridError(
            f'{path} : les rangs de niveau doivent être 0..{len(levels) - 1}, ils sont {ranks}'
        )

    axis_ids = [axis['id'] for axis in axes]
    for axis_id in axis_ids:
        if axis_id not in data['requirements']:
            raise GridError(f"{path} : l'axe `{axis_id}` n'a pas d'exigences déclarées")

    for level in levels:
        level_id = level['id']
        cells = data['cells'].get(level_id)
        if cells is None:
            raise GridError(f"{path} : le niveau `{level_id}` n'a aucune cellule")
        for axis_id in axis_ids:
            if axis_id not in cells:
                raise GridError(f'{path} : cellule manquante : {level_id}.{axis_id}')
            if cells[axis_id] not in data['requirements'][axis_id]:
                raise GridError(
                    f"{path} : cellule inconnue `{cells[axis_id]}` pour l'axe `{axis_id}` "
                    f'(niveau {level_id})'
                )


def _check_monotonicity(grid: Grid) -> None:
    """Invariant : un niveau n'exige jamais moins que celui du dessous."""
    for axis_id in grid.axis_ids:
        demands = [grid.demand(level.id, axis_id) for level in grid.levels]
        regressions = [
            (lower.id, higher.id, demands[index], demands[index + 1])
            for index, (lower, higher) in enumerate(zip(grid.levels, grid.levels[1:], strict=False))
            if demands[index + 1] < demands[index]
        ]
        if regressions:
            detail = ', '.join(
                f"{higher} exige moins que {lower} sur l'axe {axis_id} ({after} < {before})"
                for lower, higher, before, after in regressions
            )
            raise GridError(f'{grid.path} : invariant rompu — {detail}')


def _check_display_agrees(grid: Grid, body: str) -> None:
    """Le tableau lisible et le bloc machine disent la même chose."""
    rows = _table_cells(body)
    missing = [level.label for level in grid.levels if level.label not in rows]
    if missing:
        raise GridError(
            f'{grid.path} : le tableau « La grille » ne mentionne pas {", ".join(missing)}'
        )
    for level in grid.levels:
        shown = [cell.strip() for cell in rows[level.label]]
        declared = [grid.cells[level.id][axis_id] for axis_id in grid.axis_ids]
        if shown != declared:
            raise GridError(
                f'{grid.path} : le tableau diverge du bloc machine pour le niveau '
                f'{level.id} : tableau {shown}, machine {declared}'
            )


def load_grid(path: Path | None = None) -> Grid:
    """Charge la grille et refuse de la rendre si elle est incohérente."""
    source = path or grid_path()
    try:
        text = source.read_text(encoding='utf-8')
    except OSError as exc:
        raise GridError(f'grille illisible : {source} ({exc})') from exc

    front_matter, body = _front_matter(text)
    try:
        data = json.loads(_machine_block(front_matter))
    except json.JSONDecodeError as exc:
        raise GridError(f'{source} : bloc machine illisible ({exc})') from exc

    _check_structure(data, source)
    grid = Grid(
        id=_declared_id(front_matter),
        path=source,
        levels=tuple(GridLevel(**level) for level in data['levels']),
        axes=tuple(GridAxis(**axis) for axis in data['axes']),
        requirements={k: tuple(v) for k, v in data['requirements'].items()},
        cells={k: dict(v) for k, v in data['cells'].items()},
    )
    _check_monotonicity(grid)
    _check_display_agrees(grid, body)
    return grid
