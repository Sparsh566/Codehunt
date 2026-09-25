import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.session import SessionLocal
from backend.app.models.user import User
from backend.app.models.learner_profile import LearnerProfile
from backend.app.utils.security import hash_password, create_access_token

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def test_user_and_token():
    db = SessionLocal()
    # Unique username for test isolation
    username = "analyticstester"
    user = db.query(User).filter(User.username == username).first()
    if user:
        db.query(LearnerProfile).filter(LearnerProfile.user_id == user.id).delete()
        db.delete(user)
        db.commit()

    user = User(
        username=username,
        email="analytics@example.com",
        hashed_password=hash_password("OceanSafe123!"),
        role="fisherman",
        level=2,
        xp=350,
        current_streak=3
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    profile = LearnerProfile(
        user_id=user.id,
        ocean_conditions_mastery=75.0,
        safety_awareness_mastery=85.0,
        pfz_understanding_mastery=60.0,
        advisory_compliance_mastery=90.0,
        total_decisions=5,
        quiz_attempts=2,
        quiz_high_score=90
    )
    db.add(profile)
    db.commit()

    token = create_access_token({"sub": str(user.id), "username": username})
    user_id = user.id
    db.close()

    yield {"token": token, "username": username, "user_id": user_id}

    # Cleanup
    db = SessionLocal()
    u = db.query(User).filter(User.id == user_id).first()
    if u:
        db.query(LearnerProfile).filter(LearnerProfile.user_id == user_id).delete()
        db.delete(u)
        db.commit()
    db.close()

def test_get_badges_catalog(client):
    response = client.get("/api/analytics/badges")
    assert response.status_code == 200
    badges = response.json()
    assert isinstance(badges, list)
    assert len(badges) >= 6
    badge_ids = [b["id"] for b in badges]
    assert "welcome_sailor" in badge_ids
    assert "quiz_scholar" in badge_ids
    assert "high_wave_guardian" in badge_ids
    assert "pfz_navigator" in badge_ids

def test_get_profile_unauthorized(client):
    response = client.get("/api/analytics/profile")
    assert response.status_code == 401

def test_get_profile_authenticated(client, test_user_and_token):
    token = test_user_and_token["token"]
    response = client.get(
        "/api/analytics/profile",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "analyticstester"
    assert data["level"] == 2
    assert data["xp"] == 350
    assert data["mastery"]["ocean_conditions_mastery"] == 75.0
    assert data["mastery"]["safety_awareness_mastery"] == 85.0
    assert data["mastery"]["pfz_understanding_mastery"] == 60.0
    assert data["mastery"]["advisory_compliance_mastery"] == 90.0
    assert data["mastery"]["overall_literacy_index"] > 0

    # Badges check - since quiz_high_score >= 80, quiz_scholar should be unlocked
    unlocked_ids = [b["id"] for b in data["badges"] if b["is_unlocked"]]
    assert "quiz_scholar" in unlocked_ids
    assert "high_wave_guardian" in unlocked_ids
    assert "pfz_navigator" in unlocked_ids
