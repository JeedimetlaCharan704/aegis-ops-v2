"""Configuration settings for AegisOps Autonomous SRE Agent."""

import os
from dataclasses import dataclass

@dataclass
class AegisConfig:
    # AWS Bedrock Configuration
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    BEDROCK_MODEL_ID: str = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")
    BEDROCK_FAST_MODEL_ID: str = os.getenv("BEDROCK_FAST_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")

    # Strands Decider 2B Configuration
    DECIDER_ENDPOINT: str = os.getenv("DECIDER_ENDPOINT", "http://127.0.0.1:8000/v1/systemone")
    DECIDER_MODEL_NAME: str = "StrandsAgents/strands-decider-2B-qwen3.5-v1-2610"
    
    # Decision Gate Thresholds
    CONFIDENCE_PROCEED_THRESHOLD: float = 0.85
    CONFIDENCE_HUMAN_CONFIRM_THRESHOLD: float = 0.60
    
    # Benchmark Constants
    BEDROCK_INPUT_COST_PER_1K: float = 0.003
    BEDROCK_OUTPUT_COST_PER_1K: float = 0.015
    DECIDER_COST_PER_QUERY: float = 0.00000  # Local CPU/GPU compute has 0 API token cost
    
    # Environment mode
    SIMULATED_AWS: bool = os.getenv("SIMULATED_AWS", "true").lower() == "true"

config = AegisConfig()
