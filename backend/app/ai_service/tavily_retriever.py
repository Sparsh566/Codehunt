"""Tavily Authoritative Search & Retrieval Service.

Fetches contextual reference links for the "Learn More" research drawer.
Strictly restricted to authoritative domains (incois.gov.in, moes.gov.in, imd.gov.in, oceandecade.org).
NEVER used to validate decisions.
"""

import logging
from typing import Optional, List, Dict, Any
from tavily import TavilyClient

from backend.app.config import settings
from backend.app.ai_service.fallback_engine import get_fallback_learn_more

logger = logging.getLogger(__name__)

AUTHORITATIVE_DOMAINS = [
    "incois.gov.in",
    "moes.gov.in",
    "imd.gov.in",
    "oceandecade.org"
]

class TavilyRetriever:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.TAVILY_API_KEY
        self.client = None
        if self.api_key:
            try:
                self.client = TavilyClient(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Could not initialize Tavily client: {e}")

    def search_authoritative(
        self,
        query: str,
        topic: str = "general",
        max_results: int = 3
    ) -> Dict[str, Any]:
        """Queries Tavily restricted strictly to official Indian and UN ocean domains.

        Falls back gracefully to curated INCOIS resources if offline or unavailable.
        """
        # Ensure query explicitly mentions INCOIS and ocean literacy
        enriched_query = f"{query} site:incois.gov.in OR site:moes.gov.in OR site:imd.gov.in OR site:oceandecade.org"

        if not self.client or not self.api_key:
            results = get_fallback_learn_more(topic)
            return {
                "query": query,
                "provider": "curated_incois_fallback",
                "results": results[:max_results]
            }

        try:
            response = self.client.search(
                query=enriched_query,
                search_depth="basic",
                include_domains=AUTHORITATIVE_DOMAINS,
                max_results=max_results
            )
            items = []
            for item in response.get("results", []):
                items.append({
                    "title": item.get("title", "Official Ocean Advisory"),
                    "url": item.get("url", "https://incois.gov.in"),
                    "snippet": item.get("content", "")[:280],
                    "source": item.get("url", "").split("//")[-1].split("/")[0]
                })

            if not items:
                items = get_fallback_learn_more(topic)

            return {
                "query": query,
                "provider": "tavily_live",
                "results": items[:max_results]
            }
        except Exception as e:
            logger.warning(f"Tavily search failed ({e}). Returning curated authoritative fallback.")
            return {
                "query": query,
                "provider": "curated_incois_fallback_degraded",
                "results": get_fallback_learn_more(topic)[:max_results]
            }
