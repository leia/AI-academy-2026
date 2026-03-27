from __future__ import annotations

from typing import Dict, List, Optional

from anthropic import Anthropic
from openai import OpenAI

from ai_analyzer.config import LLMConfig
from ai_analyzer.retry_utils import with_retries, backoff_delay


def chat(messages: List[Dict[str, str]], config: LLMConfig, max_tokens: int = 800, mime: Optional[str] = None) -> str:
    """
    Minimal abstraction over provider-specific chat APIs.
    Accepts OpenAI-style message dicts: [{role: system|user, content: "..."}].
    Returns the model text content (first candidate).
    """
    if config.provider == "openai":
        client = OpenAI(api_key=config.api_key, base_url=config.base_url)
        resp = with_retries(
            lambda: client.chat.completions.create(
                model=config.model, messages=messages, max_tokens=max_tokens, temperature=0
            )
        )
        return resp.choices[0].message.content

    if config.provider == "claude":
        client = Anthropic(api_key=config.api_key)
        system_parts = [m["content"] for m in messages if m["role"] == "system"]
        user_parts = [m["content"] for m in messages if m["role"] == "user"]
        system_text = "\n".join(system_parts)
        user_text = "\n\n".join(user_parts)
        resp = with_retries(
            lambda: client.messages.create(
                model=config.model,
                max_tokens=max_tokens,
                system=system_text or None,
                messages=[{"role": "user", "content": user_text}],
                temperature=0,
            )
        )
        return resp.content[0].text

    if config.provider == "gemini":
        try:
            from google import genai
            from google.genai import types as genai_types
        except ImportError as exc:
            raise ImportError(
                "google-genai is required for GEMINI generation. Install with `pip install google-genai`."
            ) from exc

        client = genai.Client(api_key=config.api_key)
        model_name = config.model
        #if not model_name.startswith("models/"):
        #    model_name = f"models/{model_name}"

        # Flatten system + user into a single text prompt
        system_parts = [m["content"] for m in messages if m["role"] == "system"]
        user_parts = [m["content"] for m in messages if m["role"] == "user"]
        prompt = ""
        if system_parts:
            prompt += "System:\n" + "\n".join(system_parts) + "\n\n"
        prompt += "User:\n" + "\n".join(user_parts)

        resp = with_retries(
            lambda: client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    max_output_tokens=max_tokens,
                    response_mime_type=mime or "text/plain",
                    temperature=0,
                ),
            )
        )
        return resp.text

    raise ValueError(f"Unsupported provider: {config.provider}")
