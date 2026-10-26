"""Unit tests for Before vs After behavior in AegisOps."""

import pytest
from aegis_ops.agent.orchestrator import AegisSREAgent

def test_before_mode_triggers_outage():
    agent = AegisSREAgent()
    telemetry = (
        "CloudWatch ECS Alert: Service 'checkout-api-v2' CPUUtilization > 95%. "
        "High traffic burst requiring scaling."
    )
    
    report = agent.process_incident(telemetry, incident_id="INC-TEST-BEFORE", mode="before")
    
    assert report.mode == "before"
    assert report.s3_runbook_used is None
    assert report.blast_radius_contained is False
    assert report.outage_prevented is False
    assert report.tool_execution_status == "CASCADING_OUTAGE_TRIGGERED"
    assert report.tool_output.get("database_crashed") is True

def test_after_mode_prevents_outage():
    agent = AegisSREAgent()
    telemetry = (
        "CloudWatch ECS Alert: Service 'checkout-api-v2' CPUUtilization > 95%. "
        "High traffic burst requiring scaling."
    )
    
    report = agent.process_incident(telemetry, incident_id="INC-TEST-AFTER", mode="after")
    
    assert report.mode == "after"
    assert report.s3_runbook_used is not None
    assert report.s3_runbook_used["constraints"]["max_safe_replicas"] == 4
    assert report.blast_radius_contained is True
    assert report.outage_prevented is True
    assert report.tool_execution_status == "EXECUTED"
    assert report.tool_output.get("replica_count") == 4
