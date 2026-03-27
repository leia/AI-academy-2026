from __future__ import annotations

from typing import List, Dict

from ai_analyzer.config import LLMConfig
from ai_analyzer.llm import chat


QA_SYSTEM = """You are a concise assistant. Answer the user's question using ONLY the provided context. 
If the answer is not in the context, reply with "I don't know." Keep answers under 120 words."""


def build_qa_prompt(question: str, contexts: List[Dict]) -> list:
    context_block = "\n".join([f"[{c['metadata'].get('source')}] {c['text']}" for c in contexts])
    user = f"Question: {question}\n\nContext:\n{context_block}"
    return [{"role": "system", "content": QA_SYSTEM}, {"role": "user", "content": user}]


def answer_question(question: str, contexts: List[Dict], llm_config: LLMConfig) -> str:
    messages = build_qa_prompt(question, contexts)
    return chat(messages, llm_config, max_tokens=256, mime="text/plain")
