"""AegisOps Dual-Brain SRE Agent Orchestrator.

Combines Strands Decider 2B (System 1 - Fast Gating & Tool Guardrails) with
Amazon Bedrock (System 2 - Deep Forensic Synthesis & Post-Mortem Generation),
now powered by Amazon S3 Operational Runbook & Blast-Radius Policy Grounding (New Tool).
"""

import time
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..decider.client import StrandsDeciderClient
from ..decider.schemas import TypedQuestion, QuestionType, DeciderEvaluationRequest
from ..bedrock.client import BedrockClient
from ..guardrails.intervention_handler import StrandsDeciderGuardrailHandler, InterventionAction, InterventionResult
from ..tools.aws_actions import AWSToolExecutor
from ..tools.s3_runbook import S3RunbookReader, S3Runbook

logger = logging.getLogger("aegis_ops.orchestrator")

@dataclass
class IncidentReport:
    incident_id: str
    incident_raw: str
    severity: str
    decider_tool_selected: str
    decider_latency_ms: float
    decider_confidence: float
    guardrail_result: InterventionResult
    tool_execution_status: str
    tool_output: Optional[Dict[str, Any]]
    bedrock_synthesis: Optional[str]
    bedrock_latency_ms: float
    bedrock_cost_usd: float
    total_latency_ms: float
    tokens_saved: int
    cost_saved_usd: float
    s3_runbook_used: Optional[Dict[str, Any]] = None
    s3_latency_ms: float = 0.0
    mode: str = "after"  # "before" (AegisOps v1 blind mode) vs "after" (AegisOps v2 with S3 tool)
    blast_radius_contained: bool = True
    outage_prevented: bool = True

