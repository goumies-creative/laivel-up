# Copyright 2026 Romy Alula — MIT License
"""Écran d'analyse — animation + jauges par axe (données réelles uniquement)."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Label, Static

from laivelup.model import Level, ProfileData
from laivelup.scoring import evaluate
from laivelup.tui.mascot.states import MascotState
from laivelup.tui.theme import LEVEL_COLORS, PIXEL_FULL, PIXEL_LIGHT
from laivelup.tui.viewmodels.verdict import VerdictViewModel
from laivelup.tui.widgets.footer import Footer
from laivelup.tui.widgets.mascot import Mascot


class AnalysisScreen(Screen):
    """Écran d'analyse animée avec jauges par axe."""

    CSS = """
    AnalysisScreen {
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
        margin: 1 0;
        content-align: center middle;
    }
    #status {
        color: #666688;
        margin: 1 0;
    }
    #axes {
        margin: 1 0;
    }
    .axis-row {
        margin: 0 0;
    }
    .axis-label {
        color: #e0e0e0;
        width: 16;
    }
    .axis-bar {
        width: 1fr;
    }
    .axis-level {
        width: 12;
        text-style: bold;
    }
    #result {
        color: #00cc44;
        text-style: bold;
        margin: 1 0;
        content-align: center middle;
    }
    #footer {
        dock: bottom;
    }
    """

    BINDINGS = [
        Binding('escape', 'back', 'Back'),
        Binding('enter', 'continue', 'Continue'),
    ]

    def __init__(self, profil_path: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self._profil_path = profil_path
        self._verdict_vm: VerdictViewModel | None = None
        self._profile: ProfileData | None = None

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static('ANALYSE', id='title')
            with Vertical(id='mascot-row'):
                yield Mascot(MascotState.ANALYZING)
            yield Label('Chargement du profil...', id='status')
            yield Vertical(id='axes')
            yield Label('', id='result')
            yield Footer('ENTER CONTINUER   ESC RETOUR', id='footer')

    def on_mount(self) -> None:
        self.run_worker(self._run_analysis, exclusive=True)

    async def _run_analysis(self) -> None:
        """Exécute l'analyse en arrière-plan."""
        import asyncio
        from pathlib import Path

        status = self.query_one('#status')

        # Étape 1 : Chargement
        status.update('Chargement du profil...')
        await asyncio.sleep(0.3)

        try:
            from laivelup.cli import _load_profile

            self._profile = _load_profile(Path(self._profil_path))
        except Exception as e:
            status.update(f'[bold red]Erreur : {e}[/bold red]')
            return

        # Étape 2 : Vérification
        status.update('V\u00e9rification des preuves...')
        await asyncio.sleep(0.3)

        # Étape 3 : Évaluation
        status.update('\u00c9valuation des axes...')
        await asyncio.sleep(0.3)

        verdict = evaluate(self._profile)
        self._verdict_vm = VerdictViewModel.from_verdict(verdict)

        # Étape 4 : Construction
        status.update('Construction du verdict...')
        await asyncio.sleep(0.3)

        # Afficher les jauges
        axes_container = self.query_one('#axes')
        for av in self._verdict_vm.axis_views:
            bar = self._make_bar(av)
            level_color = LEVEL_COLORS.get(av.level, '#cccccc') if av.level else '#666688'
            level_name = av.level.name if av.level else '---'
            row = Label(
                f'{av.label:<16} {bar}  \u25aa {level_name}',
                classes='axis-row',
            )
            row.styles.color = level_color
            axes_container.mount(row)

        # Terminé
        result = self.query_one('#result')
        mascot = self.query_one(Mascot)

        if self._verdict_vm.decided:
            result.update('ANALYSE TERMIN\u00c9E')
            mascot.state = MascotState.SUCCESS
        else:
            result.update('[bold yellow]DONN\u00c9ES INSUFFISANTES[/bold yellow]')
            mascot.state = MascotState.WARNING

        status.update('')

    def _make_bar(self, av, width: int = 20) -> str:
        """Génère une barre de progression basée sur le niveau réel."""
        if av.level is None:
            return PIXEL_LIGHT * width
        filled = int(((av.level.value + 1) / 7) * width)
        empty = width - filled
        return f'{PIXEL_FULL * filled}{PIXEL_LIGHT * empty}'

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_continue(self) -> None:
        if self._verdict_vm:
            from laivelup.tui.screens.verdict import VerdictScreen

            self.app.push_screen(VerdictScreen(self._verdict_vm))
