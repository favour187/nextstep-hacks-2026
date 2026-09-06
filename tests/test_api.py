"""End-to-end API tests for StepWise (auth -> goal -> check-in -> chat)."""

from __future__ import annotations

from app.core.testing import auth_headers, create_user


def _auth(client) -> dict[str, str]:
    data = create_user(client, email="stepwise@example.com")
    return auth_headers(data["token"])


def test_full_flow(client):
    headers = _auth(client)

    # 1. Create a goal -> deterministic plan
    res = client.post(
        "/api/sustainability/goals",
        headers=headers,
        json={
            "goal_text": "I want to reduce the waste my household produces",
            "weekly_effort_hours": 2.0,
            "weekly_budget_usd": 5.0,
            "horizon_days": 30,
        },
    )
    assert res.status_code == 201, res.text
    goal = res.json()
    assert goal["category"] == "waste"
    assert goal["reframed_goal"]
    assert len(goal["plan"]["chosen"]) >= 4
    assert len(goal["plan"]["milestones"]) >= 3
    assert all(isinstance(f, dict) and "multiplier" in f for f in goal["plan"]["feasibility"])
    assert goal["plan"]["total_impact"]["kg"] > 0 or goal["plan"]["total_impact"]["items"] > 0

    goal_id = goal["id"]

    # 2. List + get
    listing = client.get("/api/sustainability/goals", headers=headers).json()
    assert len(listing["goals"]) == 1
    fetched = client.get(f"/api/sustainability/goals/{goal_id}", headers=headers)
    assert fetched.status_code == 200
    assert fetched.json()["impact"]["kg"] >= 0

    # 3. Check-in with the first two actions
    first_two = [a["action_id"] for a in goal["plan"]["chosen"][:2]]
    res = client.post(
        f"/api/sustainability/goals/{goal_id}/check-ins",
        headers=headers,
        json={"action_ids": first_two, "feeling_score": 4, "notes": "did it!"},
    )
    assert res.status_code == 201, res.text
    after = res.json()
    assert after["streak"] >= 1
    assert after["check_in"]["action_ids"] == first_two

    # 4. Impact is now positive for the logged actions
    fetched = client.get(f"/api/sustainability/goals/{goal_id}", headers=headers).json()
    assert fetched["impact"] == after["impact"]

    # 5. Validation: unknown action → 422; wrong user → 404
    bad = client.post(
        f"/api/sustainability/goals/{goal_id}/check-ins",
        headers=headers,
        json={"action_ids": ["not-real-action"]},
    )
    assert bad.status_code == 422

    other = create_user(client, email="other@example.com")
    foreign = client.get(
        f"/api/sustainability/goals/{goal_id}", headers=auth_headers(other["token"])
    )
    assert foreign.status_code == 404

    # 6. Chat: deterministic local fallback answers
    res = client.post(
        "/api/sustainability/chat",
        headers=headers,
        json={"message": "Explain this plan to me", "goal_id": goal_id},
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["reply"]
    assert body["used_fallback"] is True

    # 7. Auth required
    assert client.get("/api/sustainability/goals").status_code == 401


def test_goal_requires_meaningful_text(client):
    headers = _auth(client)
    res = client.post("/api/sustainability/goals", headers=headers, json={"goal_text": "hi"})
    assert res.status_code == 422
