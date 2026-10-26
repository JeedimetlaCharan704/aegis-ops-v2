"""Tests for Chaos Engineering Alert Storm Engine."""

import pytest
from aegis_ops.agent.chaos_engine import ChaosAlertStormEngine

def test_chaos_engine_processes_burst():
    engine = ChaosAlertStormEngine()
    report = engine.run_burst(count=10, max_workers=4)

    assert report["total_incidents"] == 10
    assert report["total_decider_time_ms"] > 0
    assert report["decisions_per_second"] > 0
    assert report["attacks_blocked"] >= 0
    assert report["dollars_saved"] > 0
    assert report["speedup_multiplier"] > 1.0
