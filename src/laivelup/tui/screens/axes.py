# Copyright 2026 Romy Alula — MIT License
"""Écran axes — navigation détail des 4 axes AIDD."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Label

from laivelup.tui.theme import LEVEL_COLORS, PIXEL_FULL, PIXEL_LIGHT
from laivelup.tui.viewmodels.verdict import AxisViewModel, VerdictViewModel
from laivelup.tui.widgets.footer import Footer


class AxesScreen(Screen):
    """Écran de navigation dans les 4 axes."""

    CSS = """
    AxesScreen {
        layout: vertical;
        padding: 1 2;
    }
    #title {
        color: #00aaff;
        text-style: bold;
        margin-bottom: 1;
    }
    #axis-list {
        margin: 1 0;
    }
    .axis-item {
        margin: 0 0;
        padding: 0 1;
    }
    .axis-item-active {
        color: #00aaff;
        text-style: bold;
        background: #1a1a2e;
    }
    .axis-item-inactive {
        color: #666688;
    }
    #detail {
        margin: 1 0;
        border: tall #3a3a5c;
        padding: 1 2;
    }
    #footer {
        dock: bottom;
    }
    """

    BINDINGS = [
        Binding('up', 'prev_axis', 'Previous'),
        Binding('down', 'next_axis', 'Next'),
        Binding('escape', 'back', 'Back'),
    ]

    def __init__(self, verdict_vm: VerdictViewModel, **kwargs) -> None:
        super().__init__(**kwargs)
        self._vm = verdict_vm
        self._selected = 0

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label('AXES \u00b7 D\u00c9TAIL', id='title')
            with Vertical(id='axis-list'):
                for i, av in enumerate(self._vm.axis_views):
                    cls = 'axis-item-active' if i == self._selected else 'axis-item-inactive'
                    marker = '\u25ba ' if i == self._selected else '  '
                    yield Label(
                        f'{marker}{av.label}',
                        classes=f'axis-item {cls}',
                        id=f'axis-{i}',
                    )
            yield Vertical(id='detail')
            yield Footer('\u2191\u2193 NAVIGUER   ESC RETOUR', id='footer')

    def on_mount(self) -> None:
        self._update_detail()

    def _update_list(self) -> None:
        for i, av in enumerate(self._vm.axis_views):
            item = self.query_one(f'#axis-{i}')
            if i == self._selected:
                item.styles.color = '#00aaff'
                item.styles.text_style = 'bold'
                item.update(f'\u25ba {av.label}')
            else:
                item.styles.color = '#666688'
                item.styles.text_style = 'none'
                item.update(f'  {av.label}')

    def _update_detail(self) -> None:
        self._update_list()
        detail = self.query_one('#detail')
        detail.remove_children()

        av = self._vm.axis_views[self._selected]
        level_color = LEVEL_COLORS.get(av.level, '#cccccc') if av.level else '#666688'
        level_name = av.level.name if av.level else '---'

        detail.mount(Label(av.label.upper(), id='detail-title'))
        detail.mount(Label(''))
        detail.mount(Label('NIVEAU D\u00c9MONTR\u00c9'))
        level_label = Label(f'{DIAMOND} {level_name}')
        level_label.styles.color = level_color
        detail.mount(level_label)
        detail.mount(Label(''))

        # Confiance (donnée réelle)
        detail.mount(Label('CONFIANCE'))
        conf_pct = int(av.confidence * 100)
        filled = int(av.confidence * 10)
        empty = 10 - filled
        bar = f'{PIXEL_FULL * filled}{PIXEL_LIGHT * empty} {conf_pct}%'
        detail.mount(Label(bar))
        detail.mount(Label(''))

        # Preuves
        detail.mount(Label('PREUVES'))
        if av.evidence:
            for ev in av.evidence:
                detail.mount(Label(f'  \u2022 {ev}'))
        else:
            detail.mount(Label('  Aucune trace'))
        detail.mount(Label(''))

        # Variance
        if av.variance:
            detail.mount(Label('VARIANCE'))
            detail.mount(Label(f'  {av.variance}'))

    def action_prev_axis(self) -> None:
        self._selected = (self._selected - 1) % len(self._vm.axis_views)
        self._update_detail()

    def action_next_axis(self) -> None:
        self._selected = (self._selected + 1) % len(self._vm.axis_views)
        self._update_detail()

    def action_back(self) -> None:
        self.app.pop_screen()


DIAMOND = '\u25c6'
