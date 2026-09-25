from backend.app.ai_service.groq_explainer import GroqExplainer
from backend.app.ai_service.tavily_retriever import TavilyRetriever
from backend.app.ai_service.fallback_engine import get_fallback_explanation, get_fallback_learn_more

_explainer_instance = None
_retriever_instance = None

def get_groq_explainer() -> GroqExplainer:
    global _explainer_instance
    if _explainer_instance is None:
        _explainer_instance = GroqExplainer()
    return _explainer_instance

def get_tavily_retriever() -> TavilyRetriever:
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = TavilyRetriever()
    return _retriever_instance

__all__ = [
    "GroqExplainer",
    "TavilyRetriever",
    "get_groq_explainer",
    "get_tavily_retriever",
    "get_fallback_explanation",
    "get_fallback_learn_more"
]
