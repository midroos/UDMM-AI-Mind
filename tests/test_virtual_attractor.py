import pytest
from udmm2.agent.agent import UDMMAgent
from udmm2.envs.natural_env import NaturalEnv

def test_agent_moves_toward_attractor():
    env = NaturalEnv()
    agent = UDMMAgent(env=env)

    # Set attractor far away
    agent.set_attractor(10.0, 0.0, weight=2.0)

    start_state = agent.body.get_state()
    assert start_state["x"] == 0.0

    # Run one step
    agent.step()

    after_state = agent.body.get_state()

    # Agent should have moved in the positive x direction
    assert after_state["x"] > start_state["x"]
    assert after_state["y"] == start_state["y"]

def test_attractor_strength_affects_step_size():
    agent1 = UDMMAgent()
    agent1.set_attractor(10.0, 0.0, weight=0.5) # Weak attractor
    action1 = agent1.select_action()

    agent2 = UDMMAgent()
    agent2.set_attractor(10.0, 0.0, weight=5.0) # Strong attractor
    action2 = agent2.select_action()

    assert action2["step"] > action1["step"]
