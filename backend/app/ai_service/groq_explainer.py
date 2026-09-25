"""Groq AI Explanation Service.

Calls Groq (llama-3.3-70b-versatile) strictly post-verdict to generate
empathetic, educational, multilingual explanations of the deterministic outcome.
NEVER decides safety, score, or legality of choices.
"""

import logging
from typing import Optional, Dict, Any
from groq import Groq

from backend.app.config import settings
from backend.app.game_engine.schemas import ScenarioDefinition, EvaluationVerdict
from backend.app.ai_service.fallback_engine import get_fallback_explanation

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_EN = """You are an expert Ocean Literacy and Maritime Safety Educator partnering with the Ministry of Earth Sciences (MoES) and INCOIS (Indian National Centre for Ocean Information Services).
A player in an ocean simulation game has just made a maritime decision. The deterministic game engine has ALREADY judged the outcome.
Your sole job is to explain WHY this outcome occurred in clear, educational, engaging language based on ocean physics, meteorology, and INCOIS advisory rules.

Structure your response with:
1. 🌊 **Ocean Dynamics & Physics**: Explain why the ocean conditions (waves, wind, swell, temperature, or currents) created this result.
2. 🧭 **INCOIS Operational Guidance**: Explain the exact rule or advisory lesson seafarers must remember.

Keep the tone encouraging and authoritative. Keep under 140 words. Do NOT recalculate or contradict the verdict."""

SYSTEM_PROMPT_HI = """आप पृथ्वी विज्ञान मंत्रालय (MoES) और भारतीय राष्ट्रीय महासागर सूचना सेवा केंद्र (INCOIS) के विशेषज्ञ समुद्री शिक्षक हैं।
खिलाड़ी ने अभी-अभी समुद्र में एक निर्णय लिया है। गेम इंजन ने पहले ही निर्णय की शुद्धता तय कर दी है।
आपका काम यह समझाना है कि यह परिणाम क्यों हुआ — समुद्र की भौतिकी, लहरों, हवा और INCOIS की चेतावनियों के आधार पर।

सरल, स्पष्ट और प्रभावशाली हिंदी में उत्तर दें (लगभग 120 शब्द):
1. 🌊 **समुद्री भौतिकी व कारण**: समझाएं कि समुद्र की लहरों, हवा या धाराओं ने यह स्थिति कैसे बनाई।
2. 🧭 **INCOIS सलाह व सीख**: बताएं कि नाविक या नागरिक को आगे के लिए क्या याद रखना चाहिए।"""

class GroqExplainer:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model = model or settings.GROQ_MODEL
        self.client = None
        if self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Could not initialize Groq client: {e}")

    def generate_explanation(
        self,
        scenario: ScenarioDefinition,
        verdict: EvaluationVerdict,
        chosen_option_text: str,
        language: str = "en"
    ) -> Dict[str, str]:
        """Generates an educational explanation of the decision verdict.

        Gracefully degrades to the offline fallback engine on any error or timeout.
        """
        lang = language.lower() if language.lower() in ["en", "hi"] else "en"

        # If Groq client is not available or key empty, use deterministic fallback immediately
        if not self.client or not self.api_key:
            fallback = get_fallback_explanation(scenario.scenario_code, verdict.chosen_option_id, lang)
            return {
                "explanation": fallback,
                "language": lang,
                "provider": "offline_fallback"
            }

        sys_prompt = SYSTEM_PROMPT_HI if lang == "hi" else SYSTEM_PROMPT_EN

        user_content = f"""Scenario: {scenario.title} ({scenario.location})
Role: {scenario.role}
Ocean Conditions:
- Wave Height: {scenario.ocean_data.wave_height_m} meters
- Wind Speed: {scenario.ocean_data.wind_speed_knots} knots
- Swell Period: {scenario.ocean_data.swell_period_sec} seconds
- Sea Surface Temperature: {scenario.ocean_data.sea_surface_temp_c}°C
- PFZ Active: {scenario.ocean_data.pfz_zone_active}
- INCOIS Warning: {scenario.ocean_data.incois_warning_type} ({scenario.ocean_data.incois_alert_level} Alert)

Player's Choice: "{chosen_option_text}"
Deterministic Verdict:
- Safety Result: {"SAFE & COMPLIANT" if verdict.is_safe else "DANGEROUS / NON-COMPLIANT"}
- Optimal Action: {"YES" if verdict.is_optimal else "NO"}
- Score Delta: {verdict.score_delta}
- Vessel Condition: {verdict.vessel_status}
- Underlying Seamanship Rule: {verdict.feedback_rule}

Please provide the concise educational explanation."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.3,
                max_tokens=350,
                timeout=8.0  # Strict timeout to never hang gameplay
            )
            content = response.choices[0].message.content.strip()
            return {
                "explanation": content,
                "language": lang,
                "provider": f"groq:{self.model}"
            }
        except Exception as e:
            logger.warning(f"Groq API call failed or timed out ({e}). Gracefully degrading to fallback.")
            fallback = get_fallback_explanation(scenario.scenario_code, verdict.chosen_option_id, lang)
            return {
                "explanation": fallback,
                "language": lang,
                "provider": "offline_fallback_degraded"
            }
