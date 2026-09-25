import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.db.init_db import init_db
from backend.app.game_engine.schemas import ScenarioDefinition, OceanConditions, ScenarioOption, ConsequenceRule
from backend.app.game_engine.evaluator import evaluate_decision
from backend.app.game_engine.rules import (
    classify_sea_state,
    classify_wind_beaufort,
    check_role_safety_thresholds
)
from backend.app.ocean_adapter import get_ocean_provider

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    init_db()

@pytest.fixture
def fixtures_data():
    fixtures_path = Path(__file__).resolve().parent.parent / "fixtures" / "scenarios.json"
    with open(fixtures_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {s["scenario_code"]: s for s in data}

# =========================================================================
# 1. PURE RULE & CLASSIFICATION TESTS
# =========================================================================

def test_wmo_sea_state_classification():
    assert classify_sea_state(0.05)["code"] == 0
    assert classify_sea_state(0.8)["code"] == 2
    assert classify_sea_state(3.2)["code"] == 4
    assert classify_sea_state(5.5)["code"] == 5

def test_beaufort_scale_classification():
    assert classify_wind_beaufort(0.5)["force"] == 0
    assert classify_wind_beaufort(15.0)["force"] == 4
    assert classify_wind_beaufort(35.0)["force"] == 8
    assert classify_wind_beaufort(52.0)["force"] == 10

def test_role_safety_boundaries():
    # Fisherman: waves > 2.5m should be hazardous
    fish_haz = check_role_safety_thresholds("fisherman", wave_height_m=3.8, wind_speed_knots=30.0, incois_alert_level="ORANGE")
    assert fish_haz["is_inherently_hazardous"] is True
    assert fish_haz["wave_exceeded"] is True

    # Tourism Operator: waves > 1.8m should be hazardous
    tour_haz = check_role_safety_thresholds("tourism_operator", wave_height_m=2.0, wind_speed_knots=15.0, incois_alert_level="YELLOW")
    assert tour_haz["is_inherently_hazardous"] is True

    # Ship Captain: wave = 3.0m in GREEN alert is safe
    capt_safe = check_role_safety_thresholds("ship_captain", wave_height_m=3.0, wind_speed_knots=25.0, incois_alert_level="GREEN")
    assert capt_safe["is_inherently_hazardous"] is False

# =========================================================================
# 2. SCENARIO TESTS (5+ TYPES ACROSS 3 ROLES)
# =========================================================================

def test_scenario_1_fisherman_high_wave_alert(fixtures_data):
    """Role: Fisherman | High Wave Alert in PFZ (Veraval)."""
    raw = fixtures_data["FISH-ARAB-001"]
    scenario = ScenarioDefinition(**raw)

    # Choice 1: Safe Shelter
    v_safe = evaluate_decision(scenario, "opt_fish_shelter")
    assert v_safe.is_safe is True
    assert v_safe.is_optimal is True
    assert v_safe.score_delta > 0
    assert v_safe.vessel_status == "Vessel Secure in Harbor"

    # Choice 2: Reckless Venture into 3.8m waves
    v_unsafe = evaluate_decision(scenario, "opt_fish_venture")
    assert v_unsafe.is_safe is False
    assert v_unsafe.is_optimal is False
    assert v_unsafe.score_delta < 0
    assert "Capsize" in v_unsafe.vessel_status

def test_scenario_2_fisherman_optimal_pfz(fixtures_data):
    """Role: Fisherman | Calm seas with rich thermal PFZ boundary (Ratnagiri)."""
    raw = fixtures_data["FISH-MAHA-002"]
    scenario = ScenarioDefinition(**raw)

    # Choice 1: Navigate to PFZ line
    v_opt = evaluate_decision(scenario, "opt_navigate_pfz")
    assert v_opt.is_safe is True
    assert v_opt.is_optimal is True
    assert v_opt.score_delta == 110
    assert v_opt.xp_awarded == 160

    # Choice 2: Overharvest nursery grounds
    v_destr = evaluate_decision(scenario, "opt_overharvest_juveniles")
    assert v_destr.is_safe is False
    assert v_destr.score_delta < 0

def test_scenario_3_ship_captain_cyclone_diversion(fixtures_data):
    """Role: Ship Captain | Severe Cyclonic Storm track diversion (Paradip)."""
    raw = fixtures_data["CAPT-BOB-003"]
    scenario = ScenarioDefinition(**raw)

    # Choice 1: Storm Track Diversion
    v_div = evaluate_decision(scenario, "opt_divert_south")
    assert v_div.is_safe is True
    assert v_div.is_optimal is True
    assert v_div.score_delta == 120
    assert v_div.vessel_status == "Vessel & Cargo Secure"

    # Choice 2: Pushing ahead through storm center
    v_storm = evaluate_decision(scenario, "opt_push_ahead")
    assert v_storm.is_safe is False
    assert v_storm.score_delta == -150
    assert "Catastrophic" in v_storm.vessel_status

def test_scenario_4_ship_captain_tidal_shallow_channel(fixtures_data):
    """Role: Ship Captain | Shallow Channel Under-Keel Clearance (Gulf of Khambhat)."""
    raw = fixtures_data["CAPT-GUJ-004"]
    scenario = ScenarioDefinition(**raw)

    # Choice 1: Wait for high tide window
    v_tide = evaluate_decision(scenario, "opt_wait_high_tide")
    assert v_tide.is_safe is True
    assert v_tide.is_optimal is True
    assert v_tide.score_delta == 95

    # Choice 2: Grounding risk at low tide
    v_ground = evaluate_decision(scenario, "opt_cross_low_tide")
    assert v_ground.is_safe is False
    assert v_ground.score_delta == -100
    assert "Grounded" in v_ground.vessel_status

def test_scenario_5_pirate_king_rip_current(fixtures_data):
    """Role: Pirate King | Strong Rip Current & Swell Surge (Kovalam)."""
    raw = fixtures_data["PIRATE-KERA-005"]
    scenario = ScenarioDefinition(**raw)

    # Choice 1: Deepwater trench escape
    v_esc = evaluate_decision(scenario, "opt_sail_deep_trench")
    assert v_esc.is_safe is True
    assert v_esc.is_optimal is True
    assert v_esc.score_delta == 115

    # Choice 2: Ramming shallow sandbars
    v_wreck = evaluate_decision(scenario, "opt_beach_breakers")
    assert v_wreck.is_safe is False
    assert v_wreck.score_delta == -120
    assert "Smashed" in v_wreck.vessel_status

def test_scenario_6_pirate_king_coral_pass(fixtures_data):
    """Role: Pirate King | Shallow Coral Garden Navigation (Lakshadweep)."""
    raw = fixtures_data["PIRATE-LAKS-006"]
    scenario = ScenarioDefinition(**raw)

    # Choice 1: Use natural turquoise pass
    v_pass = evaluate_decision(scenario, "opt_use_natural_pass")
    assert v_pass.is_safe is True
    assert v_pass.is_optimal is True

    # Choice 2: Plow through reef
    v_plow = evaluate_decision(scenario, "opt_plow_reef")
    assert v_plow.is_safe is False
    assert v_plow.score_delta == -115

# =========================================================================
# 3. IDEMPOTENCY & OCEAN ADAPTER TESTS
# =========================================================================

def test_evaluator_is_pure_and_idempotent(fixtures_data):
    """Verifies that running evaluate_decision 10 times yields identical verdicts."""
    raw = fixtures_data["FISH-ARAB-001"]
    scenario = ScenarioDefinition(**raw)

    verdicts = [evaluate_decision(scenario, "opt_fish_shelter") for _ in range(10)]
    first = verdicts[0]
    for v in verdicts[1:]:
        assert v.is_safe == first.is_safe
        assert v.score_delta == first.score_delta
        assert v.vessel_status == first.vessel_status
        assert v.feedback_rule == first.feedback_rule

def test_ocean_adapter_telemetry():
    provider = get_ocean_provider()
    stations = provider.list_stations()
    assert len(stations) >= 5

    snapshot = provider.get_latest_telemetry("STN-VERAVAL")
    assert snapshot.station.station_id == "STN-VERAVAL"
    assert snapshot.forecast.significant_wave_height_m == 3.8
    assert snapshot.active_warning is not None
    assert snapshot.active_warning.severity == "ORANGE"
    assert snapshot.pfz_advisory is not None

# =========================================================================
# 4. REST API INTEGRATION TESTS
# =========================================================================

def test_api_list_scenarios():
    resp = client.get("/api/scenarios")
    assert resp.status_code == 200
    scenarios = resp.json()
    assert len(scenarios) >= 6

    # Test filtering by role
    resp_fish = client.get("/api/scenarios?role=fisherman")
    assert resp_fish.status_code == 200
    fish_list = resp_fish.json()
    assert all(s["role"] == "fisherman" for s in fish_list)

def test_api_evaluate_decision():
    payload = {
        "scenario_code": "FISH-ARAB-001",
        "chosen_option_id": "opt_fish_shelter"
    }
    resp = client.post("/api/decisions/evaluate", json=payload)
    assert resp.status_code == 200
    verdict = resp.json()
    assert verdict["is_safe"] is True
    assert verdict["is_optimal"] is True
    assert verdict["score_delta"] == 100
    assert "Secure in Harbor" in verdict["vessel_status"]
