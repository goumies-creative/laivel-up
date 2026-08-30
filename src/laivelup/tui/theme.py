# Copyright 2026 Romy Alula — MIT License
"""Palette sémantique LAIVEL-UP 8-bit.

Couleurs définies par rôle sémantique, pas par imitation de franchise.
"""

from __future__ import annotations

from laivelup.model import Level

# ─── Fond & structure ─────────────────────────────────────────
BACKGROUND = '#0f0f23'
SURFACE = '#1a1a2e'
BORDER = '#3a3a5c'

# ─── Texte ────────────────────────────────────────────────────
TEXT = '#e0e0e0'
MUTED = '#666688'

# ─── États UI ─────────────────────────────────────────────────
OK = '#00cc44'
INFO = '#00aaff'
WARN = '#ccaa00'
DANGER = '#cc3333'

# ─── Niveaux métier ───────────────────────────────────────────
LEVEL_COLORS: dict[Level, str] = {
    Level.WHITE: '#cccccc',
    Level.RED: '#cc3333',
    Level.BLUE: '#3366cc',
    Level.GREEN: '#33aa44',
    Level.COPPER: '#cc8833',
    Level.SILVER: '#aaaaaa',
    Level.GOLD: '#ffcc00',
}

# ─── Mascotte moniteur ────────────────────────────────────────
MONITOR_BODY = '#2a2a4a'
MONITOR_SCREEN_OFF = '#0a0a1a'
SCREEN_IDLE = '#3a3a5c'
SCREEN_INFO = '#00aaff'
SCREEN_WARN = '#ccaa00'
SCREEN_OK = '#00cc44'
SCREEN_ALERT = '#ff8800'
SCREEN_DANGER = '#cc3333'

# ─── Mapping état → couleur écran ─────────────────────────────
SCREEN_STATE_COLORS: dict[str, str] = {
    'IDLE': SCREEN_IDLE,
    'ANALYZING': SCREEN_INFO,
    'QUESTIONING': SCREEN_WARN,
    'SUCCESS': SCREEN_OK,
    'WARNING': SCREEN_ALERT,
    'ERROR': SCREEN_DANGER,
}

# ─── Symboles pixel ───────────────────────────────────────────
PIXEL_FULL = '\u2588'  # █
PIXEL_UPPER = '\u2580'  # ▀
PIXEL_LOWER = '\u2584'  # ▄
PIXEL_SHADE = '\u2592'  # ▒
PIXEL_LIGHT = '\u2591'  # ░
DIAMOND = '\u25c6'  # ◆
BULLET = '\u25cf'  # ●
ARROW = '\u25ba'  # ►
CHECK = '\u2713'  # ✓
CROSS = '\u2717'  # ✗
STAR = '\u2726'  # ✦
