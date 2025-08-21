from __future__ import annotations
from typing import Dict, Any, List
import os
import logging

logger = logging.getLogger(__name__)

class ExternalAIConnector:
    """
    Adapter to external LLMs or AI services.
    In CI/localhost without keys, returns deterministic simple outputs.
    """
    def __init__(self):
        self.provider = os.getenv("EXT_AI_PROVIDER", "mock")
        self.api_key  = os.getenv("EXT_AI_API_KEY")

    def complete_text(self, prompt: str, max_tokens: int = 256) -> str:
        if not self.api_key:
            return f"[MOCK COMPLETION] {prompt[:120]} ..."
        # Place real HTTP call here
        logger.warning("External AI call is stubbed; returning mock-like output.")
        return f"[STUB COMPLETION] {prompt[:120]} ..."

    def extract_concepts(self, text: str) -> List[Dict[str, Any]]:
        """
        Simple heuristic concept extractor; replace with LLM in prod.
        """
        tokens = [t.strip(",.()[]:;!?") for t in text.split()]
        uniq = []
        for t in tokens:
            if len(t) >= 4 and t.lower() not in uniq:
                uniq.append(t.lower())
        uniq = uniq[:5]
        return [{"label": u, "attributes": {"type": "entity", "modality": ["linguistic"]}, "relations": [], "confidence": 0.5} for u in uniq]
