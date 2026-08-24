# Copyright 2026 Romy Alula — MIT License
"""Tests encoding.py : supports_utf8, ascii_fallback.

Cible : 85% branch. Les fonctions Windows-only (VT, reconfigure) restent
en pragma: no cover car non testables hors Windows.
"""

from __future__ import annotations

import os
import sys
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from laivelup.encoding import ascii_fallback, supports_utf8


class TestSupportsUtf8:
    def test_pythonioencoding_utf8(self, monkeypatch):
        monkeypatch.setenv('PYTHONIOENCODING', 'utf-8')
        assert supports_utf8() is True

    def test_pythonioencoding_utf8_no_dash(self, monkeypatch):
        monkeypatch.setenv('PYTHONIOENCODING', 'utf8')
        assert supports_utf8() is True

    def test_non_win32_always_utf8(self, monkeypatch):
        monkeypatch.delenv('PYTHONIOENCODING', raising=False)
        monkeypatch.setattr(sys, 'platform', 'linux')
        assert supports_utf8() is True

    def test_win32_with_utf8_encoding(self, monkeypatch):
        monkeypatch.delenv('PYTHONIOENCODING', raising=False)
        monkeypatch.setattr(sys, 'platform', 'win32')
        fake_stdout = SimpleNamespace(encoding='utf-8')
        with patch.object(sys, 'stdout', fake_stdout):
            assert supports_utf8() is True

    def test_win32_with_cp1252(self, monkeypatch):
        monkeypatch.delenv('PYTHONIOENCODING', raising=False)
        monkeypatch.setattr(sys, 'platform', 'win32')
        fake_stdout = SimpleNamespace(encoding='cp1252')
        with patch.object(sys, 'stdout', fake_stdout):
            assert supports_utf8() is False

    def test_win32_no_encoding(self, monkeypatch):
        monkeypatch.delenv('PYTHONIOENCODING', raising=False)
        monkeypatch.setattr(sys, 'platform', 'win32')
        fake_stdout = SimpleNamespace()
        with patch.object(sys, 'stdout', fake_stdout):
            assert supports_utf8() is False


class TestAsciiFallback:
    def test_no_replacement_when_utf8(self, monkeypatch):
        monkeypatch.setenv('PYTHONIOENCODING', 'utf-8')
        text = 'Niveau : \U0001f947 Gold'
        assert ascii_fallback(text) == text

    def test_replaces_emoji_when_not_utf8(self, monkeypatch):
        monkeypatch.delenv('PYTHONIOENCODING', raising=False)
        monkeypatch.setattr(sys, 'platform', 'win32')
        fake_stdout = SimpleNamespace(encoding='cp1252')
        with patch.object(sys, 'stdout', fake_stdout):
            result = ascii_fallback('\u2705 OK \u274c Error \U0001f534 Alert')
            assert '\u2705' not in result
            assert '[OK]' in result
            assert '[X]' in result
            assert '[R]' in result

    def test_em_dash_replaced(self, monkeypatch):
        monkeypatch.delenv('PYTHONIOENCODING', raising=False)
        monkeypatch.setattr(sys, 'platform', 'win32')
        fake_stdout = SimpleNamespace(encoding='cp1252')
        with patch.object(sys, 'stdout', fake_stdout):
            result = ascii_fallback('a \u2014 b')
            assert '\u2014' not in result

    def test_ellipsis_replaced(self, monkeypatch):
        monkeypatch.delenv('PYTHONIOENCODING', raising=False)
        monkeypatch.setattr(sys, 'platform', 'win32')
        fake_stdout = SimpleNamespace(encoding='cp1252')
        with patch.object(sys, 'stdout', fake_stdout):
            result = ascii_fallback('wait\u2026')
            assert '\u2026' not in result

    def test_empty_string(self, monkeypatch):
        monkeypatch.setenv('PYTHONIOENCODING', 'utf-8')
        assert ascii_fallback('') == ''

    def test_no_emoji_text(self, monkeypatch):
        monkeypatch.setenv('PYTHONIOENCODING', 'utf-8')
        text = 'Plain ASCII text'
        assert ascii_fallback(text) == text
