from __future__ import annotations

import json
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


def has_event_structure(text: str) -> bool:
    lower = text.lower()
    keywords = ["event", "timestamp", "severity", "affected entity", "event id"]
    return ("event" in lower and "timestamp" in lower and "severity" in lower) or sum(
        k in lower for k in keywords
    ) >= 3


def has_retry_policy(text: str) -> bool:
    lower = text.lower()
    if "retry" not in lower:
        return False
    has_interval = any(tok in lower for tok in ["second", "sec", "minute", "min", "backoff"])
    has_count = bool(re.search(r"\b\d+\s*(x|times|retries|retry)\b", lower)) or "retry up to" in lower
    has_fallback = any(tok in lower for tok in ["fallback", "email", "sms", "alternate", "channel"])
    return (has_interval and has_count) or (has_count and has_fallback)


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

    # Ops events & retries: only flag if missing
    if not has_event_structure(text):
        findings.append("Operational event structure undefined")
    if not has_retry_policy(text):
        findings.append("Notification retry policy unspecified")
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
    return questions


def generate_questions_with_filter(ambiguities: List[str], requirement_text: str) -> List[str]:
    """
    Generate questions but drop ones that are already answered in the requirement/context.
    """
    lower = requirement_text.lower()

    def answered(amb: str) -> bool:
        if "event structure" in amb.lower():
            return has_event_structure(requirement_text)
        if "retry policy" in amb.lower():
            return has_retry_policy(requirement_text)
        return False

    filtered = [amb for amb in ambiguities if not answered(amb)]
    questions = generate_questions(filtered)

    has_acceptance = "acceptance" in lower or "criteria" in lower or has_metrics(requirement_text)
    if not filtered and not has_acceptance:
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


# ---- LLM tool selection (optional) ----

LLM_TOOL_SET = {
    "ambiguity_detector": "Detect vague or underspecified statements.",
    "question_generator": "Generate follow-up clarification questions.",
    "risk_scorer": "Assign delivery risk score and rationale.",
}


def choose_tools_llm(requirement: str, heuristics: List[str], llm_config) -> List[str]:
    """
    Minimal tool-calling style planner: ask the LLM which helper tools to run.
    Falls back to decide_tools on any error.
    """
    try:
        from ai_analyzer.llm import chat  # local import to avoid cycles
    except Exception:
        return decide_tools(list(heuristics))

    heuristics_text = "\n".join(f"- {h}" for h in heuristics) if heuristics else "None"
    tool_list = "\n".join([f"- {name}: {desc}" for name, desc in LLM_TOOL_SET.items()])
    prompt = [
        {
            "role": "system",
            "content": "You are a planner. Choose the minimal set of tools needed to analyze the requirement.",
        },
        {
            "role": "user",
            "content": f"""Requirement:
{requirement}

Heuristic signals:
{heuristics_text}

Available tools:
{tool_list}

Return ONLY JSON: {{"tools": ["tool_name", ...]}}""",
        },
    ]
    try:
        raw = chat(prompt, llm_config, max_tokens=200, mime="application/json")
        data = json.loads(raw)
        chosen = data.get("tools", []) if isinstance(data, dict) else []
        filtered = [t for t in chosen if t in LLM_TOOL_SET]
        return filtered or decide_tools(list(heuristics))
    except Exception:
        return decide_tools(list(heuristics))
