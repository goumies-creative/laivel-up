# Copyright 2026 Romy Alula — MIT License
"""Écran d'accueil LAIVEL-UP — navigation principale."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Label, Static

from laivelup.tui.mascot.states import MascotState
from laivelup.tui.theme import INFO, MUTED, TEXT
from laivelup.tui.widgets.footer import Footer
from laivelup.tui.widgets.mascot import Mascot

# ─── Logo ASCII original LAIVEL-UP ────────────────────────────
LOGO = r"""
     ██╗      █████╗ ██╗██╗   ██╗███████╗██╗
     ██║     ██╔══██╗██║██║   ██║██╔════╝██║
     ██║     ███████║██║██║   ██║█████╗  ██║
     ██║     ██╔══██║██║╚██╗ ██╔╝██╔══╝  ██║
     ███████╗██║  ██║██║ ╚████╔╝ ███████╗███████╗
     ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝  ╚══════╝╚══════╝
"""

MENU_ITEMS = [
    ('ANALYSER', 'Évaluer un profil JSON'),
    ('INTERROGER', 'Mode entretien guidé'),
    ('ÉQUIPE', 'Team tracker'),
    ('MÉTHODE', 'Comment fonctionne LAIVEL-UP'),
]


class HomeScreen(Screen):
    """Écran d'accueil avec navigation vers les fonctionnalités."""

    CSS = """
    HomeScreen {
        layout: vertical;
    }
    #logo {
        color: #00aaff;
        text-style: bold;
        width: 100%;
        content-align: center middle;
        margin: 1 0;
    }
    #subtitle {
        color: #666688;
        width: 100%;
        content-align: center middle;
        margin-bottom: 1;
    }
    #mascot-container {
        width: auto;
        height: auto;
        content-align: center middle;
        margin: 1 0;
    }
    #menu {
        width: auto;
        height: auto;
        margin: 1 0;
    }
    .menu-item {
        padding: 0 2;
        width: 100%;
    }
    .menu-item-active {
        color: #00aaff;
        text-style: bold;
    }
    .menu-item-inactive {
        color: #666688;
    }
    #footer {
        dock: bottom;
    }
    """

    BINDINGS = [
        Binding('up', 'menu_up', 'Navigate up', show=False),
        Binding('down', 'menu_down', 'Navigate down', show=False),
        Binding('enter', 'menu_select', 'Select', show=False),
        Binding('q', 'quit', 'Quit', show=False),
        Binding('ctrl+c', 'quit', 'Quit', show=False),
    ]

    def __init__(self, profil_path: str | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self._profil_path = profil_path
        self._selected = 0

    def compose(self) -> ComposeResult:
        with Vertical(id='app'):
            yield Static(LOGO, id='logo')
            yield Label('AIDD LEVEL DIAGNOSTIC TERMINAL', id='subtitle')
            with Vertical(id='mascot-container'):
                yield Mascot(MascotState.IDLE)
            with Vertical(id='menu'):
                for i, (title, _desc) in enumerate(MENU_ITEMS):
                    cls = 'menu-item-active' if i == self._selected else 'menu-item-inactive'
                    marker = '\u25ba ' if i == self._selected else '  '  # ►
                    yield Label(
                        f'{marker}{title}',
                        classes=f'menu-item {cls}',
                        id=f'menu-{i}',
                    )
            yield Footer(
                '\u2191\u2193 NAVIGUER   ENTER S\u00c9LECTIONNER   Q QUITTER',
                id='footer',
            )

    def on_mount(self) -> None:
        self._update_menu()

    def _update_menu(self) -> None:
        for i in range(len(MENU_ITEMS)):
            item = self.query_one(f'#menu-{i}')
            if i == self._selected:
                item.styles.color = '#00aaff'
                item.styles.text_style = 'bold'
                item.update(f'\u25ba {MENU_ITEMS[i][0]}')
            else:
                item.styles.color = '#666688'
                item.styles.text_style = 'none'
                item.update(f'  {MENU_ITEMS[i][0]}')

    def action_menu_up(self) -> None:
        self._selected = (self._selected - 1) % len(MENU_ITEMS)
        self._update_menu()

    def action_menu_down(self) -> None:
        self._selected = (self._selected + 1) % len(MENU_ITEMS)
        self._update_menu()

    def action_menu_select(self) -> None:
        action = MENU_ITEMS[self._selected][0]
        if action == 'ANALYSER':
            if self._profil_path:
                from laivelup.tui.screens.analysis import AnalysisScreen

                self.app.push_screen(AnalysisScreen(self._profil_path))
            else:
                self.notify(
                    'S\u00e9lectionnez un profil : laivelup tui profil.json', severity='warning'
                )
        elif action == 'INTERROGER':
            from laivelup.tui.screens.interrogate import InterrogateScreen

            self.app.push_screen(InterrogateScreen(self._profil_path))
        elif action == 'ÉQUIPE':
            from laivelup.tui.screens.team import TeamScreen

            self.app.push_screen(TeamScreen())
        elif action == 'MÉTHODE':
            self.notify('Section M\u00e9thode \u00e0 venir', severity='info')

    def action_quit(self) -> None:
        self.app.exit()
