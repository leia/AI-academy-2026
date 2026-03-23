from typing import List, Optional

from pydantic import BaseModel, Field


class RequirementSummary(BaseModel):
    """Concise restatement of the user's requirement."""

    text: str = Field(..., description="One or two sentences summarizing the requirement.")


class Ambiguity(BaseModel):
    """Represents a detected ambiguity or missing detail."""

    issue: str = Field(..., description="What is ambiguous or underspecified.")
    impact: Optional[str] = Field(
        None, description="Potential delivery impact if unresolved (optional)."
    )
    severity: Optional[str] = Field(
        None,
        description="Qualitative severity band (e.g., low/medium/high) if heuristic scoring is used.",
    )


class RiskAssessment(BaseModel):
    """Lightweight risk view tied to ambiguity and uncertainty."""

    score: float = Field(..., ge=0.0, le=1.0, description="Normalized delivery risk score 0-1.")
    rationale: Optional[str] = Field(None, description="Brief reason for the score.")


class ClarificationReport(BaseModel):
    """
    Primary structured output contract used by the CLI and downstream consumers.

    Designed to be JSON-serializable and stable for logging or evaluation harnesses.
    """

    summary: RequirementSummary
    ambiguities: List[Ambiguity]
    questions: List[str] = Field(default_factory=list, description="Clarifying questions to ask.")
    risk: RiskAssessment
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Model self-reported confidence in the overall report.",
    )
    reflection: Optional[str] = Field(
        None, description="Self-critique or notes about assumptions and next steps."
    )


__all__ = [
    "RequirementSummary",
    "Ambiguity",
    "RiskAssessment",
    "ClarificationReport",
]
