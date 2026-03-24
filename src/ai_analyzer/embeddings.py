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
            # batch to reduce round-trips; adjust batch size to ease rate limits
            for start in range(0, len(texts), 64):
                batch = texts[start : start + 128]
                response = client.embeddings.create(model=config.model, input=batch)
                vectors.extend([item.embedding for item in response.data])
            return np.array(vectors, dtype="float32")

        return embed

    if config.provider == "gemini":
        try:
            from google.genai import Client
        except ImportError as exc:
            raise ImportError(
                "google-genai is required for GEMINI embeddings. Install with `pip install google-genai`."
            ) from exc

        client = Client(api_key=config.api_key)
        model_name = config.model
        #if not model_name.startswith("models/"):
        #    model_name = f"{model_name}"

        def embed(texts: List[str]) -> np.ndarray:
            vectors: List[List[float]] = []
            for text in texts:
                resp = client.models.embed_content(model=model_name, contents=[text])
                vectors.append(resp.embeddings[0].values)
            return np.array(vectors, dtype="float32")

        return embed

    raise ValueError(f"Unsupported embedding provider: {config.provider}")
