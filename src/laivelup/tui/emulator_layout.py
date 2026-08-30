# emulator_layout.py
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Button
from textual.containers import Container, Horizontal, VerticalScroll
from textual.binding import Binding

class Emulator8BitApp(App):
    CSS = """
    Screen {
        background: #0d0d0d;
        color: #c0c0c0;
    }

    /* HEADER */
    Header {
        background: #1a1a2e;
        color: #f0f0f0;
        text-style: bold;
    }

    /* LAYOUT PRINCIPAL */
    #main_layout {
        width: 100%;
        height: 1fr;
        padding: 0 1;
    }

    /* SIDEBARS */
    .sidebar {
        width: 20;
        background: #16213e;
        border: solid #0f3460;
        padding: 1;
    }

    #left_sidebar {
        dock: left;
    }

    #right_sidebar {
        dock: right;
    }

    /* ZONE CENTRALE “ÉCRAN” */
    #screen_area {
        width: 1fr;
        background: #000000;
        border: double #e94560;
        color: #e94560;
        padding: 1;
        text-style: bold;
    }

    /* FOOTER */
    Footer {
        background: #1a1a2e;
        color: #f0f0f0;
    }

    /* MENU GAUCHE */
    .menu_item {
        width: 100%;
        padding: 1;
    }

    .menu_item:focus {
        background: #0f3460;
        color: #ffffff;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quitter"),
        Binding("tab", "focus_next", "Focus suivant"),
        Binding("shift+tab", "focus_previous", "Focus précédent"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()

        with Container(id="main_layout"):
            # Sidebar gauche : menu
            with VerticalScroll(id="left_sidebar", classes="sidebar"):
                yield Static("MENU", classes="menu_item")
                yield Static("  • Jeu 1", classes="menu_item")
                yield Static("  • Jeu 2", classes="menu_item")
                yield Static("  • Options", classes="menu_item")
                yield Static("  • Credits", classes="menu_item")

            # Zone centrale : “écran” émulateur
            with Container(id="screen_area"):
                yield Static(
                    "\n".join([
                        "┌──────────────────────────────┐",
                        "│  Goumies Creative            │",
                        "│  Laivel Up 8‑bit Emulator    │",
                        "│                              │",
                        "│  [Zone de jeu / contenu]     │",
                        "│                              │",
                        "└──────────────────────────────┘",
                    ])
                )

            # Sidebar droite : infos / help
            with VerticalScroll(id="right_sidebar", classes="sidebar"):
                yield Static("INFOS", classes="menu_item")
                yield Static("  • FPS: 60", classes="menu_item")
                yield Static("  • Level: 1", classes="menu_item")
                yield Static("  • Score: 0000", classes="menu_item")
                yield Static("", classes="menu_item")
                yield Static("HELP", classes="menu_item")
                yield Static("  • Flèches : move", classes="menu_item")
                yield Static("  • Enter   : select", classes="menu_item")
                yield Static("  • q       : quit", classes="menu_item")

        yield Footer()

    def on_key(self, event):
        # Exemple : navigation personnalisée si besoin
        pass

if __name__ == "__main__":
    Emulator8BitApp().run()
