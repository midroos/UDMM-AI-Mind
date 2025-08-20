import pytest
from uuid import UUID
from udmm2.memory.semantic_memory import SemanticMemory

@pytest.fixture
def mem():
    """Provides a clean SemanticMemory instance."""
    return SemanticMemory()

def test_add_and_get_concept(mem: SemanticMemory):
    """Test adding a concept and retrieving it."""
    cid = mem.add_concept(label="water", description="A clear liquid.", attributes={}, relations=[])
    assert isinstance(cid, UUID)

    concept_out = mem.get_concept_by_id(cid)
    assert concept_out is not None
    assert concept_out["label"] == "water"

def test_add_and_get_rule(mem: SemanticMemory):
    """Test adding a rule and retrieving it."""
    rid = mem.add_rule(conditions=["thirsty"], actions=["drink"], priority=1, confidence=0.9, source="experiential")
    assert isinstance(rid, UUID)

    rule_out = mem.get_rule_by_id(rid)
    assert rule_out is not None
    assert rule_out["actions"] == ["drink"]

def test_concept_linking_and_relations(mem: SemanticMemory):
    """Test linking concepts and querying relations."""
    cid1 = mem.add_concept(label="water", description="", attributes={}, relations=[])
    relation = [{"target_id": str(cid1), "relation": "is_a"}]
    cid2 = mem.add_concept(label="liquid", description="", attributes={}, relations=relation)

    # Test get_related
    related_labels = mem.get_related("liquid")
    assert "water" in related_labels

    # Test query_related (by ID)
    related_nodes = mem.query_related(cid2)
    assert len(related_nodes) == 1
    assert related_nodes[0][0] == cid1

def test_rule_to_concept_linking(mem: SemanticMemory):
    """Test that rules are automatically linked to concepts in their conditions."""
    cid = mem.add_concept(label="Heat", description="", attributes={}, relations=[])
    rid = mem.add_rule(conditions=["concept('Heat').is_present"], actions=["avoid"], priority=1, confidence=0.9, source="synthetic")

    related_rules = mem.rules_related_to_concept(cid)
    assert len(related_rules) == 1
    assert related_rules[0] == rid
