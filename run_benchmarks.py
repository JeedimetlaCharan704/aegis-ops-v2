"""Standalone Benchmark Runner for AegisOps.

Executes quantitative evaluations comparing Strands Decider 2B vs Amazon Bedrock
across latency, throughput, token savings, and cost reduction.
"""

import sys
import json

# Ensure UTF-8 output encoding on Windows consoles
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from aegis_ops.benchmarks.benchmark_runner import DeciderBenchmarkRunner

def run():
    print("=" * 80)
    print("  STRANDS DECIDER 2B VS. AMAZON BEDROCK BENCHMARK SUITE")
    print("=" * 80)
    print("Executing 5 decision scenarios...\n")

    runner = DeciderBenchmarkRunner()
    results = runner.run_suite(iterations=1)

    print(f"{'Scenario Name':<35} | {'Pattern':<15} | {'Decider (ms)':<12} | {'Bedrock (ms)':<12} | {'Speedup':<8}")
    print("-" * 90)

    for sc in results["scenarios"]:
        print(f"{sc['scenario_name']:<35} | {sc['pattern_type']:<15} | {sc['decider_latency_ms']:<12.1f} | {sc['bedrock_latency_ms']:<12.1f} | {sc['speedup_factor']:<8.1f}x")

    print("-" * 90)
    summary = results["summary"]
    print(f"\n[SUMMARY METRICS]")
    print(f"  * Average Decider 2B Latency:   {summary['overall_decider_avg_latency_ms']} ms")
    print(f"  * Average Bedrock Latency:      {summary['overall_bedrock_avg_latency_ms']} ms")
    print(f"  * Average Latency Speedup:      {summary['overall_speedup_factor']}")
    print(f"  * Fast-Path Token Cost:         $0.0000 (100% elimination of LLM token spend on decision gates)")
    print(f"  * Projected Monthly Savings:    ${summary['projected_monthly_savings_usd']:,.2f} USD (at 10k decisions/day)")
    print("=" * 80)

    # Save to file
    with open("benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print("Saved detailed report to: benchmark_results.json\n")

if __name__ == "__main__":
    run()
