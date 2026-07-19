"""Shared Inspect helpers (temperature policy, prompt loading)."""

from __future__ import annotations

from pathlib import Path

from src import PROMPTS_DIR

# Ported from bird-taxonomy-evals: newer Anthropic / OpenAI reasoning models
# reject an explicit temperature param.
_ANTHROPIC_TEMPERATURE_OK_PREFIXES = ("claude-haiku-", "claude-sonnet-4", "claude-3-")
_OPENAI_NO_TEMPERATURE_PREFIXES = ("gpt-5", "o3", "o4")


def temp_for(model_name: str, *, default: float = 0.0) -> float | None:
    """Return temperature to request, or None to omit the param."""
    bare = model_name.split("/", 1)[-1]
    if bare.startswith("claude"):
        return default if bare.startswith(_ANTHROPIC_TEMPERATURE_OK_PREFIXES) else None
    return None if bare.startswith(_OPENAI_NO_TEMPERATURE_PREFIXES) else default


def load_prompt(name: str) -> str:
    path = PROMPTS_DIR / name
    return path.read_text(encoding="utf-8")
