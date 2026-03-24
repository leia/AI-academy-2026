from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from ai_analyzer.config import LLMConfig
from ai_analyzer.llm import chat
from ai_analyzer.schemas import (
    Ambiguity,
    ClarificationReport,
    RequirementSummary,
    RiskAssessment,
)
from ai_analyzer.reflection import reflect
from ai_analyzer.tools import detect_ambiguities, generate_questions, score_risk


@dataclass
class ContextItem:
    text: str
    metadata: dict
    score: float


def build_prompt(requirement: str, contexts: List[ContextItem], heuristics: List[str]) -> list:
    context_block = "\n\n".join(
        [f"[{c.metadata.get('type','unknown')}|{c.metadata.get('source')}] {c.text}" for c in contexts]
    )
    heuristic_block = "\n".join(f"- {h}" for h in heuristics)

    system = (
        "You are a senior requirements analyst. Produce a structured JSON report with keys: "
        "summary, ambiguities (list of {issue, impact?, severity?}), questions (list), "
        "risk {score 0-1, rationale}, confidence 0-1, reflection (string). "
        "Stay concise and actionable."
    )
    user = f"""Requirement:
{requirement}

Retrieved context:
{context_block}

Heuristic ambiguity signals:
{heuristic_block}

Return only JSON."""
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def run_analysis(
    requirement: str,
    contexts: List[ContextItem],
    llm_config: LLMConfig,
    enable_reflection: bool = True,
) -> ClarificationReport:
    heuristics = detect_ambiguities(requirement)
    messages = build_prompt(requirement, contexts, heuristics)
    raw = chat(messages, llm_config)
    report = parse_or_fallback(raw, requirement, heuristics)
    if enable_reflection:
        try:
            report = reflect(report, llm_config)
        except Exception as exc:
            report.reflection = f"Reflection failed: {exc}"
    return report


def parse_or_fallback(raw: str, requirement: str, heuristics: List[str]) -> ClarificationReport:
    try:
        data = json.loads(raw)
        return ClarificationReport.model_validate(data)
    except Exception:
        # Heuristic fallback
        ambiguities = [Ambiguity(issue=h) for h in heuristics] if heuristics else []
        score, rationale = score_risk(len(ambiguities))
        questions = generate_questions(heuristics)
        return ClarificationReport(
            summary=RequirementSummary(text=requirement[:240]),
            ambiguities=ambiguities,
            questions=questions,
            risk=RiskAssessment(score=score, rationale=rationale),
            confidence=0.4 if heuristics else 0.6,
            reflection="LLM parsing failed; used heuristic fallback.",
        )
