import pytest
from udmm2.agent.agent import UDMMAgent

def test_agent_semantic_and_embodied_cycle():
    # Setup: Create a low-discrepancy state to prioritize exploration
    agent = UDMMAgent(name="EmbodiedSemanticAgent", reference_state={"object": "tree"})
    agent.semantic_memory.add_concept_simple("tree", {"type": "plant"}, ["leaf", "branch"])

    initial_body_state = agent.body.get_state()

    inputs = {"object": "tree"}
    action_result = {"status": "explored"}

    # Action
    result = agent.step(inputs, action_result)

    # Assertions for semantics
    assert "expectations" in result
    assert "object_related" in result["expectations"]
    assert "leaf" in result["expectations"]["object_related"]

    # Assertions for embodiment
    assert "emotion_signal" in result
    assert result["emotion_signal"] > 0
    assert "Explore" in result["selected_action"]

    final_body_state = agent.body.get_state()
    assert initial_body_state != final_body_state

    # Check the episode log
    # Assuming the latest episode is the one just created
    last_episode = list(agent.episodic_memory.episodes.values())[-1]
    assert last_episode.body_before == initial_body_state
    assert last_episode.body_after == final_body_state
    assert last_episode.emotion_signal == result["emotion_signal"]
