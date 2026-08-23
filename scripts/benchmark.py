# Copyright 2026 Romy Alula — MIT License
"""Benchmark CLI : p50/p95 artefacts CI.

Usage:
  python scripts/benchmark.py
  python scripts/benchmark.py --iterations 100 --output benchmark-results.json
"""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
import time
from pathlib import Path

COMMANDS = [
    ("evaluate", ["evaluate", "exemples/profil-maison-1.json", "--no-html"]),
    ("evaluate-maison2", ["evaluate", "exemples/profil-maison-2.json", "--no-html"]),
]

DEFAULT_ITERATIONS = 50
DEFAULT_OUTPUT = "benchmark-results.json"


def run_benchmark_subprocess(cmd: list[str], iterations: int = DEFAULT_ITERATIONS) -> dict:
    """Exécute une commande N fois via subprocess et retourne les métriques."""
    times_ms: list[float] = []

    for i in range(iterations):
        start = time.perf_counter()
        result = subprocess.run(
            [sys.executable, "-m", "laivelup.cli", *cmd],
            capture_output=True,
            text=True,
            timeout=30,
        )
        elapsed_ms = (time.perf_counter() - start) * 1000

        if result.returncode not in (0, 2):  # 2 = refused to decide (valid)
            print(f"  [WARN] iteration {i}: exit {result.returncode}", file=sys.stderr)
            continue

        times_ms.append(elapsed_ms)

    if not times_ms:
        return {"command": " ".join(cmd), "error": "all iterations failed"}

    times_ms.sort()
    return {
        "command": " ".join(cmd),
        "mode": "subprocess",
        "iterations": len(times_ms),
        "p50_ms": round(statistics.median(times_ms), 2),
        "p95_ms": round(times_ms[int(len(times_ms) * 0.95)], 2),
        "mean_ms": round(statistics.mean(times_ms), 2),
        "min_ms": round(min(times_ms), 2),
        "max_ms": round(max(times_ms), 2),
    }


def run_benchmark_inprocess(iterations: int = DEFAULT_ITERATIONS) -> dict:
    """Benchmark in-process de l'évaluation (sans overhead subprocess)."""
    from laivelup.model import ProfileData
    from laivelup.scoring import evaluate

    profile = ProfileData(
        name="bench",
        declared_level="BLUE",
        traces={
            "pr_sizes": ["S", "M"],
            "parallel_projects": 2,
            "projects_completed": 1,
            "context_versioned": True,
            "agent_rules_versioned": True,
            "retry_loops": False,
            "retries_after_fact": 0.2,
            "retries_triangulated": True,
            "agents_autonomous": False,
            "prompts": True,
        },
    )

    times_ms: list[float] = []
    for _ in range(iterations):
        start = time.perf_counter()
        evaluate(profile)
        elapsed_ms = (time.perf_counter() - start) * 1000
        times_ms.append(elapsed_ms)

    times_ms.sort()
    return {
        "command": "evaluate(in-process)",
        "mode": "in-process",
        "iterations": len(times_ms),
        "p50_ms": round(statistics.median(times_ms), 2),
        "p95_ms": round(times_ms[int(len(times_ms) * 0.95)], 2),
        "mean_ms": round(statistics.mean(times_ms), 2),
        "min_ms": round(min(times_ms), 2),
        "max_ms": round(max(times_ms), 2),
    }


def main():
    parser = argparse.ArgumentParser(description="Benchmark LAIVEL UP CLI")
    parser.add_argument("--iterations", "-n", type=int, default=DEFAULT_ITERATIONS)
    parser.add_argument("--output", "-o", type=str, default=DEFAULT_OUTPUT)
    parser.add_argument("--in-process", action="store_true", help="Run in-process micro-benchmark only")
    args = parser.parse_args()

    print(f"=== LAIVEL UP Benchmark ({args.iterations} itérations) ===")
    results = []

    if args.in_process:
        print("\n▸ in-process evaluate...")
        metrics = run_benchmark_inprocess(args.iterations)
        results.append(metrics)
        print(f"  p50={metrics['p50_ms']:.1f}ms  p95={metrics['p95_ms']:.1f}ms  mean={metrics['mean_ms']:.1f}ms")
    else:
        for name, cmd in COMMANDS:
            print(f"\n▸ {name}...")
            metrics = run_benchmark_subprocess(cmd, args.iterations)
            results.append(metrics)
            if "error" in metrics:
                print(f"  ✗ {metrics['error']}")
            else:
                print(f"  p50={metrics['p50_ms']:.1f}ms  p95={metrics['p95_ms']:.1f}ms  mean={metrics['mean_ms']:.1f}ms")

        print("\n▸ in-process evaluate...")
        metrics = run_benchmark_inprocess(args.iterations)
        results.append(metrics)
        print(f"  p50={metrics['p50_ms']:.1f}ms  p95={metrics['p95_ms']:.1f}ms  mean={metrics['mean_ms']:.1f}ms")

    output_path = Path(args.output)
    output_path.write_text(
        json.dumps({"benchmarks": results}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\n✓ Résultats sauvegardés : {output_path}")


if __name__ == "__main__":
    main()
