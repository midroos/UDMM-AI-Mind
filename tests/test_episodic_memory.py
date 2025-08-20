import pytest
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4
from udmm2.memory.episodic_memory import EpisodicMemory
from udmm2.memory.models import Episode

@pytest.fixture
def em():
    """Provides a clean EpisodicMemory instance for each test."""
    return EpisodicMemory()

def test_add_and_get_episode(em: EpisodicMemory):
    """Test that an episode can be added and retrieved."""
    eid = em.add_episode(
        description="test",
        context="test_env",
        perception={"state": "initial"},
        action="do_something",
        result={"state": "final"}
    )
    fetched = em.get_episode(eid)
    assert fetched is not None
    assert fetched.action == "do_something"
    assert fetched.id == eid

def test_list_episodes(em: EpisodicMemory):
    """Test listing episodes."""
    em.add_episode(description="ep1", context="NaturalEnv")
    em.add_episode(description="ep2", context="TrapEnv")

    result = em.list_episodes()
    assert len(result) == 2
    # Check that they are sorted by timestamp (most recent first)
    assert result[0].description == "ep2"
