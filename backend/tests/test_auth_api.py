import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.init_db import init_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    init_db()

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["groq_configured"] is True
    assert data["tavily_configured"] is True

import uuid

def test_user_registration_and_login():
    # Register unique user
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"diver_{unique_suffix}"
    reg_payload = {
        "username": username,
        "password": "diverpassword123",
        "email": f"{username}@ocean.org",
        "role": "tourism_operator"
    }
    reg_resp = client.post("/api/auth/register", json=reg_payload)
    assert reg_resp.status_code == 200
    reg_data = reg_resp.json()
    assert "access_token" in reg_data
    assert reg_data["user"]["username"] == username
    assert reg_data["user"]["role"] == "tourism_operator"

    # Login with credentials
    login_payload = {
        "username": username,
        "password": "diverpassword123"
    }
    login_resp = client.post("/api/auth/login", json=login_payload)
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    token = login_data["access_token"]
    assert token

    # Check /me with Bearer token
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = client.get("/api/auth/me", headers=headers)
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["username"] == username

def test_get_learn_questions_and_submission():
    # Fetch questions
    q_resp = client.get("/api/learn/questions")
    assert q_resp.status_code == 200
    questions = q_resp.json()
    assert len(questions) == 10
    assert any("percentage of Earth's surface" in q["question"] for q in questions)
    
    # Test submission
    first_q = questions[0]
    submit_payload = {
        "answers": [
            {
                "question_id": first_q["id"],
                "selected_option": "70%"
            }
        ]
    }
    sub_resp = client.post("/api/learn/submit", json=submit_payload)
    assert sub_resp.status_code == 200
    sub_data = sub_resp.json()
    assert sub_data["total_score"] == 10
    assert sub_data["accuracy_percentage"] == 100
    assert len(sub_data["results"]) == 1
    assert sub_data["results"][0]["is_correct"] is True
