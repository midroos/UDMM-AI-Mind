import pytest
from udmm2.agent.agent import UDMMAgent
from udmm2.envs.natural_env import NaturalEnv
from udmm2.goals.attractor import AttractorModel

def test_hierarchical_subgoals_generation():
    """Test that subgoals are generated correctly."""
    agent = UDMMAgent()
    attractor = AttractorModel(target_x=4.0, target_y=0.0)
    agent.set_hierarchical_attractor(attractor, n_steps=4)

    assert agent.hierarchical_intent is not None
    subgoals = agent.hierarchical_intent.subgoals
    assert len(subgoals) == 4
    # The first subgoal should be at x=1.0
    assert subgoals[0].target_x == pytest.approx(1.0)
    # The last subgoal should be at the attractor's location
    assert subgoals[3].target_x == pytest.approx(4.0)

def test_agent_follows_subgoals():
    """Test that the agent follows and completes a sequence of subgoals."""
    agent = UDMMAgent()
    attractor = AttractorModel(target_x=2.0, target_y=0.0)
    agent.set_hierarchical_attractor(attractor, n_steps=2) # Two subgoals: at x=1 and x=2

    # Run enough steps to complete the first subgoal
    for _ in range(20):
        agent.step()
        if agent.hierarchical_intent.current_index == 1:
            break

    assert agent.hierarchical_intent.subgoals[0].completed is True
    assert agent.hierarchical_intent.current_index == 1

    # Run more steps to complete the final subgoal
    for _ in range(20):
        agent.step()
        if agent.hierarchical_intent.current_subgoal() is None:
            break

    assert agent.hierarchical_intent.subgoals[1].completed is True
    assert agent.hierarchical_intent.current_subgoal() is None
