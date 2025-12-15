"""
LLM Router - The brain switchboard.

All LLM calls go through here. Agents don't care which model
is under the hood, they just ask for completions and get answers.

This is the layer that makes switching from Gemini to Claude to GPT
a 5-minute config change instead of a 5-hour refactor.
"""

from .router import LLMRouter, llm_router

__all__ = ["LLMRouter", "llm_router"]
