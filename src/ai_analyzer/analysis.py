from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict, Any

from ai_analyzer.config import LLMConfig
from ai_analyzer.llm import chat
from ai_analyzer.schemas import (
    Ambiguity,
    ClarificationReport,
    RequirementSummary,
    RiskAssessment,
)
from ai_analyzer.reflection import reflect
from ai_analyzer.tools import detect_ambiguities, generate_questions, score_risk, decide_tools
from ai_analyzer.prompts import ANALYSIS_SYSTEM, ANALYSIS_USER_TEMPLATE


@dataclass
class ContextItem:
    text: str
    metadata: dict
    score: float


def build_prompt(requirement: str, contexts: List[ContextItem], heuristics: List[str]) -> list:
    context_block = "\n".join(
        [f"[{c.metadata.get('type','unknown')}|{c.metadata.get('source')}] {c.text}" for c in contexts]
    )
    heuristics_block = "\n".join(f"- {h}" for h in heuristics) if heuristics else "- none"

    user = ANALYSIS_USER_TEMPLATE.format(
        requirement=requirement, k=len(contexts), context_block=context_block, heuristics_block=heuristics_block
    )
    return [{"role": "system", "content": ANALYSIS_SYSTEM}, {"role": "user", "content": user}]


def run_analysis(
    requirement: str,
    contexts: List[ContextItem],
    llm_config: LLMConfig,
    enable_reflection: bool = True,
    debug_raw: bool = False,
    debug_reflect: bool = False,
    trace: Optional[List[Dict[str, Any]]] = None,
) -> ClarificationReport:
    trace = trace if trace is not None else []
    heuristics = detect_ambiguities(requirement)
    trace.append({"step": "heuristics", "info": {"count": len(heuristics)}})
    tools = decide_tools(heuristics)
    trace.append({"step": "planner", "info": {"tools": tools}})
    messages = build_prompt(requirement, contexts, heuristics)
    raw = chat(messages, llm_config)
    trace.append({"step": "analysis_llm", "info": {"provider": llm_config.provider, "model": llm_config.model}})
    if debug_raw:
        print(f"[DEBUG] model raw:\n{raw}\n")
    report = parse_or_fallback(raw, requirement, heuristics, tools, trace=trace)
    if enable_reflection:
        try:
            report = reflect(report, llm_config, debug_reflect=debug_reflect, trace=trace)
        except Exception as exc:
            report.reflection = f"Reflection failed: {exc}"
            trace.append({"step": "reflection_error", "info": {"error": str(exc)}})
    return report


def parse_or_fallback(
    raw: str,
    requirement: str,
    heuristics: List[str],
    tools: List[str],
    trace: Optional[List[Dict[str, Any]]] = None,
) -> ClarificationReport:
    trace = trace if trace is not None else []
    try:
        data = json.loads(raw)
        return ClarificationReport.model_validate(data)
    except Exception:
        trace.append({"step": "analysis_parse_fallback", "info": {}})
        # Heuristic fallback
        ambiguities = [Ambiguity(issue=h) for h in heuristics] if heuristics else []
        score, rationale = score_risk(len(ambiguities))
        questions = generate_questions(heuristics) if "question_generator" in tools else []
        return ClarificationReport(
            summary=RequirementSummary(text=requirement[:240]),
            ambiguities=ambiguities,
            questions=questions,
            risk=RiskAssessment(score=score, rationale=rationale),
            confidence=0.4 if heuristics else 0.6,
            reflection="LLM parsing failed; used heuristic fallback.",
        )
