from __future__ import annotations

import json
from typing import List

from ai_analyzer.config import LLMConfig
from ai_analyzer.llm import chat
from ai_analyzer.schemas import ClarificationReport
from ai_analyzer.prompts import REFLECTION_SYSTEM


def reflect(report: ClarificationReport, llm_config: LLMConfig) -> ClarificationReport:
    user = f"Here is the report to critique:\n\n{report.model_dump_json(indent=2)}"
    messages = [{"role": "system", "content": REFLECTION_SYSTEM}, {"role": "user", "content": user}]
    raw = chat(messages, llm_config, max_tokens=400)
    try:
        data = json.loads(raw)
    except Exception:
        # If reflection fails, just annotate and return
        report.reflection = "Reflection failed to parse; keeping original report."
        return report

    gaps: List[str] = data.get("gaps", [])
    adjustments = data.get("adjustments", {}) or {}
    revision = data.get("revision")

    # Apply revision if present and valid
    if revision:
        try:
            report = ClarificationReport.model_validate(revision)
        except Exception:
            # keep original, but note the issue
            report.reflection = "Reflection revision was invalid; kept original."
            return report

    # Apply adjustments
    conf_delta = float(adjustments.get("confidence_delta", 0))
    risk_delta = float(adjustments.get("risk_delta", 0))
    report.confidence = min(1.0, max(0.0, report.confidence + conf_delta))
    report.risk.score = min(1.0, max(0.0, report.risk.score + risk_delta))

    # Append reflection notes
    gap_text = "; ".join(gaps) if gaps else "No additional gaps noted."
    note_parts = [gap_text]
    if conf_delta or risk_delta:
        note_parts.append(f"Applied adjustments: confidence {conf_delta:+}, risk {risk_delta:+}.")
    report.reflection = " ".join(note_parts)
    return report
