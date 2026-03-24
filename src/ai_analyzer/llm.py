from __future__ import annotations

from typing import List, Dict, Any

from anthropic import Anthropic
from openai import OpenAI

from ai_analyzer.config import LLMConfig


def chat(messages: List[Dict[str, str]], config: LLMConfig, max_tokens: int = 800) -> str:
    """
    Minimal abstraction over provider-specific chat APIs.
    Accepts OpenAI-style message dicts: [{role: system|user, content: "..."}].
    Returns the model text content (first candidate).
    """
    if config.provider == "openai":
        client = OpenAI(api_key=config.api_key, base_url=config.base_url)
        resp = client.chat.completions.create(model=config.model, messages=messages, max_tokens=max_tokens)
        return resp.choices[0].message.content

    if config.provider == "claude":
        client = Anthropic(api_key=config.api_key)
        system_parts = [m["content"] for m in messages if m["role"] == "system"]
        user_parts = [m["content"] for m in messages if m["role"] == "user"]
        system_text = "\n".join(system_parts)
        user_text = "\n\n".join(user_parts)
        resp = client.messages.create(
            model=config.model,
            max_tokens=max_tokens,
            system=system_text or None,
            messages=[{"role": "user", "content": user_text}],
        )
        return resp.content[0].text

    if config.provider == "gemini":
        import google.generativeai as genai

        genai.configure(api_key=config.api_key)
        # Flatten to a single prompt string; Gemini v1 does not support multi-turn in the same way.
        system_parts = [m["content"] for m in messages if m["role"] == "system"]
        user_parts = [m["content"] for m in messages if m["role"] == "user"]
        prompt = ""
        if system_parts:
            prompt += "System:\n" + "\n".join(system_parts) + "\n\n"
        prompt += "User:\n" + "\n".join(user_parts)
        model = genai.GenerativeModel(config.model)
        resp = model.generate_content(prompt)
        return resp.text

    raise ValueError(f"Unsupported provider: {config.provider}")