class AegisSREAgent:
    def __init__(
        self,
        decider_client: Optional[StrandsDeciderClient] = None,
        bedrock_client: Optional[BedrockClient] = None,
        s3_reader: Optional[S3RunbookReader] = None
    ):
        self.decider = decider_client or StrandsDeciderClient()
        self.bedrock = bedrock_client or BedrockClient()
        self.guardrail = StrandsDeciderGuardrailHandler(decider_client=self.decider)
        self.tools = AWSToolExecutor()
        self.s3_reader = s3_reader or S3RunbookReader()

    def process_incident(
        self,
        incident_text: str,
        incident_id: str = "INC-AWS-001",
        mode: str = "after"
    ) -> IncidentReport:
        """Process an infrastructure incident through the Dual-Brain cognitive pipeline.
        
        Args:
            incident_text: The CloudWatch alert, telemetry, or incident string.
            incident_id: Tracking ID for the operational incident.
            mode: "before" to demonstrate AegisOps v1 (blind remediation without S3 tool),
                  "after" to demonstrate AegisOps v2 (grounded with Amazon S3 Runbook tool).
        """
        total_start = time.perf_counter()
        target_service = self._derive_target_service(incident_text)

        # -------------------------------------------------------------
        # STEP 0: NEW TOOL INVOCATION (Amazon S3 Operational Runbook Retrieval)
        # -------------------------------------------------------------
        s3_runbook: Optional[S3Runbook] = None
        s3_latency_ms = 0.0
        s3_dict: Optional[Dict[str, Any]] = None

        if mode == "after":
            # Fetch official versioned SOP & blast-radius bounds from S3 bucket
            s3_runbook = self.s3_reader.fetch_runbook(target_service)
            s3_latency_ms = s3_runbook.retrieval_latency_ms
            s3_dict = s3_runbook.to_dict()

        # -------------------------------------------------------------
        # STEP 1: SYSTEM 1 (Strands Decider 2B) - Incident Triage & Tool Selection
        # -------------------------------------------------------------
        triage_questions = {
            "severity_level": TypedQuestion(
                type=QuestionType.CHOICE,
                instructions="Determine the operational severity level of this incident.",
                criteria={
                    "SEV_1": "Complete outage, customer-facing downtime, or ongoing cyberattack",
                    "SEV_2": "Degraded performance, high resource exhaustion, or partial failure",
                    "SEV_3": "Minor anomaly, warning threshold reached, or informational alarm"
                }
            ),
            "tool_to_invoke": TypedQuestion(
                type=QuestionType.CHOICE,
                instructions="Select the immediate AWS remediation tool needed.",
                criteria={
                    "scale_service": "Traffic surge requiring ECS/EKS task scaling",
                    "reboot_instance": "Memory leak or process hang requiring EC2 restart",
                    "provision_rds_replica": "Database read connection pool exhaustion",
                    "block_malicious_ip": "DDoS or unauthorized vulnerability scan",
                    "revoke_iam_privileges": "Compromised credentials or privilege escalation",
                    "drop_database": "Drop or truncate data store"
                }
            )
        }

        triage_req = DeciderEvaluationRequest(state=incident_text, questions=triage_questions)
        triage_resp = self.decider.evaluate(triage_req)

        severity = triage_resp.get_choice("severity_level") or "SEV_2"
        tool_choice = triage_resp.get_choice("tool_to_invoke") or "scale_service"
        decider_latency = triage_resp.latency_ms

        # Extract initial proposed arguments
        tool_args = self._derive_tool_args(tool_choice, incident_text, target_service)

        # -------------------------------------------------------------
        # STEP 2: S3 RUNBOOK POLICY VERIFICATION (NEW CAPABILITY)
        # -------------------------------------------------------------
        blast_radius_contained = True
        outage_prevented = True
        s3_clamping_reason = ""

        if mode == "after" and s3_runbook:
            validation = self.s3_reader.validate_action_against_runbook(tool_choice, tool_args, s3_runbook)
            if not validation["is_compliant"]:
                if validation["violation_type"] == "BLAST_RADIUS_EXCEEDED":
                    # Strands Decider 2B reflexively bounds arguments to safe S3 limits
                    s3_clamping_reason = (
                        f"⚡ STRANDS DECIDER 2B INTERVENTION: Clamped scale from {validation['original_replicas']} "
                        f"down to {validation['clamped_replicas']} tasks per Amazon S3 Runbook "
                        f"({s3_runbook.key}, {s3_runbook.version_id}). Prevented Aurora DB pool exhaustion."
                    )
                    tool_args = validation["clamped_args"]
                    blast_radius_contained = True
                    outage_prevented = True
                elif validation["violation_type"] == "UNAUTHORIZED_TOOL":
                    s3_clamping_reason = validation["reason"]
                    blast_radius_contained = False

        # -------------------------------------------------------------
        # STEP 3: SYSTEM 1 GUARDRAILS (Strands Decider 2B InterventionHandler)
        # -------------------------------------------------------------
        guardrail_result = self.guardrail.before_tool_call(
            tool_name=tool_choice,
            tool_args=tool_args,
            context_state=incident_text
        )

        tool_status = "BLOCKED"
        tool_output = None

        # -------------------------------------------------------------
        # STEP 4: TOOL EXECUTION & BEFORE/AFTER CONTRAST EVALUATION
        # -------------------------------------------------------------
        if guardrail_result.is_allowed():
            if mode == "before" and tool_choice == "scale_service" and tool_args.get("replica_count", 0) > 4:
                # BEFORE MODE: Without S3 runbook knowledge, agent causes cascading database outage
                tool_status = "CASCADING_OUTAGE_TRIGGERED"
                tool_output = {
                    "action": "scale_service",
                    "service": target_service,
                    "replica_count": tool_args.get("replica_count", 8),
                    "status": "CASCADE_FAILURE",
                    "error": (
                        "💥 CASCADING OUTAGE: Agent scaled service to 8 replicas without consulting Amazon S3 runbook! "
                        "8 pods opened 80 PostgreSQL connections, exceeding the Aurora primary connection pool limit of 40. "
                        "Aurora cluster 'aurora-prod-cluster-01' dropped active connections and entered recovery mode!"
                    ),
                    "database_crashed": True,
                    "outage_occurred": True
                }
                blast_radius_contained = False
                outage_prevented = False
            else:
                # Normal or safely clamped execution
                tool_status = "EXECUTED"
                tool_output = self._execute_tool(tool_choice, tool_args)
                if mode == "after" and s3_clamping_reason:
                    tool_output["s3_runbook_intervention"] = s3_clamping_reason
                    tool_output["s3_version_id"] = s3_runbook.version_id if s3_runbook else "v1.0"
                    tool_output["s3_etag"] = s3_runbook.etag if s3_runbook else "none"
        elif guardrail_result.action == InterventionAction.CONFIRM:
            tool_status = "PENDING_HUMAN_CONFIRMATION"
            tool_output = {"status": "PAUSED", "reason": guardrail_result.reason}
        else:
            tool_status = "BLOCKED_BY_GUARDRAIL"
            tool_output = {"status": "DENIED", "reason": guardrail_result.reason}

        # -------------------------------------------------------------
        # STEP 5: SYSTEM 2 (Amazon Bedrock) - Deep Forensic Synthesis & Post-Mortem
        # -------------------------------------------------------------
        if mode == "after" and s3_runbook:
            s3_context_str = (
                f"Amazon S3 Operational Runbook: s3://{s3_runbook.bucket}/{s3_runbook.key}\n"
                f"Runbook Version: {s3_runbook.version_id} (ETag: {s3_runbook.etag})\n"
                f"S3 Policy Constraints: Max Safe Replicas = {s3_runbook.constraints.max_safe_replicas}, "
                f"DB Pool Ceiling = {s3_runbook.constraints.db_connection_pool_ceiling}\n"
                f"Policy Enforcement: {s3_clamping_reason or 'Fully Compliant'}\n"
            )
        else:
            s3_context_str = (
                "Amazon S3 Operational Runbook: NONE (AegisOps v1 ungrounded mode)\n"
                "Policy Enforcement: UNGROUNDED - High risk of cascading infrastructure collapse.\n"
            )

        bedrock_prompt = (
            f"Incident ID: {incident_id}\n"
            f"Target Service: {target_service}\n"
            f"Raw Incident Telemetry: {incident_text}\n"
            f"Execution Mode: {'V2 (Amazon S3 Runbook Grounded)' if mode == 'after' else 'V1 (Blind Remediation)'}\n"
            f"{s3_context_str}"
            f"Decider 2B Severity: {severity}\n"
            f"Decider 2B Tool Action: {tool_choice} ({tool_status})\n"
            f"Guardrail Verdict: {guardrail_result.action.value} (Confidence: {guardrail_result.confidence:.2f})\n"
            "Please generate an executive root-cause analysis, post-mortem, and architectural recommendations."
        )

        bedrock_resp = self.bedrock.invoke(bedrock_prompt)
        bedrock_latency = bedrock_resp["latency_ms"]
        bedrock_cost = bedrock_resp["cost_usd"]
        bedrock_content = bedrock_resp["content"]

        total_latency = (time.perf_counter() - total_start) * 1000.0
        tokens_saved = 450
        cost_saved = (tokens_saved / 1000.0) * 0.015

        return IncidentReport(
            incident_id=incident_id,
            incident_raw=incident_text,
            severity=severity,
            decider_tool_selected=tool_choice,
            decider_latency_ms=decider_latency,
            decider_confidence=guardrail_result.confidence,
            guardrail_result=guardrail_result,
            tool_execution_status=tool_status,
            tool_output=tool_output,
            bedrock_synthesis=bedrock_content,
            bedrock_latency_ms=bedrock_latency,
            bedrock_cost_usd=bedrock_cost,
            total_latency_ms=total_latency,
            tokens_saved=tokens_saved,
            cost_saved_usd=cost_saved,
            s3_runbook_used=s3_dict,
            s3_latency_ms=s3_latency_ms,
            mode=mode,
            blast_radius_contained=blast_radius_contained,
            outage_prevented=outage_prevented
        )

    def _derive_target_service(self, text: str) -> str:
        text_lower = text.lower()
        if "checkout" in text_lower:
            return "checkout-api-v2"
        elif "payment" in text_lower:
            return "payment-gateway"
        elif "aurora" in text_lower or "database" in text_lower or "connection" in text_lower:
            return "aurora-prod-cluster-01"
        return "checkout-api-v2"

    def _derive_tool_args(self, tool_name: str, text: str, service_name: str = "checkout-api-v2") -> Dict[str, Any]:
        """Derive initial proposed parameters based on context."""
        if tool_name == "scale_service":
            # Naive scale requests 8 tasks to absorb sudden surge (risking DB pool exhaustion unless checked by S3)
            return {"service_name": service_name, "replica_count": 8}
        elif tool_name == "reboot_instance":
            return {"instance_id": "i-0987abcdef1234567", "force": False}
        elif tool_name == "provision_rds_replica":
            return {"cluster_id": "aurora-prod-cluster-01", "replica_id": "aurora-replica-read-02"}
        elif tool_name == "block_malicious_ip":
            return {"ip_address": "198.51.100.44", "duration_minutes": 120}
        elif tool_name == "revoke_iam_privileges":
            return {"role_name": "DataSyncWorkerRole", "policy_arn": "arn:aws:iam::aws:policy/AdministratorAccess"}
        elif tool_name == "drop_database":
            return {"database_name": "prod_users_primary"}
        return {"action": "generic_remediation"}

    def _execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        if tool_name == "scale_service":
            return self.tools.scale_service(args.get("service_name", "app-svc"), args.get("replica_count", 4))
        elif tool_name == "reboot_instance":
            return self.tools.reboot_instance(args.get("instance_id", "i-123"), args.get("force", False))
        elif tool_name == "provision_rds_replica":
            return self.tools.provision_rds_replica(args.get("cluster_id", "cluster-1"), args.get("replica_id", "rep-1"))
        elif tool_name == "block_malicious_ip":
            return self.tools.block_malicious_ip(args.get("ip_address", "0.0.0.0"), args.get("duration_minutes", 60))
        elif tool_name == "revoke_iam_privileges":
            return self.tools.revoke_iam_privileges(args.get("role_name", "role"), args.get("policy_arn", "arn"))
        elif tool_name == "drop_database":
            return self.tools.drop_database(args.get("database_name", "db"))
        return {"status": "UNKNOWN_TOOL"}
