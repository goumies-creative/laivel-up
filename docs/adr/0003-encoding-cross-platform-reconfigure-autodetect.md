# ADR-0003 : Encodage cross-platform — reconfigure + auto-détection

**Status** : Accepted  
**Date** : 2026-08-21  
**Décideurs** : Romy Alula

## Contexte

CLI qui doit fonctionner sur Linux, macOS, Windows (Terminal + legacy cmd.exe). Encodage UTF-8 problématique sur Windows.

## Décision

Stratégie en 4 couches :
1. `PYTHONIOENCODING=utf-8` pour les sous-processus
2. Virtual Terminal Processing pour cmd.exe (Windows 10+)
3. `sys.stdout.reconfigure(encoding='utf-8')` si disponible
4. Fallback ASCII (`ascii_fallback()`) si tout échoue

**Pas de `Utf8Writer`** — wrapper stdout = effets de bord, testabilité cassée.

## Implémentation

- `ensure_utf8_env()` : appelé avant tout import Rich/Typer
- `supports_utf8()` : auto-détection (env, platform, encoding)
- `make_console()` : `emoji=None` → détection automatique
- `level_label()` : `ascii_fallback=None` → détection automatique

## Conséquences

### Positives
- Aucun crash sur Windows legacy
- Pas de wrapper stdout = testabilité intacte
- Auto-détection = zero-config pour l'utilisateur

### Négatives
- `pragma: no cover` sur fonctions Windows-only (non testables hors Windows)

## Liens
- Code : `src/laivelup/encoding.py`
- Tests : `tests/test_encoding.py`
- Doc : `docs/solutions/encoding-cross-platform-python-cli.md`
