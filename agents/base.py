"Base agent setup and LLM factory utilities."

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BaseAgent:
    """Marker base class for agents.

    Previously this carried a LangChain LLM instance. We now call Gemini
    directly via `core.gemini_client`, so this class is intentionally minimal.
    """

    pass

