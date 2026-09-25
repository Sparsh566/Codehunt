import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.init_db import init_db
from backend.app.ai_service.groq_explainer import GroqExplainer
from backend.app.ai_service.tavily_retriever import TavilyRetriever
from backend.app.game_engine.schemas import ScenarioDefinition, OceanConditions, ScenarioOption, ConsequenceRule
from backend.app.game_engine.evaluator import evaluate_decision

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    init_db()

@pytest.fixture
def sample_scenario():
    return ScenarioDefinition(
        scenario_code="FISH-ARAB-001",
        role="fisherman",
        title="High Wave Alert in Potential Fishing Zone (PFZ)",
        location="Veraval Offshore, Arabian Sea",
        narrative="Orange alert with 3.8m waves and active PFZ.",
        ocean_data=OceanConditions(
            wave_height_m=3.8,
            wind_speed_knots=34.0,
            swell_period_sec=14.2,
            sea_surface_temp_c=28.4,
            pfz_zone_active=True,
            incois_warning_type="high_wave",
            incois_alert_level="ORANGE"
        ),
        options=[
            ScenarioOption(id="opt_fish_shelter", text="Wait in harbor", action_type="safe_shelter"),
            ScenarioOption(id="opt_fish_venture", text="Venture to PFZ", action_type="reckless")
        ],
        recommended_action_id="opt_fish_shelter",
        consequences={
            "opt_fish_shelter": ConsequenceRule(
                is_safe=True,
                score_delta=100,
                vessel_status="Vessel Secure in Harbor",
                xp_awarded=150,
                feedback_rule="Obeying INCOIS Orange Alert saved vessel and crew."
            ),
            "opt_fish_venture": ConsequenceRule(
                is_safe=False,
                score_delta=-120,
                vessel_status="Severe Capsize Risk",
                xp_awarded=15,
                feedback_rule="Small fishing crafts capsize in >3.5m waves."
            )
        }
    )

def test_api_explain_endpoint_english():
    payload = {
        "scenario_code": "FISH-ARAB-001",
        "chosen_option_id": "opt_fish_shelter",
        "language": "en"
    }
    resp = client.post("/api/decisions/explain", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["scenario_code"] == "FISH-ARAB-001"
    assert data["language"] == "en"
    assert len(data["explanation"]) > 30
    assert "provider" in data

def test_api_explain_endpoint_hindi():
    payload = {
        "scenario_code": "FISH-ARAB-001",
        "chosen_option_id": "opt_fish_shelter",
        "language": "hi"
    }
    resp = client.post("/api/decisions/explain", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["language"] == "hi"
    assert len(data["explanation"]) > 20

def test_api_learn_more_authoritative():
    resp = client.get("/api/decisions/learn-more?scenario_code=FISH-ARAB-001")
    assert resp.status_code == 200
    data = resp.json()
    assert data["scenario_code"] == "FISH-ARAB-001"
    assert len(data["results"]) >= 1
    # Check that returned resources come from authoritative ocean domains
    assert any(
        any(domain in r["url"] or domain in r["source"] for domain in ["incois", "moes", "imd", "oceandecade"])
        for r in data["results"]
    )

def test_groq_fallback_when_offline(sample_scenario):
    verdict = evaluate_decision(sample_scenario, "opt_fish_shelter")
    # Explainer with dummy/invalid key should gracefully fallback with zero exceptions
    offline_explainer = GroqExplainer(api_key="gsk_invalid_test_key_dummy_12345")
    res = offline_explainer.generate_explanation(
        scenario=sample_scenario,
        verdict=verdict,
        chosen_option_text="Wait in harbor",
        language="en"
    )
    assert res is not None
    assert "explanation" in res
    assert len(res["explanation"]) > 30
    assert "fallback" in res["provider"]

def test_tavily_fallback_when_offline():
    offline_retriever = TavilyRetriever(api_key="tvly-invalid-dummy-key")
    res = offline_retriever.search_authoritative(
        query="High wave alerts",
        topic="high_wave",
        max_results=2
    )
    assert res is not None
    assert len(res["results"]) >= 1
    assert "incois" in res["results"][0]["url"]
