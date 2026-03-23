from __future__ import annotations

from typing import Callable, List

import numpy as np
from openai import OpenAI

from ai_analyzer.config import EmbedConfig


def build_embed_fn(config: EmbedConfig) -> Callable[[List[str]], np.ndarray]:
    """
    Return a function that embeds a list of texts into an ndarray of shape (n, d).
    Supports OpenAI and Gemini (Google Generative AI).
    """

    if config.provider == "openai":
        client = OpenAI(api_key=config.api_key, base_url=config.base_url)

        def embed(texts: List[str]) -> np.ndarray:
            vectors: List[List[float]] = []
            # batch to reduce round-trips; OpenAI allows up to ~2048 tokens per item
            for start in range(0, len(texts), 128):
                batch = texts[start : start + 128]
                response = client.embeddings.create(model=config.model, input=batch)
                vectors.extend([item.embedding for item in response.data])
            return np.array(vectors, dtype="float32")

        return embed

    if config.provider == "gemini":
        import google.generativeai as genai

        genai.configure(api_key=config.api_key)

        def embed(texts: List[str]) -> np.ndarray:
            vectors: List[List[float]] = []
            for text in texts:
                resp = genai.embed_content(model=config.model, content=text)
                vectors.append(resp["embedding"])
            return np.array(vectors, dtype="float32")

        return embed

    raise ValueError(f"Unsupported embedding provider: {config.provider}")
