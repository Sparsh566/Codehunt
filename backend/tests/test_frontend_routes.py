import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_root_redirect():
    response = client.get("/", follow_redirects=False)
    assert response.status_code in [302, 307]
    assert response.headers["location"] == "/app/index.html"

def test_static_frontend_index():
    response = client.get("/app/index.html")
    assert response.status_code == 200
    assert "Codehunt v2" in response.text
    assert "Learn Mode" in response.text
    assert "Play Mode" in response.text

def test_static_frontend_learn():
    response = client.get("/app/learn.html")
    assert response.status_code == 200
    assert "Learn Mode" in response.text
    assert "Need a hint?" in response.text

def test_static_frontend_play():
    response = client.get("/app/play.html")
    assert response.status_code == 200
    assert "Pirate King" in response.text
    assert "Fisherman" in response.text
    assert "Ship Captain" in response.text

def test_static_frontend_leaderboard():
    response = client.get("/app/leaderboard.html")
    assert response.status_code == 200
    assert "Maritime Honor Roll" in response.text
    assert "Pirate King" in response.text

def test_api_leaderboard():
    response = client.get("/api/leaderboard")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    assert any(d["username"] == "admin" for d in data)
