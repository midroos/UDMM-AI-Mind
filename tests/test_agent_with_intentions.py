import pytest
from udmm2.agent.agent import UDMMAgent


def test_agent_generates_intentions_and_updates_model():
    agent = UDMMAgent(name="TestAgent", reference_state={"goal": "stable"})
    inputs = {"goal": "unstable"}
    action_result = {"goal": "unstable"}

    result = agent.step(inputs, action_result)

    assert "discrepancy" in result
    assert result["discrepancy"] == 1.0
    assert len(result["intentions"]) > 0
    assert result["selected_action"] in [i["description"] for i in result["intentions"]]

def test_agent_low_discrepancy():
    agent = UDMMAgent(name="TestAgent", reference_state={"goal": "stable"})
    inputs = {"goal": "stable"}
    action_result = {"goal": "stable"}

    result = agent.step(inputs, action_result)
    assert result["discrepancy"] == 0.0
    # Should still generate a low-priority environmental action
    assert len(result["intentions"]) == 1
    assert result["intentions"][0]["type"] == "environmental_action"
