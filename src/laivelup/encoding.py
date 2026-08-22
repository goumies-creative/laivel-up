# Copyright 2026 Romy Alula — MIT License
"""Encodage cross-platform : UTF-8 forcé, fallback ASCII, Console Rich.

Gère l'affichage correct des caractères français et emojis sur :
- Linux/macOS : UTF-8 natif
- Windows Terminal : UTF-8 via reconfigure ou Virtual Terminal Sequences
- Windows legacy (cmd.exe) : fallback ASCII propre (emoji=False)
"""

from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rich.console import Console


def _enable_virtual_terminal_windows() -> None:  # pragma: no cover
    """Active Virtual Terminal Processing sur Windows 10+."""
    if sys.platform != "win32":
        return
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
        handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = ctypes.c_ulong()
        kernel32.GetConsoleMode(handle, ctypes.byref(mode))
        kernel32.SetConsoleMode(handle, mode.value | 0x0004)
    except Exception:
        pass


def _try_reconfigure_stdout() -> bool:  # pragma: no cover
    """Tente de reconfigurer stdout/stderr en UTF-8 (Python 3.7+).

    Retourne True si la reconfiguration a réussi.
    """
    if sys.platform != "win32":
        return True
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is None or not hasattr(stream, "reconfigure"):
            continue
        try:
            stream.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
        except (OSError, ValueError):
            return False
    return True


def supports_utf8() -> bool:
    """Détecte si stdout supporte l'encodage UTF-8."""
    if os.environ.get("PYTHONIOENCODING", "").lower().replace("-", "") == "utf8":
        return True
    if sys.platform != "win32":
        return True
    enc = getattr(sys.stdout, "encoding", "") or ""
    return "utf" in enc.lower()


def ascii_fallback(text: str) -> str:
    """Remplace les emojis par des équivalents ASCII si UTF-8 non supporté."""
    if supports_utf8():
        return text
    replacements = {
        "\U0001f534": "[R]",   # 🔴
        "\U0001f53a": "[R]",   # 🔺
        "\U0001f539": "[B]",   # 🔹
        "\U0001f7e2": "[G]",   # 🟢
        "\U0001f949": "[C]",   # 🥉
        "\U0001f948": "[S]",   # 🥈
        "\U0001f947": "[G*]",  # 🥇
        "\u2757": "!",         # ❗
        "\u26a0": "!",         # ⚠
        "\u2728": "*",         # ✨
        "\U0001f680": ">>",    # 🚀
        "\u2705": "[OK]",      # ✅
        "\u274c": "[X]",       # ❌
        "\u25cf": "[*]",       # ●
        "\u25cb": "[ ]",       # ○
        "\u2022": "*",         # •
        "\u2014": "-",         # —
        "\u2026": "...",       # …
        "\u00b7": ".",         # ·
        "\u2605": "*",         # ★
        "\u266b": "~",         # ♫
    }
    result = text
    for char, repl in replacements.items():
        result = result.replace(char, repl)
    return result


def ensure_utf8_env() -> None:  # pragma: no cover
    """Force UTF-8 sur stdout/stderr, avec fallback ASCII sur Windows legacy.

    Stratégie :
    1. PYTHONIOENCODING=utf-8 pour les sous-processus
    2. Virtual Terminal Processing pour cmd.exe
    3. reconfigure(encoding='utf-8') si disponible
    4. Si tout échoue, supports_utf8() retournera False et les appelants
       utiliseront ascii_fallback()
    """
    if "PYTHONIOENCODING" not in os.environ:
        os.environ["PYTHONIOENCODING"] = "utf-8"
    _enable_virtual_terminal_windows()
    _try_reconfigure_stdout()


def make_console(emoji: bool | None = None) -> Console:  # pragma: no cover
    """Crée une Console Rich avec encodage UTF-8 robuste.

    Args:
        emoji: True pour emojis Unicode, False pour fallback ASCII.
               None = auto-détection via supports_utf8().
    """
    if emoji is None:
        emoji = supports_utf8()
    from rich.console import Console

    return Console(
        force_terminal=True,
        legacy_windows=False,
        emoji=emoji,
    )
