from __future__ import annotations

import re
from typing import List, Tuple

# Each tuple: (regex, description)
AMBIGUITY_PATTERNS = [
    (r"\bimprov(e|ement)\b.*\b(ux|usability|ui)\b", "Vague UX improvement"),
    (r"\b(make|made)\s+it\s+faster\b", "Vague speed goal"),
    (r"\bperformance\b", "Performance mentioned; metrics unspecified"),
    (r"\ball\b.*\b(devices|browsers)\b", "Unbounded device/browser scope"),
    (r"\bsoon\b|\basap\b|\bquickly\b", "Vague timeline"),
    (r"\boptimi[sz]e\b", "Optimize without target metric"),
    (r"\bno\s+downtime\b", "Zero-downtime claim without window/plan"),
    (r"\bscal(?:e|able|ability)\b", "Scale mentioned; load not specified"),
]


METRIC_PATTERN = re.compile(
    r"""
    (                                   # numeric values with units
        \b\d+(\.\d+)?\s?
        (ms|s|sec|min|minutes|hours|rps|req/s|%)\b
    )
    |
    \bsla\b
    |
    \blatency\b
    """,
    re.IGNORECASE | re.VERBOSE,
)


def has_metrics(text: str) -> bool:
    return bool(METRIC_PATTERN.search(text))


def detect_ambiguities(text: str) -> List[str]:
    findings = []
    lower = text.lower()
    for pattern, desc in AMBIGUITY_PATTERNS:
        if re.search(pattern, lower, flags=re.IGNORECASE):
            if "performance" in desc and has_metrics(text):
                continue  # metrics present, skip this hit
            if "scale" in desc and has_metrics(text):
                continue
            findings.append(desc)

    # Only flag missing acceptance if we don't see metrics/SLA-like signals
    if "acceptance" not in lower and "criteria" not in lower and not has_metrics(text):
        findings.append("Missing acceptance criteria")

    # Non-measurable improvement heuristic
    if any(word in lower for word in ["improve", "better", "faster"]) and not has_metrics(text):
        findings.append("Non-measurable goal (no metrics provided)")
    return findings


def score_risk(num_ambiguities: int) -> Tuple[float, str]:
    if num_ambiguities == 0:
        return 0.2, "Low ambiguity detected."
    if num_ambiguities == 1:
        return 0.35, "Single ambiguity; clarify before committing."
    if num_ambiguities == 2:
        return 0.55, "Multiple ambiguities; delivery risk medium."
    return 0.75, "High ambiguity count; risk elevated until clarified."


def generate_questions(ambiguities: List[str]) -> List[str]:
    questions = []
    for amb in ambiguities:
        questions.append(f"Can you clarify: {amb}?")
    if not ambiguities:
        questions.append("What are the success metrics and acceptance criteria?")
    return questions


def decide_tools(heuristics: List[str]) -> List[str]:
    """
    Simple planner to decide which helper tools to run.
    Always runs ambiguity detection (already done); conditionally include follow-ups.
    """
    tools = ["ambiguity_detector"]
    if heuristics:
        tools.append("question_generator")
        tools.append("risk_scorer")
    else:
        tools.append("question_generator")  # still useful even without detected ambiguities
    return tools
