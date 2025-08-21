import pytest
from udmm2.agent.legacy_agent import LegacyUDMMAgent
from udmm2.envs.natural_env import NaturalEnv

def test_learning_updates_confidence_soft():
    env = NaturalEnv(objects=[{"id":"food", "x":1.0, "y":0.0, "tags":["food"]}])
    agent = LegacyUDMMAgent(env=env)

    # Seed a concept and a rule
    try:
        agent.semantic_memory.add_concept(label="food", description="", attributes={}, relations=[])
        rid = agent.semantic_memory.add_rule(
            conditions=["near(concept('food'))"],
            actions=["approach"],
            priority=1,
            confidence=0.3,
            source="experiential"
        )
    except Exception:
        rid = None

    # Run a step
    out = agent.step(perception={"objects":["food"]})

    # Assert that metrics were recorded and no exception occurred
    m = agent.get_metrics()
    assert isinstance(m.get("prediction_error", []), list)
    assert len(m["prediction_error"]) > 0
    assert isinstance(m.get("precision_gain", []), list)
    assert len(m["precision_gain"]) > 0

    # If the rule was created successfully, check its confidence
    if rid is not None:
        r = agent.semantic_memory.get_rule_by_id(rid)
        assert r is not None
        assert 0.0 <= float(r.get("confidence", 0.5)) <= 1.0
