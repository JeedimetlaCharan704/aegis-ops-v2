"""Tests for Benchmark Suite."""

import pytest
from aegis_ops.benchmarks.benchmark_runner import DeciderBenchmarkRunner

def test_benchmark_runner_executes_suite():
    runner = DeciderBenchmarkRunner()
    results = runner.run_suite(iterations=1)
    
    assert "summary" in results
    assert "scenarios" in results
    assert len(results["scenarios"]) == 5
    
    # Verify Decider latency is substantially faster than Bedrock
    for sc in results["scenarios"]:
        assert sc["decider_latency_ms"] < sc["bedrock_latency_ms"]
        assert sc["speedup_factor"] > 1.0
