import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass
class LLMConfig:
    provider: str
    api_key: str
    model: str
    base_url: str | None = None
    api_version: str | None = None


@dataclass
class EmbedConfig:
    provider: str
    api_key: str
    model: str
    base_url: str | None = None


def load_llm_config() -> LLMConfig:
    """
    Load LLM configuration with support for OpenAI, Claude (Anthropic), and Gemini.
    Defaults to OpenAI if no provider is specified.
    """

    load_dotenv()
    provider = os.getenv("LLM_PROVIDER", "openai").lower()

    if provider == "openai":
        api_key = required("OPENAI_API_KEY")
        model = os.getenv("OPENAI_MODEL", "gpt-4.1")
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        return LLMConfig(provider, api_key, model, base_url)

    if provider == "claude":
        api_key = required("ANTHROPIC_API_KEY")
        model = os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
        base_url = "https://api.anthropic.com"
        return LLMConfig(provider, api_key, model, base_url, api_version="2023-06-01")

    if provider == "gemini":
        api_key = required("GOOGLE_API_KEY")
        model = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
        base_url = "https://generativelanguage.googleapis.com"
        return LLMConfig(provider, api_key, model, base_url)

    raise ValueError(f"Unsupported LLM_PROVIDER '{provider}'.")


def load_embed_config() -> EmbedConfig:
    """
    Load embedding configuration. Default is OpenAI embeddings.
    Supports: openai, gemini.
    """
    load_dotenv()
    provider = os.getenv("EMBED_PROVIDER", "openai").lower()

    if provider == "openai":
        api_key = required("OPENAI_API_KEY")
        model = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        return EmbedConfig(provider, api_key, model, base_url)

    if provider == "gemini":
        api_key = required("GOOGLE_API_KEY")
        model = os.getenv("GEMINI_EMBED_MODEL", "models/embedding-001")
        return EmbedConfig(provider, api_key, model)

    raise ValueError(f"Unsupported EMBED_PROVIDER '{provider}'. Choose 'openai' or 'gemini'.")


def required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value
