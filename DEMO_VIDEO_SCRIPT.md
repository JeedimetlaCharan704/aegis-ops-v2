# 2-Minute 35-Second Video Walkthrough Script & Storyboard
## AWS Weekend Challenge: "Give Your Agent a Tool"

**Project:** AegisOps v2 — Autonomous SRE Agent with Amazon S3 Runbook Grounding & Strands Decider 2B  
**Target Duration:** 2 minutes 35 seconds (Strictly under the 3-minute hackathon ceiling)  
**Presenter:** Charan Jeedimetla  
**Recommended Recording Tool:** OBS Studio, Loom, or Windows Game Bar (`Win + Alt + R`)  
**Live Dashboard URL:** [http://localhost:5000](http://localhost:5000) (or your deployed URL)

---

## 🎬 Second-by-Second Video Timeline

```
0:00 - 0:30 ─── Part 1: The Starting Agent & What It Could Already Do (30s)
0:30 - 0:55 ─── Part 2: The Capability Gap & The New Amazon S3 Tool (25s)
0:55 - 1:30 ─── Part 3: The BEFORE Demonstration (Blind Scaling & DB Outage) (35s)
1:30 - 2:05 ─── Part 4: The AFTER Demonstration (S3 Runbook Grounding & 43ms Clamp) (35s)
2:05 - 2:35 ─── Part 5: Reusable Pattern, Architecture & Closing (30s)
```

---

### 🎙️ Exact Voiceover & Visual Choreography

#### [0:00 – 0:30] Part 1: The Starting Agent & What It Could Already Do
* **Screen Display:** Open browser on the AegisOps v2 dashboard at full 1080p resolution. Hover cursor over the header badges (`#strands-decider-2b`, `#amazon-bedrock`).
* **Your Voiceover:**
  > *"Hi everyone, I’m Charan. In the previous hackathon, I built **AegisOps**: an autonomous Site Reliability Engineering agent combining AWS's **Strands Decider 2B** for sub-50ms reflex guardrails with **Amazon Bedrock** for deep generative post-mortems.*
  > 
  > *AegisOps could triage CloudWatch alarms, intercept prompt injections, and execute automated remediations like scaling ECS containers or rebooting EC2 instances."*

---

#### [0:30 – 0:55] Part 2: The Capability Gap & The New Amazon S3 Tool
* **Screen Display:** Move cursor to the new **"Amazon S3 Operational Runbook Vault"** card and highlight the **BEFORE vs. AFTER** mode selector.
* **Your Voiceover:**
  > *"However, AegisOps had one fatal blind spot: **The Agentic Blast-Radius Trap**.*
  > 
  > *Because it had no access to organizational operating knowledge or company runbooks, it used hardcoded heuristics. When an alert demanded emergency scaling, the agent would blindly guess replica counts without knowing upstream database connection limits.*
  > 
  > *For this weekend challenge, I gave AegisOps **one new tool it did not have before**: an **Amazon S3 Operational Runbook Reader** (`fetch_s3_incident_runbook`), which pulls versioned, cryptographically validated Standard Operating Procedures directly from an S3 bucket in 12 milliseconds."*

---

#### [0:55 – 1:30] Part 3: The BEFORE Demonstration (Without Amazon S3 Tool)
* **Screen Display:** 
  1. Click the red button: **"BEFORE (v1 Blind Mode)"**.
  2. The alert banner turns RED: *"⚠️ ACTIVE: AegisOps v1 (Blind Remediation — No Amazon S3 Tool)"*.
  3. Click **"Memory Surge (Checkout API)"** preset.
  4. Click **"⚡ RUN DUAL-BRAIN AGENT"**.
  5. The screen flashes red with a catastrophic outage banner: `💥 CASCADING OUTAGE TRIGGERED`.
* **Your Voiceover:**
  > *"Let's see what happened BEFORE this tool existed.*
  > 
  > *Here, `checkout-api-v2` experiences a major memory surge. Operating blindly without an S3 runbook, the agent tries to solve the spike by scaling to **8 replicas**.*
  > 
  > *Look at the result: disaster. 8 replicas opened 80 pooled connections, blowing straight past the Aurora primary database connection limit of 40. The database dropped active connections and crashed the entire production cluster. The agent's ungrounded 'fix' caused a complete customer-facing outage."*

---

#### [1:30 – 2:05] Part 4: The AFTER Demonstration (With Amazon S3 Tool)
* **Screen Display:**
  1. Click the green button: **"AFTER (v2 S3 Runbook Grounded)"**.
  2. The alert banner turns GREEN: *"🛡️ ACTIVE: AegisOps v2 (Amazon S3 Operational Runbook Grounding Active)"*.
  3. Click **"⚡ RUN DUAL-BRAIN AGENT"**.
  4. The S3 card lights up with metadata (`s3://.../checkout-api-v2.json`, Version `v2.4.1`, ETag `7f8a9b1c`).
  5. Decider 2B reflex panel flashes: `Clamped scale from 8 down to 4 tasks in 41ms`.
  6. The status badge turns glowing green: `✅ PROTECTED - ZERO DOWNTIME`.
* **Your Voiceover:**
  > *"Now, watch what happens AFTER wiring up the Amazon S3 Runbook tool.*
  > 
  > *In just **12 milliseconds**, the agent fetches `s3://aegis-enterprise-runbooks/services/checkout-api-v2.json`. The runbook specifies that maximum safe scaling is **4 tasks** because the Aurora pool ceiling is 40.*
  > 
  > *Our System 1—**Strands Decider 2B**—intercepts the naive proposal in just **41 milliseconds**, clamps the scale from 8 down to 4, and executes a 100% safe remediation.*
  > 
  > *Meanwhile, **Amazon Bedrock** synthesizes an executive post-mortem citing the exact S3 runbook version and compliance check. Zero downtime, zero database crashes."*

---

#### [2:05 – 2:35] Part 5: Reusability, Architecture & Closing
* **Screen Display:** Briefly show the `run_s3_demo.py` terminal summary table or `reusable_patterns/s3_runbook_guardrail_recipe.py` in VS Code.
* **Your Voiceover:**
  > *"By adding this single Amazon S3 tool, we turned an uncontrollable autonomous agent into a safe, policy-governed SRE copilot.*
  > 
  > *I've packaged this into a reusable `S3RunbookGuardrailRecipe` so any developer using Strands Agents SDK and Amazon Bedrock can drop this exact pattern into their own agents.*
  > 
  > *Thank you, and happy building on AWS!"*
