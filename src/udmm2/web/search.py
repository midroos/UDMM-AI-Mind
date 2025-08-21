from __future__ import annotations
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import os
import logging

logger = logging.getLogger(__name__)

class SearchResult(BaseModel):
    title: str
    url: str
    snippet: Optional[str] = None
    source: str = "web"

class WebPerceptionModule:
    """
    Abstraction over web search providers. Default: a safe mock if no API keys.
    Plug actual Google CSE / Bing in _real_google/_real_bing.
    """
    def __init__(self):
        self.google_key = os.getenv("GOOGLE_API_KEY")
        self.google_cx  = os.getenv("GOOGLE_CSE_ID")
        self.bing_key   = os.getenv("BING_API_KEY")

    def search(self, query: str, provider: str = "auto", k: int = 5) -> List[SearchResult]:
        try:
            provider = provider.lower()
            if provider == "google" and self.google_key and self.google_cx:
                return self._real_google(query, k)
            if provider == "bing" and self.bing_key:
                return self._real_bing(query, k)
            # auto / fallback
            if self.google_key and self.google_cx:
                return self._real_google(query, k)
            if self.bing_key:
                return self._real_bing(query, k)
            return self._mock(query, k)
        except Exception:
            logger.exception("search failed; returning mock")
            return self._mock(query, k)

    def _mock(self, query: str, k: int) -> List[SearchResult]:
        base = [
            SearchResult(title=f"About {query} – overview", url=f"https://example.org/{query}/overview", snippet="Mocked overview."),
            SearchResult(title=f"{query} applications", url=f"https://example.org/{query}/apps", snippet="Mocked applications."),
            SearchResult(title=f"{query} risks", url=f"https://example.org/{query}/risks", snippet="Mocked risks."),
        ]
        return base[:k]

    def _real_google(self, query: str, k: int) -> List[SearchResult]:
        # NOTE: keep it simple; real HTTP request omitted by design (plug requests here if needed)
        # This stub keeps code import-safe in CI. Replace with actual calls in deployment.
        logger.warning("Google CSE keys found but HTTP call is stubbed; returning mock.")
        return self._mock(query, k)

    def _real_bing(self, query: str, k: int) -> List[SearchResult]:
        logger.warning("Bing API key found but HTTP call is stubbed; returning mock.")
        return self._mock(query, k)

    # Transform search results to semantic concepts
    def to_concepts(self, results: List[SearchResult]) -> List[Dict[str, Any]]:
        concepts = []
        for r in results:
            concepts.append({
                "label": r.title,
                "attributes": {
                    "type": "entity",
                    "modality": ["linguistic", "web"],
                    "source_url": r.url,
                },
                "relations": [],
                "confidence": 0.6,
            })
        return concepts
