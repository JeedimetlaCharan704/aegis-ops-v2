"""Typed schema definitions for Strands Decider 2B queries and responses."""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum

class QuestionType(str, Enum):
    NOUL = "noul"      # Binary yes/no with calibrated confidence
    CHOICE = "choice"  # Multi-option categorical selection
    SCORE = "score"    # Ordinal evaluation scale

@dataclass
class TypedQuestion:
    type: QuestionType
    instructions: str
    criteria: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "instructions": self.instructions,
            "criteria": self.criteria
        }

@dataclass
class DeciderEvaluationRequest:
    state: str
    questions: Dict[str, TypedQuestion]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state": self.state,
            "questions": {k: q.to_dict() for k, q in self.questions.items()}
        }

@dataclass
class DeciderEvaluationResponse:
    answers: Dict[str, Any]
    latency_ms: float
    is_simulated: bool = False

    def get_noul_confidence(self, question_id: str) -> float:
        """Get calibrated probability of True for a noul question."""
        ans = self.answers.get(question_id, {})
        if isinstance(ans, dict):
            return float(ans.get("noul", ans.get("probability", 0.0)))
        if isinstance(ans, (float, int)):
            return float(ans)
        return 0.0

    def get_choice(self, question_id: str) -> str:
        """Get the selected choice identifier."""
        ans = self.answers.get(question_id)
        if isinstance(ans, dict):
            return str(ans.get("choice", ans.get("selected", "")))
        return str(ans) if ans is not None else ""
