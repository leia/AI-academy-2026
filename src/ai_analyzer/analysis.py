from __future__ import annotations

import json
import re
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
from ai_analyzer.tools import (
    detect_ambiguities,
    score_risk,
    decide_tools,
    generate_questions,
    choose_tools_llm,
)
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


STOPWORDS = {
    "the", "a", "an", "of", "and", "or", "to", "for", "in", "on", "at", "by", "with",
    "is", "are", "be", "been", "was", "were", "this", "that", "these", "those",
    "what", "which", "who", "whom", "whose", "how", "do", "does", "did", "it",
    "its", "their", "them", "our", "we", "you", "your", "yours"
}


def question_answered(question: str, requirement_text: str, context_text: str) -> bool:
    """Heuristic: if most content words from the question appear in requirement+context, treat as answered."""
    tokens = re.findall(r"[a-z0-9]+", question.lower())
    content = [t for t in tokens if t not in STOPWORDS and len(t) > 2]
    if not content:
        return False
    haystack = f"{requirement_text} {context_text}"
    hits = sum(1 for t in content if t in haystack)
    return hits / len(content) >= 0.6


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
    tools = choose_tools_llm(requirement, heuristics, llm_config)
    trace.append({"step": "planner_llm", "info": {"tools": tools}})
    messages = build_prompt(requirement, contexts, heuristics)
    raw = chat(messages, llm_config, mime="application/json")
    trace.append({"step": "analysis_llm", "info": {"provider": llm_config.provider, "model": llm_config.model}})
    if debug_raw:
        print(f"[DEBUG] model raw:\n{raw}\n")
    report = parse_or_fallback(raw, requirement, heuristics, tools, trace=trace)
    # Heuristic reinforcement: if model omitted ambiguities/questions but heuristics found issues, inject them.
    if heuristics and (not report.ambiguities or len(report.ambiguities) == 0):
        trace.append({"step": "heuristic_inject_ambiguities", "info": {"count": len(heuristics)}})
        report.ambiguities = [Ambiguity(issue=h) for h in heuristics]
        report.questions = report.questions or []
        heuristic_score, heuristic_rationale = score_risk(len(report.ambiguities))
        if report.risk.score < heuristic_score:
            report.risk.score = heuristic_score
            report.risk.rationale = report.risk.rationale or heuristic_rationale
        # Lower confidence if we had to inject
        report.confidence = min(report.confidence, 0.6)
        if report.reflection:
            report.reflection += " | Heuristic ambiguities/questions injected."
        else:
            report.reflection = "Heuristic ambiguities/questions injected because model omitted them."
    if enable_reflection:
        try:
            report = reflect(report, llm_config, debug_reflect=debug_reflect, trace=trace)
        except Exception as exc:
            report.reflection = f"Reflection failed: {exc}"
            trace.append({"step": "reflection_error", "info": {"error": str(exc)}})
    # Simple iteration: if confidence remains low, re-run once with higher k/context
    if enable_reflection and report.confidence < 0.5:
        trace.append({"step": "iteration_trigger", "info": {"reason": "low_confidence", "confidence": report.confidence}})
        # Re-run analysis; in a fuller loop we might increase k, but keep it simple here.
        messages = build_prompt(requirement, contexts, heuristics)
        raw2 = chat(messages, llm_config)
        trace.append({"step": "analysis_llm_retry", "info": {"provider": llm_config.provider, "model": llm_config.model}})
        report = parse_or_fallback(raw2, requirement, heuristics, tools, trace=trace)
    # Post-adjust confidence/risk based on ambiguity count to avoid overconfidence
    ambiguity_count = len(report.ambiguities or [])
    if ambiguity_count >= 2:
        target_conf = max(0.35, 0.7 - 0.06 * (ambiguity_count - 1))
        if report.confidence > target_conf:
            trace.append({"step": "confidence_adjust", "info": {"from": report.confidence, "to": target_conf}})
            report.confidence = target_conf
        min_risk = min(0.9, 0.35 + 0.1 * ambiguity_count)
        if report.risk.score < min_risk:
            trace.append({"step": "risk_adjust", "info": {"from": report.risk.score, "to": min_risk}})
            report.risk.score = min_risk
            if not report.risk.rationale:
                report.risk.rationale = "Raised to reflect unresolved ambiguities."
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
