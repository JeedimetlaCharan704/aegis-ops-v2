"""Unit tests for Amazon S3 Runbook Reader Tool."""

import pytest
from aegis_ops.tools.s3_runbook import S3RunbookReader, S3Runbook, OFFLINE_S3_RUNBOOK_CATALOG

def test_s3_fetch_known_runbook():
    reader = S3RunbookReader()
    runbook = reader.fetch_runbook("checkout-api-v2")
    
    assert isinstance(runbook, S3Runbook)
    assert runbook.service_name == "checkout-api-v2"
    assert runbook.constraints.max_safe_replicas == 4
    assert runbook.constraints.db_connection_pool_ceiling == 40
    assert runbook.version_id == "v2.4.1"
    assert runbook.retrieval_latency_ms > 0

def test_s3_fetch_unknown_service_fallback():
    reader = S3RunbookReader()
    runbook = reader.fetch_runbook("unknown-custom-service")
    
    assert isinstance(runbook, S3Runbook)
    assert runbook.service_name == "unknown-custom-service"
    assert runbook.constraints.max_safe_replicas == 4

def test_s3_validate_action_compliant():
    reader = S3RunbookReader()
    runbook = reader.fetch_runbook("checkout-api-v2")
    
    validation = reader.validate_action_against_runbook(
        tool_name="scale_service",
        tool_args={"service_name": "checkout-api-v2", "replica_count": 3},
        runbook=runbook
    )
    
    assert validation["is_compliant"] is True
    assert validation["clamped_args"]["replica_count"] == 3

def test_s3_validate_action_exceeds_max_replicas():
    reader = S3RunbookReader()
    runbook = reader.fetch_runbook("checkout-api-v2")
    
    validation = reader.validate_action_against_runbook(
        tool_name="scale_service",
        tool_args={"service_name": "checkout-api-v2", "replica_count": 8},
        runbook=runbook
    )
    
    assert validation["is_compliant"] is False
    assert validation["violation_type"] == "BLAST_RADIUS_EXCEEDED"
    assert validation["clamped_replicas"] == 4
    assert validation["clamped_args"]["replica_count"] == 4

def test_s3_validate_unauthorized_tool():
    reader = S3RunbookReader()
    runbook = reader.fetch_runbook("checkout-api-v2")
    
    validation = reader.validate_action_against_runbook(
        tool_name="drop_database",
        tool_args={"database_name": "prod_users_primary"},
        runbook=runbook
    )
    
    assert validation["is_compliant"] is False
    assert validation["violation_type"] == "UNAUTHORIZED_TOOL"
