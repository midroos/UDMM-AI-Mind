import pytest
from udmm2.memory.semantic_memory import SemanticMemory
from udmm2.memory.models import Concept, Rule, SemanticLink

@pytest.fixture
def mem():
    """Provides an empty SemanticMemory instance for each test."""
    return SemanticMemory()

def test_add_concept(mem: SemanticMemory):
    """Test adding a concept to the memory."""
    c1 = Concept(id="c1", label="water", description="A clear liquid.")
    mem.add_concept(c1)
    assert mem.graph.has_node("c1")
    retrieved = mem.get_node_data("c1")
    assert retrieved == c1
    assert mem.graph.nodes["c1"]["type"] == "concept"

def test_add_rule(mem: SemanticMemory):
    """Test adding a rule to the memory."""
    r1 = Rule(id="r1", if_=["thirsty"], then=["drink_water"])
    mem.add_rule(r1)
    assert mem.graph.has_node("r1")
    retrieved = mem.get_node_data("r1")
    assert retrieved == r1
    assert mem.graph.nodes["r1"]["type"] == "rule"

def test_link_nodes(mem: SemanticMemory):
    """Test linking two nodes with a weighted, typed edge."""
    c1 = Concept(id="c1", label="water")
    c2 = Concept(id="c2", label="thirst")
    mem.add_concept(c1)
    mem.add_concept(c2)

    link = SemanticLink(source="c2", target="c1", type="satisfies", weight=0.9)
    mem.link_nodes(link)

    assert mem.graph.has_edge("c2", "c1")
    edge_data = mem.graph.get_edge_data("c2", "c1")
    assert edge_data["type"] == "satisfies"
    assert edge_data["weight"] == 0.9

def test_query_related_nodes(mem: SemanticMemory):
    """Test querying for related nodes."""
    c1 = Concept(id="c1", label="hot_surface")
    r1 = Rule(id="r1", if_=["is_hot"], then=["avoid_touch"])
    c2 = Concept(id="c2", label="danger")
    mem.add_concept(c1)
    mem.add_rule(r1)
    mem.add_concept(c2)

    mem.link_nodes(SemanticLink(source="c1", target=r1.id, type="triggers", weight=1.0))
    mem.link_nodes(SemanticLink(source="c1", target=c2.id, type="implies", weight=0.8))

    # Query all related nodes
    related = mem.query_related("c1")
    assert len(related) == 2
    # The order is not guaranteed
    assert ("r1", 1.0) in related
    assert ("c2", 0.8) in related

    # Query with a specific relation type
    related_implies = mem.query_related("c1", relation_type="implies")
    assert related_implies == [("c2", 0.8)]

    related_triggers = mem.query_related("c1", relation_type="triggers")
    assert related_triggers == [("r1", 1.0)]

def test_query_non_existent_node(mem: SemanticMemory):
    """Test querying a node that does not exist returns an empty list."""
    related = mem.query_related("non_existent_id")
    assert related == []
