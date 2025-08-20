import pytest
from udmm2.agent.agent import UDMMAgent
from udmm2.envs.natural_env import NaturalEnv

def test_prediction_error_triggers_learning():
    env = NaturalEnv(objects=[{"id":"food", "x":1.0, "y":0.0, "tags":["food"]}])
    agent = UDMMAgent(env=env)

    # Ensure semantic_memory has a rule linked to 'food' label
    # First, create the concept 'food' so the rule can link to it.
    agent.semantic_memory.add_concept(label="food", description="Edible item", attributes={}, relations=[])
    rid = agent.semantic_memory.add_rule(
        conditions=["near(concept('food'))"],
        actions=["approach"],
        priority=1,
        confidence=0.3,
        source="experiential"
    )

    # Get initial confidence
    initial_rule = agent.semantic_memory.get_rule_by_id(rid)
    initial_confidence = initial_rule["confidence"]

    # The agent starts at (0,0). Its first step will move it to (0.5, 0).
    # Its prediction will be that it doesn't move. This creates a prediction error.
    # A small prediction error should increase confidence in the rule.
    out1 = agent.step(perception={"sensed": "food"})

    # After the step, update_model will have run and adjusted the rule confidence
    final_rule = agent.semantic_memory.get_rule_by_id(rid)
    final_confidence = final_rule["confidence"]

    assert 0.0 <= final_confidence <= 1.0
    # Because the prediction error is small (agent moved as expected), confidence should increase
    assert final_confidence > initial_confidence
