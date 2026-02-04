import uuid

from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def unique_email():
    return f"testuser+{uuid.uuid4().hex}@example.com"


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # Basic sanity checks
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Basketball Team" in data


def test_signup_unregister_flow():
    activity = "Basketball Team"
    email = unique_email()

    # Ensure email not already present
    resp0 = client.get("/activities")
    assert resp0.status_code == 200
    assert email not in resp0.json()[activity]["participants"]

    # Sign up
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # Verify participant is now present
    resp2 = client.get("/activities")
    assert resp2.status_code == 200
    participants = resp2.json()[activity]["participants"]
    assert email in participants

    # Duplicate signup should fail
    resp_dup = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp_dup.status_code == 400

    # Unregister
    resp3 = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp3.status_code == 200
    assert "Unregistered" in resp3.json().get("message", "")

    # Verify participant removed
    resp4 = client.get("/activities")
    assert resp4.status_code == 200
    assert email not in resp4.json()[activity]["participants"]

    # Unregistering again should return 404
    resp5 = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp5.status_code == 404


def test_unregister_nonexistent_activity():
    resp = client.delete("/activities/Nonexistent%20Club/participants?email=noone@example.com")
    assert resp.status_code == 404
