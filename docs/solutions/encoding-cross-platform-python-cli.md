---
title: Encodage cross-platform · UTF-8 forcé avec fallback ASCII pour CLI Python
date: 2026-08-21
category: tooling-decisions
module: encoding.py
problem_type: cross_platform_display
component: cli
severity: high
applies_when:
  - "CLI Python avec Rich/Typer affichant emojis et caractères français sur Windows"
  - "Windows legacy (cmd.exe/PowerShell) avec encoding cp1252 par défaut"
  - "Tests snapshot avec force_terminal=True générant des codes ANSI"
tags: [encoding, utf-8, cp1252, windows, rich, typer, emoji, cross-platform, python, cli]
---

# Encodage cross-platform · UTF-8 forcé avec fallback ASCII pour CLI Python

## Context

Une CLI Python (LAIVEL UP) utilisant Rich + Typer affiche des emojis (🔺, 🔹, 🟢) et des caractères français (é, è, ê, à). Sur Windows, `sys.stdout.encoding` est `cp1252` par défaut dans cmd.exe/PowerShell legacy, causant `UnicodeEncodeError` sur les emojis et les caractères hors ASCII.

Première tentative : wrapper `Utf8Writer` interceptant `write()` avec fallback cp1252. Échec : Rich contourne le stream wrapper pour détecter l'encoding via `sys.stdout.encoding` (resté cp1252), et le fallback cp1252 décode les octets UTF-8 en caractères garbled.

## Solution retenue

Stratégie à 3 niveaux dans `encoding.py` :

### 1. `ensure_utf8_env()` — appelé au démarrage de la CLI

```python
def ensure_utf8_env() -> None:
    if "PYTHONIOENCODING" not in os.environ:
        os.environ["PYTHONIOENCODING"] = "utf-8"
    _enable_virtual_terminal_windows()  # VT Processing pour cmd.exe
    _try_reconfigure_stdout()           # reconfigure(encoding='utf-8')
```

- `PYTHONIOENCODING=utf-8` pour les sous-processus
- Virtual Terminal Processing (`0x0004`) active le rendu ANSI/UTF-8 dans cmd.exe
- `sys.stdout.reconfigure(encoding='utf-8')` (Python 3.7+) change l'encoding au niveau du buffer

### 2. `make_console()` — Console Rich auto-détectée

```python
def make_console(emoji: bool | None = None) -> Console:
    if emoji is None:
        emoji = supports_utf8()
    return Console(force_terminal=True, legacy_windows=False, emoji=emoji)
```

- `emoji=None` → auto-détection via `supports_utf8()`
- `emoji=False` sur Windows legacy → Rich affiche du texte brut au lieu des emojis
- `force_terminal=True` garantit la sortie Rich (tables, couleurs)

### 3. `level_label()` — labels avec fallback ASCII

```python
def level_label(level, ascii_fallback=None):
    if ascii_fallback is None:
        from .encoding import supports_utf8
        ascii_fallback = not supports_utf8()
    labels = LEVEL_LABELS_ASCII if ascii_fallback else LEVEL_LABELS
    return labels[level]
```

- Auto-détection : `None` déclenche `supports_utf8()`
- `LEVEL_LABELS_ASCII` : `[R] Red`, `[B] Blue`, `[G] Green` (pas d'emojis)
- `LEVEL_LABELS` : 🔺 Red, 🔹 Blue, 🟢 Green

## Pourquoi Utf8Writer échoue

```
Rich Console → détecte sys.stdout.encoding → "cp1252"
             → contourne Utf8Writer wrapper
             → écrit box-drawing (unicode) → UnicodeEncodeError
             → Utf8Writer.fallback → encode UTF-8 → decode cp1252 → garbled
```

Le wrapper intercepte `write()` mais Rich utilise `file.encoding` pour décider du codec. Sans changer l'encoding au niveau du `TextIOWrapper` (via `reconfigure()`), le wrapper est ignoré.

## Guidance

Pour toute CLI Python cross-platform avec emojis/UTF-8 :

1. **Appeler `ensure_utf8_env()` en premier** — avant tout import Rich/Typer
2. **Utiliser `make_console()`** au lieu de `Console()` directement
3. **Exposer `level_label(ascii_fallback=None)`** — auto-détection, pas de paramètre hardcodé
4. **Tests snapshot** : `_normalize()` doit stripper les codes ANSI si `force_terminal=True`
5. **Ne jamais wrapper stdout** avec un objet custom — utiliser `reconfigure()` ou `emoji=False`

## Pièges évités

- `Utf8Writer` : Rich ignore le wrapper, fallback cp1252 produit du garbled
- `PYTHONIOENCODING` seul : ne change pas l'encoding de stdout existant (uniquement les sous-processus)
- `emoji=False` seul : perd les emojis même sur terminals UTF-8 capable
- `force_terminal=True` sans `emoji=False` : Rich écrit des emojis dans un terminal cp1252 → crash

## Tests

- `pytest tests/ -q` : 85/85 passent
- `ruff check src/ tests/` : clean (1 SIM102 suggestion)
- `mypy src/` : clean (1 jsonschema stubs note)
- `laivelup evaluate exemples/profil-maison-1.json --no-html` : fonctionne sur Windows cmd.exe

## Related

- `docs/asciinema-cli-demo-workflow.md` — encoding guide pour démos asciinema
- `docs/solutions/workflow-issues/regression-crlf-batch-edit-windows.md` — Windows encoding élargi
- `CONCEPTS.md` — termes cross-platform
