# Copyright 2026 Romy Alula — MIT License
"""Tests scripts/generate_profile.py : gaps de couverture (coverage-90-closing-gaps.md).

Cible : _bucket_size (fonction pure), _detect_retries_after_fact (mock _git).
"""

from __future__ import annotations

from scripts.generate_profile import _bucket_size, _detect_retries_after_fact


class TestBucketSize:
    def test_small_change_is_s(self):
        assert _bucket_size(1) == 'S'
        assert _bucket_size(3) == 'S'

    def test_medium_change_is_m(self):
        assert _bucket_size(4) == 'M'
        assert _bucket_size(10) == 'M'

    def test_large_change_is_l(self):
        assert _bucket_size(11) == 'L'
        assert _bucket_size(30) == 'L'

    def test_xlarge_change_is_xl(self):
        assert _bucket_size(31) == 'XL'
        assert _bucket_size(500) == 'XL'


class TestDetectRetriesAfterFact:
    def test_no_log_returns_none_not_triangulated(self, monkeypatch, tmp_path):
        import scripts.generate_profile as gp

        monkeypatch.setattr(gp, '_git', lambda _repo, _args: '')
        ratio, triangulated = _detect_retries_after_fact(tmp_path, 'alice')
        assert ratio is None
        assert triangulated is False

    def test_fewer_than_5_commits_returns_none(self, monkeypatch, tmp_path):
        import scripts.generate_profile as gp

        log = '\n'.join([f'{"a" * 40} fix bug {i}' for i in range(3)])
        monkeypatch.setattr(gp, '_git', lambda _repo, _args: log)
        ratio, triangulated = _detect_retries_after_fact(tmp_path, 'alice')
        assert ratio is None
        assert triangulated is False

    def test_ratio_computed_from_fix_commits(self, monkeypatch, tmp_path):
        import scripts.generate_profile as gp

        commits = [f'{"a" * 40} fix issue' for _ in range(2)] + [
            f'{"b" * 40} add feature' for _ in range(8)
        ]
        log = '\n'.join(commits)
        monkeypatch.setattr(gp, '_git', lambda _repo, _args: log)
        ratio, triangulated = _detect_retries_after_fact(tmp_path, 'alice')
        assert triangulated is True
        assert ratio == 0.2  # 2 fix / 10 total
