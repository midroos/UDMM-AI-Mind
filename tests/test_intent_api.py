import pytest
from fastapi.testclient import TestClient
from udmm2.api.app import app

client = TestClient(app)

def test_goal_crud_and_agent_step():
    # 1. Create a goal
    g_in = {
        "label": "Explore & Learn",
        "kind": "exploratory",
        "priority": 2,
        "constraints": {"risk_max": 0.6},
        "target_state": {"activation_min": 0.5},
        "horizon_steps": 3
    }
    g_out = client.post("/intent/goals", json=g_in).json()
    assert "id" in g_out
    assert g_out["label"] == "Explore & Learn"
    goal_id = g_out["id"]

    # 2. List goals to ensure it's there
    goals = client.get("/intent/goals").json()
    assert len(goals) > 0
    assert goals[0]["id"] == goal_id

    # 3. Run a step with a simple perception
    step_in = {
        "objects": ["tree", "rock"], "signals": {"novelty": 0.3}
    }
    step_out = client.post("/intent/agent/step", json=step_in).json()
    assert "action" in step_out and "precision" in step_out
    assert "body_before" in step_out and "body_after" in step_out
    assert step_out["precision"]["precision_gain"] >= 1.0

    # 4. Delete the goal
    del_res = client.delete(f"/intent/goals/{goal_id}").json()
    assert del_res["ok"] is True

    # 5. Verify goal is deleted
    goals_after_del = client.get("/intent/goals").json()
    assert len(goals_after_del) == 0
