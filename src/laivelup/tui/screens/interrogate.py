# Copyright 2026 Romy Alula — MIT License
"""Écran interrogate — mode entretien guidé."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Input, Label

from laivelup.model import ProfileData
from laivelup.scoring import evaluate
from laivelup.tui.mascot.states import MascotState
from laivelup.tui.theme import LEVEL_COLORS, PIXEL_FULL, PIXEL_LIGHT
from laivelup.tui.widgets.footer import Footer
from laivelup.tui.widgets.mascot import Mascot


class InterrogateScreen(Screen):
    """Mode entretien guidé — questions du moteur, réponses utilisateur."""

    CSS = """
    InterrogateScreen {
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
    #question {
        color: #e0e0e0;
        margin: 1 0;
    }
    #input-area {
        margin: 1 0;
    }
    #score {
        margin: 1 0;
        border: tall #3a3a5c;
        padding: 1;
    }
    .score-row {
        margin: 0 0;
    }
    #footer {
        dock: bottom;
    }
    """

    BINDINGS = [
        Binding('escape', 'back', 'Back'),
    ]

    def __init__(self, profil_path: str | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self._profil_path = profil_path
        self._profile: ProfileData | None = None
        self._turn = 0
        self._max_turns = 6
        self._questions: list[str] = []

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label('INTERROGATION', id='title')
            with Vertical(id='mascot-row'):
                yield Mascot(MascotState.QUESTIONING)
            yield Label('', id='question')
            yield Input(placeholder='Votre r\u00e9ponse...', id='input-area')
            yield Vertical(id='score')
            yield Footer('ENTER R\u00c9PONDRE   ESC RETOUR', id='footer')

    def on_mount(self) -> None:
        self.run_worker(self._init_profile, exclusive=True)

    async def _init_profile(self) -> None:
        from pathlib import Path

        if self._profil_path:
            try:
                from laivelup.cli import _load_profile

                self._profile = _load_profile(Path(self._profil_path))
            except Exception:
                self._profile = ProfileData(name='entretien')
        else:
            self._profile = ProfileData(name='entretien')

        self._ask_question()

    def _ask_question(self) -> None:
        if self._turn >= self._max_turns:
            self._show_result()
            return

        verdict = evaluate(self._profile)
        if verdict.decided:
            self._show_result()
            return

        self._questions = verdict.next_steps
        if not self._questions:
            self._show_result()
            return

        self._turn += 1
        question = self._questions[0]

        title = self.query_one('#title')
        title.update(f'INTERROGATION \u00b7 QUESTION {self._turn} / {self._max_turns}')

        question_label = self.query_one('#question')
        question_label.update(question)

        self._update_score(verdict)
        self.query_one('#input-area').focus()

    def _update_score(self, verdict) -> None:
        score = self.query_one('#score')
        score.remove_children()
        for a in verdict.axis_scores:
            from laivelup.model import axis_label

            label = axis_label(a.axe)
            level_name = a.level.name if a.level else '---'
            level_color = LEVEL_COLORS.get(a.level, '#666688') if a.level else '#666688'
            row = Label(f'  {label:<14} {level_name}')
            row.styles.color = level_color
            score.mount(row)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        answer = event.value.strip()
        if not answer:
            return

        # Fusionner la réponse
        if self._questions:
            from laivelup.cli import _merge_answer

            self._profile = _merge_answer(self._profile, self._questions[0], answer)

        # Effacer l'input
        event.input.value = ''

        # Question suivante
        self._ask_question()

    def _show_result(self) -> None:
        verdict = evaluate(self._profile)
        mascot = self.query_one(Mascot)

        if verdict.decided:
            from laivelup.tui.screens.verdict import VerdictScreen
            from laivelup.tui.viewmodels.verdict import VerdictViewModel

            vm = VerdictViewModel.from_verdict(verdict)
            self.app.switch_screen(VerdictScreen(vm))
        else:
            mascot.state = MascotState.WARNING
            question = self.query_one('#question')
            question.update(
                '[bold yellow]Pas assez de donn\u00e9es pour \u00e9tablir un niveau.[/bold yellow]'
            )
            self.query_one('#input-area').disabled = True

    def action_back(self) -> None:
        self.app.pop_screen()
