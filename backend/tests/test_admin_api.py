import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.session import SessionLocal
from backend.app.models.user import User
from backend.app.models.scenario import ScenarioRecord
from backend.app.utils.security import hash_password, create_access_token

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def admin_user_and_token():
    db = SessionLocal()
    username = "testadminkey"
    user = db.query(User).filter(User.username == username).first()
    if user:
        db.delete(user)
        db.commit()

    user = User(
        username=username,
        email="testadmin@incois.gov.in",
        hashed_password=hash_password("adminSecret123!"),
        role="admin",
        is_admin=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id), "username": username})
    user_id = user.id
    db.close()

    yield {"token": token, "username": username, "user_id": user_id}

    db = SessionLocal()
    u = db.query(User).filter(User.id == user_id).first()
    if u:
        db.delete(u)
        db.commit()
    db.close()

@pytest.fixture
def regular_user_and_token():
    db = SessionLocal()
    username = "regularsailor"
    user = db.query(User).filter(User.username == username).first()
    if user:
        db.delete(user)
        db.commit()

    user = User(
        username=username,
        email="sailor@example.com",
        hashed_password=hash_password("sailor123!"),
        role="fisherman",
        is_admin=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id), "username": username})
    user_id = user.id
    db.close()

    yield {"token": token, "username": username, "user_id": user_id}

    db = SessionLocal()
    u = db.query(User).filter(User.id == user_id).first()
    if u:
        db.delete(u)
        db.commit()
    db.close()

def test_admin_stats_unauthorized(client):
    response = client.get("/api/admin/stats")
    assert response.status_code == 401

def test_admin_stats_forbidden_for_regular_user(client, regular_user_and_token):
    token = regular_user_and_token["token"]
    response = client.get(
        "/api/admin/stats",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403

def test_admin_stats_success(client, admin_user_and_token):
    token = admin_user_and_token["token"]
    response = client.get(
        "/api/admin/stats",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_users" in data
    assert "total_decisions" in data
    assert "safety_rate_pct" in data
    assert "active_scenarios_count" in data
    assert "role_distribution" in data
    assert "scenario_risk_analysis" in data

def test_admin_scenario_lifecycle(client, admin_user_and_token):
    token = admin_user_and_token["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. List scenarios
    list_resp = client.get("/api/admin/scenarios", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 6

    # 2. Create dynamic scenario
    payload = {
        "scenario_code": "TEST-ADMIN-001",
        "role": "fisherman",
        "title": "Admin Created Test Reef Scenario",
        "location": "Lakshadweep Atoll Test Zone",
        "narrative": "Testing dynamic scenario authoring from Admin Operations Console.",
        "wave_height_m": 2.2,
        "wind_speed_knots": 14.0,
        "swell_period_sec": 9.0,
        "sea_surface_temp_c": 29.0,
        "pfz_zone_active": True,
        "incois_warning_type": "none",
        "incois_alert_level": "GREEN",
        "options": [
            {"id": "test_opt_1", "text": "Deploy nets in designated PFZ channel", "risk_level": "low", "fuel_cost": 10, "catch_potential": "High"},
            {"id": "test_opt_2", "text": "Anchor on shallow fragile live coral", "risk_level": "extreme", "fuel_cost": 5, "catch_potential": "Reef Hazard"}
        ],
        "recommended_action_id": "test_opt_1",
        "consequences": {
            "test_opt_1": {"is_safe": True, "score_delta": 100, "vessel_status": "Intact", "rule_feedback": "Sustainable coral channel usage compliant with INCOIS advisory."},
            "test_opt_2": {"is_safe": False, "score_delta": -120, "vessel_status": "Damaged Hull", "rule_feedback": "Severe violation of marine ecosystem and vessel grounding hazard."}
        },
        "is_active": True
    }

    create_resp = client.post("/api/admin/scenarios", json=payload, headers=headers)
    assert create_resp.status_code == 200
    created = create_resp.json()
    assert created["scenario_code"] == "TEST-ADMIN-001"
    scenario_id = created["id"]

    # 3. Toggle scenario active
    toggle_resp = client.post(f"/api/admin/scenarios/{scenario_id}/toggle", headers=headers)
    assert toggle_resp.status_code == 200
    assert "active status is now False" in toggle_resp.json()["message"]

    # 4. Soft-delete / Archive
    delete_resp = client.delete(f"/api/admin/scenarios/{scenario_id}", headers=headers)
    assert delete_resp.status_code == 200
    assert "archived successfully" in delete_resp.json()["message"]

    # Cleanup DB record
    db = SessionLocal()
    sc = db.query(ScenarioRecord).filter(ScenarioRecord.scenario_code == "TEST-ADMIN-001").first()
    if sc:
        db.delete(sc)
        db.commit()
    db.close()
