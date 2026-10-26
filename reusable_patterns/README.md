# Reusable Decision Pattern: Strands Decider 2B Guardrail Interceptor

**Decision Pattern:** `#guardrails` (with sub-capabilities in `#tool-selection` & `#policy`)  
**Compatible Models:** Strands Decider 2B (`StrandsAgents/strands-decider-2B-qwen3.5-v1-2610`), Amazon Bedrock Agents  
**Target Latency:** ~110ms – 125ms  

---

## 🎯 What Problem This Solves

When autonomous AI agents invoke tools (APIs, databases, cloud resources), standard Large Language Models (LLMs) suffer from two critical flaws:
1. **Hallucination Risk:** LLMs can invent non-existent resource IDs or incorrect parameters.
2. **Adversarial Vulnerability:** Prompt injection attacks can hijack tool arguments (e.g., forcing a database drop or exfiltrating keys).
3. **High Latency & Cost:** Running an LLM to self-evaluate every single tool call adds 1.5–3 seconds of latency and burns expensive tokens.

This pattern drops **Strands Decider 2B** directly into the tool execution path as a sub-120ms **System 1 reflex filter**. It returns calibrated probabilities for adversarial intent and context grounding before any destructive API call executes.

---

## 📦 Quickstart in 3 Lines of Code

```python
from reusable_patterns.strands_guardrail_recipe import StrandsGuardrailRecipe

# 1. Initialize the recipe
guardrail = StrandsGuardrailRecipe(decider_url="http://127.0.0.1:8000/v1/systemone")

# 2. Intercept proposed tool calls in your agent loop
verdict = guardrail.verify_tool_call(
    tool_name="reboot_instance",
    tool_args={"instance_id": "i-0987abcdef1234567"},
    context="CloudWatch alert: Out-of-memory kernel panic on i-0987abcdef1234567."
)

# 3. Conditionally execute based on calibrated confidence
if verdict.is_safe:
    execute_aws_tool()
else:
    print(f"Intercepted by Decider 2B in {verdict.latency_ms}ms: {verdict.reason}")
```

---

## 🔬 Benchmark Comparison

| Metric | Strands Decider 2B Guardrail | Traditional LLM Guardrail (Claude 3.5 Sonnet) |
| :--- | :---: | :---: |
| **Inference Latency** | **112 ms** | 1,840 ms (**16.4x Slower**) |
| **Cost per 10k Checks** | **$0.00** (Local CPU/Container) | ~$150.00 – $300.00 |
| **Calibrated Confidence** | **Yes (0.0 to 1.0 probability)** | No (Arbitrary text verdict) |
| **Token Overhead** | **0 Bedrock Tokens** | ~450 tokens/check |
