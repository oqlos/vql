"""Load VQL pipeline configuration from environment / .env."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    for candidate in (Path.cwd() / ".env", Path(__file__).resolve().parents[5] / ".env"):
        if candidate.is_file():
            load_dotenv(candidate, override=False)
            return


def _env_bool(name: str, default: bool = False) -> bool:
    raw = (os.environ.get(name) or "").strip().lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes", "on"}


def _env_float(name: str, default: float) -> float:
    raw = (os.environ.get(name) or "").strip()
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


# OpenRouter vision models (see https://openrouter.ai/models?modality=image)
DEFAULT_VQL_VISION_MODEL = "google/gemini-2.5-flash-preview"


def normalize_openrouter_model(model: str) -> str:
    """
    OpenRouter API expects slugs like ``google/gemini-2.5-flash-preview``.

    Cursor/pfix often uses ``openrouter/google/...`` — strip that prefix.
    """
    m = (model or "").strip()
    if m.startswith("openrouter/"):
        m = m[len("openrouter/") :]
    return m


def resolve_vql_llm_model() -> str:
    """
    Vision model for L5 extraction.

    Uses VQL_LLM_MODEL only — do NOT fall back to LLM_MODEL (usually a text coder).
    """
    explicit = (os.environ.get("VQL_LLM_MODEL") or "").strip()
    if explicit:
        return normalize_openrouter_model(explicit)
    return DEFAULT_VQL_VISION_MODEL


@dataclass(frozen=True)
class PipelineLLMConfig:
    enabled: bool
    api_key: str
    model: str
    base_url: str
    vision: bool
    temperature: float
    max_tokens: int
    timeout_s: float

    @property
    def configured(self) -> bool:
        return self.enabled and bool(self.api_key)


@dataclass(frozen=True)
class PipelineConfig:
    locale: str
    grid: int
    adopt_method: str
    llm: PipelineLLMConfig
    save_render: bool
    merge_llm_layers: bool

    @classmethod
    def from_env(cls, *, locale: str = "pl", grid: int = 12, adopt_method: str = "auto") -> PipelineConfig:
        _load_dotenv()
        model = resolve_vql_llm_model()
        api_key = (
            os.environ.get("VQL_LLM_API_KEY")
            or os.environ.get("OPENROUTER_API_KEY")
            or os.environ.get("OPENAI_API_KEY")
            or ""
        )
        llm = PipelineLLMConfig(
            enabled=_env_bool("VQL_LLM_ENABLED", default=bool(api_key)),
            api_key=api_key,
            model=model,
            base_url=os.environ.get("VQL_LLM_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/"),
            vision=_env_bool("VQL_LLM_VISION", default=True),
            temperature=_env_float("VQL_LLM_TEMPERATURE", 0.1),
            max_tokens=int(_env_float("VQL_LLM_MAX_TOKENS", 4096)),
            timeout_s=_env_float("VQL_LLM_TIMEOUT", 120.0),
        )
        return cls(
            locale=locale,
            grid=grid,
            adopt_method=(os.environ.get("VQL_ADOPT_METHOD") or adopt_method).strip().lower(),
            llm=llm,
            save_render=_env_bool("VQL_SAVE_RENDER", default=True),
            merge_llm_layers=_env_bool("VQL_LLM_MERGE_LAYERS", default=True),
        )
