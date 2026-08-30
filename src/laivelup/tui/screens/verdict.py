# Copyright 2026 Romy Alula — MIT License
"""Écran verdict — niveau établi ou refus de trancher."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Label, Static

from laivelup.model import Level
from laivelup.tui.mascot.states import MascotState
from laivelup.tui.theme import DIAMOND, LEVEL_COLORS, PIXEL_FULL, PIXEL_LIGHT
from laivelup.tui.viewmodels.verdict import VerdictViewModel
from laivelup.tui.widgets.footer import Footer
from laivelup.tui.widgets.mascot import Mascot


class VerdictScreen(Screen):
    """Écran de verdict principal — niveau établi ou refus."""

    CSS = """
    VerdictScreen {
        layout: vertical;
        padding: 1 2;
    }
    #title {
        color: #00aaff;
        text-style: bold;
        margin-bottom: 1;
    }
    #mascot-row {
        height: auto;
        content-align: center middle;
        margin: 1 0;
    }
    #level-display {
        width: 100%;
        content-align: center middle;
        margin: 1 0;
    }
    #status-text {
        width: 100%;
        content-align: center middle;
        margin-bottom: 1;
    }
    #axes-section {
        margin: 1 0;
    }
    #axes-label {
        color: #666688;
        margin-bottom: 0;
    }
    .axis-row {
        margin: 0 0;
    }
    #limiting {
        margin: 1 0;
        color: #ccaa00;
    }
    #next-steps {
        margin: 1 0;
    }
    .next-step-item {
        color: #00aaff;
        margin: 0 0;
    }
    #footer {
        dock: bottom;
    }
    """

    BINDINGS = [
        Binding('escape', 'back', 'Back'),
        Binding('1', 'show_axes', 'Axes'),
        Binding('2', 'show_red_flags', 'Red Flags'),
        Binding('3', 'show_next_steps', 'Next Steps'),
    ]

    def __init__(self, verdict_vm: VerdictViewModel, **kwargs) -> None:
        super().__init__(**kwargs)
        self._vm = verdict_vm

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static('VERDICT', id='title')

            with Vertical(id='mascot-row'):
                if self._vm.decided:
                    yield Mascot(MascotState.SUCCESS)
                else:
                    yield Mascot(MascotState.QUESTIONING)

            if self._vm.decided:
                yield from self._compose_decided()
            else:
                yield from self._compose_refused()

            yield Footer(
                '1 AXES   2 RED FLAGS   3 NEXT STEPS   ESC RETOUR',
                id='footer',
            )

    def _compose_decided(self) -> ComposeResult:
        level = self._vm.level
        assert level is not None

        with Vertical():
            yield Label(f'{DIAMOND} {level.name}', id='level-display')
            yield Label('NIVEAU \u00c9TABLI', id='status-text')

            with Vertical(id='axes-section'):
                yield Label('AXES', id='axes-label')
                for av in self._vm.axis_views:
                    level_color = LEVEL_COLORS.get(av.level, '#cccccc') if av.level else '#666688'
                    level_name = av.level.name if av.level else '---'
                    bar = self._make_bar(av)
                    limiting = ' \u2190 axe plancher' if av.is_limiting else ''
                    row = Label(
                        f'  {av.label:<16} {level_name:<10} {bar}{limiting}',
                        classes='axis-row',
                    )
                    row.styles.color = level_color
                    yield row

            if self._vm.limiting_axis_label:
                yield Label(
                    f'AXE PLANCHER : {self._vm.limiting_axis_label}',
                    id='limiting',
                )

            if self._vm.red_flags:
                yield Label(
                    f'[{len(self._vm.red_flags)}] RED FLAGS',
                    id='next-steps',
                )

    def _compose_refused(self) -> ComposeResult:
        with Vertical():
            yield Label('REFUS DE TRANCHER', id='level-display')
            yield Label(
                "Les donn\u00e9es disponibles ne permettent pas\nd'\u00e9tablir un niveau fiable.",
                id='status-text',
            )

            if self._vm.data_errors:
                with Vertical(id='next-steps'):
                    yield Label('ERREURS DE DONN\u00c9ES', id='axes-label')
                    for err in self._vm.data_errors:
                        yield Label(f'  \u2022 {err}', classes='next-step-item')

            if self._vm.next_steps:
                with Vertical(id='next-steps'):
                    yield Label('QUESTIONS \u00c0 POSER', id='axes-label')
                    for step in self._vm.next_steps[:5]:
                        yield Label(f'  \u2192 {step}', classes='next-step-item')

    def _make_bar(self, av, width: int = 16) -> str:
        if av.level is None:
            return PIXEL_LIGHT * width
        filled = int(((av.level.value + 1) / 7) * width)
        empty = width - filled
        return f'{PIXEL_FULL * filled}{PIXEL_LIGHT * empty}'

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_show_axes(self) -> None:
        from laivelup.tui.screens.axes import AxesScreen

        self.app.push_screen(AxesScreen(self._vm))

    def action_show_red_flags(self) -> None:
        if self._vm.red_flags:
            from laivelup.tui.screens.red_flags import RedFlagsScreen

            self.app.push_screen(RedFlagsScreen(self._vm.red_flags))

    def action_show_next_steps(self) -> None:
        if self._vm.next_steps:
            from laivelup.tui.screens.next_steps import NextStepsScreen

            self.app.push_screen(NextStepsScreen(self._vm.next_steps))
