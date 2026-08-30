# Copyright 2026 Romy Alula — MIT License
"""Tests for scripts/*.py modules (benchmark, ci_evaluate, demo, version_bump).

Target: bring script coverage from 0% to meaningful levels.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent
SCRIPTS = REPO / 'scripts'
SRC = REPO / 'src'


class TestBenchmarkScript:
    """Tests for scripts/benchmark.py"""

    def test_inprocess_benchmark_runs(self):
        """Test in-process benchmark path."""
        from scripts.benchmark import run_benchmark_inprocess

        result = run_benchmark_inprocess(iterations=2)
        assert result['mode'] == 'in-process'
        assert result['iterations'] == 2
        assert 'p50_ms' in result
        assert 'p95_ms' in result
        assert 'mean_ms' in result

    def test_subprocess_benchmark_returns_dict(self):
        """Test subprocess benchmark path with mocked iterations=0."""
        from scripts.benchmark import run_benchmark_subprocess

        # Use a simple command that exits quickly
        result = run_benchmark_subprocess(['--version'], iterations=1)
        # Should either succeed or fail gracefully
        assert isinstance(result, dict)
        assert 'command' in result

    def test_main_inprocess_flag(self, tmp_path):
        """Test main() with --in-process flag."""
        output_file = tmp_path / 'bench.json'

        # Run the script via subprocess with --in-process
        env = {**__import__('os').environ, 'PYTHONPATH': str(SRC), 'PYTHONIOENCODING': 'utf-8'}
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / 'benchmark.py'),
                '--in-process',
                '--iterations',
                '1',
                '--output',
                str(output_file),
            ],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            env=env,
            cwd=str(REPO),
        )
        assert result.returncode == 0
        assert output_file.exists()
        data = json.loads(output_file.read_text(encoding='utf-8'))
        assert 'benchmarks' in data
        assert len(data['benchmarks']) == 1
        assert data['benchmarks'][0]['mode'] == 'in-process'


class TestCiEvaluateScript:
    """Tests for scripts/ci_evaluate.py"""

    def test_main_exits_1_on_no_user(self):
        """Test that --user is required."""
        env = {**__import__('os').environ, 'PYTHONPATH': str(SRC)}
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / 'ci_evaluate.py')],
            capture_output=True,
            text=True,
            env=env,
            cwd=str(REPO),
        )
        assert result.returncode == 2  # argparse error

    def test_generate_profile_integration(self, tmp_path):
        """Test the generate_profile import path works."""
        from scripts.generate_profile import generate_profile

        # Create a minimal repo structure
        (tmp_path / '.git').mkdir()
        profile = generate_profile(tmp_path, 'testuser', verbose=False)
        assert 'name' in profile
        assert 'traces' in profile

    def test_ci_evaluate_md_output(self, tmp_path, monkeypatch):
        """Test ci_evaluate.py --format md (imported main function)."""
        from scripts.ci_evaluate import main as ci_main

        out_file = tmp_path / 'verdict.md'
        monkeypatch.setattr(
            'sys.argv',
            [
                'ci_evaluate.py',
                '--user',
                'testuser',
                '--repo',
                str(REPO),
                '--out',
                str(out_file),
                '--format',
                'md',
            ],
        )
        result = ci_main()
        assert result in (0, 2)
        assert out_file.exists()
        content = out_file.read_text(encoding='utf-8')
        assert len(content) > 0

    def test_ci_evaluate_json_output(self, tmp_path, monkeypatch):
        """Test ci_evaluate.py --format json (imported main function)."""
        from scripts.ci_evaluate import main as ci_main

        out_file = tmp_path / 'verdict.json'
        monkeypatch.setattr(
            'sys.argv',
            [
                'ci_evaluate.py',
                '--user',
                'testuser',
                '--repo',
                str(REPO),
                '--out',
                str(out_file),
                '--format',
                'json',
            ],
        )
        result = ci_main()
        assert result in (0, 2)
        assert out_file.exists()
        data = json.loads(out_file.read_text(encoding='utf-8'))
        assert 'level' in data
        assert 'axes' in data

    def test_ci_evaluate_undecided(self, tmp_path, monkeypatch):
        """Test ci_evaluate.py with minimal profile returns exit 2."""
        from scripts.ci_evaluate import main as ci_main

        out_file = tmp_path / 'verdict.md'
        # Use tmp_path as repo (no git data → minimal profile)
        monkeypatch.setattr(
            'sys.argv',
            [
                'ci_evaluate.py',
                '--user',
                'testuser',
                '--repo',
                str(tmp_path),
                '--out',
                str(out_file),
                '--format',
                'md',
            ],
        )
        result = ci_main()
        assert result == 2  # undecided
        assert out_file.exists()


class TestDemoScript:
    """Tests for scripts/demo.py"""

    def test_main_runs_without_errors(self, monkeypatch):
        """Test demo main() runs without crashing (mocked subprocess)."""

        # Mock subprocess.run to avoid actually running commands
        def mock_run(cmd, *_args, **_kwargs):
            # Allow the first few calls to succeed silently
            return subprocess.CompletedProcess(cmd, 0, '', '')

        monkeypatch.setattr(subprocess, 'run', mock_run)

        # Run the demo script
        sys.path.insert(0, str(SCRIPTS))
        import scripts.demo as demo_module

        # Just test it doesn't crash
        demo_module.main()

    def test_run_helper(self, monkeypatch):
        """Test the _run helper function."""
        import scripts.demo as demo_module

        calls = []

        def mock_run(cmd, **_kwargs):
            calls.append(cmd)
            return subprocess.CompletedProcess(cmd, 0, '', '')

        monkeypatch.setattr(subprocess, 'run', mock_run)
        monkeypatch.setattr('time.sleep', lambda _: None)

        demo_module._run('echo test', 'Test Label', 'Test comment', pause=0)
        assert len(calls) == 1
        assert calls[0] == ['echo', 'test']


class TestVersionBumpScript:
    """Tests for scripts/version_bump.py"""

    def test_read_version(self, tmp_path, monkeypatch):
        """Test _read_version parses pyproject.toml correctly."""
        import scripts.version_bump as vb

        # Create a temporary pyproject.toml
        test_pyproject = tmp_path / 'pyproject.toml'
        test_pyproject.write_text('[project]\nversion = "1.2.3"\n', encoding='utf-8')

        monkeypatch.setattr(vb, 'PYPROJECT', test_pyproject)

        major, minor, patch = vb._read_version()
        assert major == 1
        assert minor == 2
        assert patch == 3

    def test_write_version(self, tmp_path, monkeypatch):
        """Test _write_version updates both files."""
        import scripts.version_bump as vb

        test_pyproject = tmp_path / 'pyproject.toml'
        test_pyproject.write_text('[project]\nversion = "1.2.3"\n', encoding='utf-8')

        test_init = tmp_path / '__init__.py'
        test_init.write_text('__version__ = "1.2.3"\n', encoding='utf-8')

        monkeypatch.setattr(vb, 'PYPROJECT', test_pyproject)
        monkeypatch.setattr(vb, 'INIT', test_init)

        vb._write_version(2, 0, 0)

        assert 'version = "2.0.0"' in test_pyproject.read_text(encoding='utf-8')
        assert '__version__ = "2.0.0"' in test_init.read_text(encoding='utf-8')

    def test_main_invalid_args(self):
        """Test main() with invalid args exits with error."""
        env = {**__import__('os').environ, 'PYTHONPATH': str(SRC)}
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / 'version_bump.py'), 'invalid'],
            capture_output=True,
            text=True,
            env=env,
            cwd=str(REPO),
        )
        assert result.returncode == 1
        assert 'Usage:' in result.stdout or 'Usage:' in result.stderr

    def test_main_patch_bump(self, tmp_path, monkeypatch):
        """Test patch bump logic."""
        import scripts.version_bump as vb

        test_pyproject = tmp_path / 'pyproject.toml'
        test_pyproject.write_text('[project]\nversion = "1.2.3"\n', encoding='utf-8')

        test_init = tmp_path / '__init__.py'
        test_init.write_text('__version__ = "1.2.3"\n', encoding='utf-8')

        monkeypatch.setattr(vb, 'PYPROJECT', test_pyproject)
        monkeypatch.setattr(vb, 'INIT', test_init)
        monkeypatch.setattr(vb, '_git_commit_tag', lambda *_a, **_k: None)

        # Simulate sys.argv
        old_argv = sys.argv
        sys.argv = ['version_bump.py', 'patch']
        try:
            vb.main()
        except SystemExit:
            pass
        finally:
            sys.argv = old_argv

        assert 'version = "1.2.4"' in test_pyproject.read_text(encoding='utf-8')

    def test_main_minor_bump(self, tmp_path, monkeypatch):
        """Test minor bump logic."""
        import scripts.version_bump as vb

        test_pyproject = tmp_path / 'pyproject.toml'
        test_pyproject.write_text('[project]\nversion = "1.2.3"\n', encoding='utf-8')

        test_init = tmp_path / '__init__.py'
        test_init.write_text('__version__ = "1.2.3"\n', encoding='utf-8')

        monkeypatch.setattr(vb, 'PYPROJECT', test_pyproject)
        monkeypatch.setattr(vb, 'INIT', test_init)
        monkeypatch.setattr(vb, '_git_commit_tag', lambda *_a, **_k: None)

        old_argv = sys.argv
        sys.argv = ['version_bump.py', 'minor']
        try:
            vb.main()
        except SystemExit:
            pass
        finally:
            sys.argv = old_argv

        assert 'version = "1.3.0"' in test_pyproject.read_text(encoding='utf-8')

    def test_main_major_bump(self, tmp_path, monkeypatch):
        """Test major bump logic."""
        import scripts.version_bump as vb

        test_pyproject = tmp_path / 'pyproject.toml'
        test_pyproject.write_text('[project]\nversion = "1.2.3"\n', encoding='utf-8')

        test_init = tmp_path / '__init__.py'
        test_init.write_text('__version__ = "1.2.3"\n', encoding='utf-8')

        monkeypatch.setattr(vb, 'PYPROJECT', test_pyproject)
        monkeypatch.setattr(vb, 'INIT', test_init)
        monkeypatch.setattr(vb, '_git_commit_tag', lambda *_a, **_k: None)

        old_argv = sys.argv
        sys.argv = ['version_bump.py', 'major']
        try:
            vb.main()
        except SystemExit:
            pass
        finally:
            sys.argv = old_argv

        assert 'version = "2.0.0"' in test_pyproject.read_text(encoding='utf-8')
