import pytest
from udmm2.agent.agent import UDMMAgent
from udmm2.envs.natural_env import NaturalEnv

def test_embodied_cycle_moves_agent():
    env = NaturalEnv(objects=[{"id": "fruit1", "x": 0.6, "y": 0.0, "tags": ["food"]}])
    agent = UDMMAgent(env=env)

    # Get initial state
    before_state = agent.body.get_state()
    assert before_state["x"] == 0.0

    # Run one step
    output = agent.step(perception={"objects": ["rock"]})

    # Get state after
    after_state = agent.body.get_state()

    # Assertions
    assert "result" in output
    assert "action" in output
    assert output["action"]["type"] == "move_forward"

    # Agent should have moved
    assert after_state["x"] > before_state["x"]

    # Energy should be within bounds
    assert 0.0 <= agent.body.energy <= 1.0

def test_agent_senses_environment():
    # Place an object right in front of the agent
    env = NaturalEnv(objects=[{"id": "fruit1", "x": 0.5, "y": 0.0, "tags": ["food"]}])
    agent = UDMMAgent(env=env)

    # The action result will contain the environment feedback
    result = agent.apply_action({"type": "move_forward", "step": 0.1})

    assert "env_feedback" in result
    feedback = result["env_feedback"]
    assert "nearby" in feedback
    assert len(feedback["nearby"]) == 1
    assert feedback["nearby"][0]["id"] == "fruit1"
