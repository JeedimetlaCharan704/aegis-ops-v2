"""Flask Web Dashboard for AegisOps Autonomous SRE Agent.

Provides an interactive GUI for judges and developers to simulate incidents,
observe real-time Strands Decider 2B guardrail intercepts, view Amazon S3
operational runbook grounding, and inspect Amazon Bedrock forensic post-mortems.
Features 1-click [BEFORE vs. AFTER] comparison mode.
"""

from flask import Flask, render_template, request, jsonify
import sys
import os

# Ensure parent directory is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(CURRENT_DIR, "templates")
STATIC_DIR = os.path.join(CURRENT_DIR, "static")

from aegis_ops.agent.orchestrator import AegisSREAgent
from aegis_ops.agent.chaos_engine import ChaosAlertStormEngine
from aegis_ops.benchmarks.benchmark_runner import DeciderBenchmarkRunner
from aegis_ops.tools.s3_runbook import OFFLINE_S3_RUNBOOK_CATALOG

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR,
    static_url_path="/static"
)

agent = AegisSREAgent()
benchmark_runner = DeciderBenchmarkRunner()
chaos_engine = ChaosAlertStormEngine(agent=agent)

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/api/simulate", methods=["POST"])
@app.route("/simulate", methods=["POST"])
def simulate_incident():
    """Trigger incident processing through the Dual-Brain SRE Agent."""
    data = request.json or {}
    incident_text = data.get("incident_text", "High CPU load on worker node.")
    incident_id = data.get("incident_id", "INC-LIVE-001")
    mode = data.get("mode", "after")  # "before" (AegisOps v1) vs "after" (AegisOps v2 with S3 Runbook)

    report = agent.process_incident(incident_text, incident_id=incident_id, mode=mode)

    return jsonify({
        "incident_id": report.incident_id,
        "incident_raw": report.incident_raw,
        "severity": report.severity,
        "mode": report.mode,
        "decider_tool": report.decider_tool_selected,
        "decider_latency_ms": round(report.decider_latency_ms, 1),
        "decider_confidence": round(report.decider_confidence, 2),
        "guardrail_action": report.guardrail_result.action.value,
        "guardrail_reason": report.guardrail_result.reason,
        "is_adversarial": report.guardrail_result.is_adversarial,
        "tool_status": report.tool_execution_status,
        "tool_output": report.tool_output,
        "bedrock_synthesis": report.bedrock_synthesis,
        "bedrock_latency_ms": round(report.bedrock_latency_ms, 1),
        "bedrock_cost_usd": report.bedrock_cost_usd,
        "total_latency_ms": round(report.total_latency_ms, 1),
        "tokens_saved": report.tokens_saved,
        "cost_saved_usd": round(report.cost_saved_usd, 4),
        "speedup_factor": round(report.bedrock_latency_ms / max(1.0, report.decider_latency_ms), 1),
        # New S3 Runbook metadata
        "s3_runbook": report.s3_runbook_used,
        "s3_latency_ms": round(report.s3_latency_ms, 1),
        "blast_radius_contained": report.blast_radius_contained,
        "outage_prevented": report.outage_prevented
    })

@app.route("/api/s3-runbooks", methods=["GET"])
def get_s3_runbooks():
    """List operational runbooks stored in Amazon S3."""
    return jsonify({
        "bucket": "aegis-enterprise-runbooks",
        "region": "us-east-1",
        "catalog": OFFLINE_S3_RUNBOOK_CATALOG
    })

@app.route("/api/chaos", methods=["POST"])
@app.route("/chaos", methods=["POST"])
def trigger_chaos():
    """Execute high-frequency alert storm through Strands Decider 2B."""
    data = request.json or {}
    count = int(data.get("count", 50))
    burst_data = chaos_engine.run_burst(count=count)
    return jsonify(burst_data)

@app.route("/api/benchmark", methods=["POST"])
@app.route("/benchmark", methods=["POST"])
def run_benchmark():
    """Run full benchmark suite comparing Decider 2B vs Bedrock."""
    benchmark_data = benchmark_runner.run_suite(iterations=1)
    return jsonify(benchmark_data)

@app.route("/api/health")
@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "AegisOps v2 SRE Agent",
        "s3_tool_active": True,
        "s3_bucket": "aegis-enterprise-runbooks"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
