import pytest
from udmm2.agent.agent import UDMMAgent

def test_agent_uses_semantic_memory_for_expectations():
    agent = UDMMAgent(name="SemanticAgent", reference_state={"goal": "stable"})
    agent.semantic_memory.add_concept_simple("tree", {"type": "plant"}, ["leaf", "branch"])

    inputs = {"object": "tree"}
    action_result = {"object": "tree"}

    result = agent.step(inputs, action_result)

    assert "expectations" in result
    assert "object_related" in result["expectations"]
    assert "leaf" in result["expectations"]["object_related"]
    assert "branch" in result["expectations"]["object_related"]
