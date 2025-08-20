import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from udmm2.memory.episodic_memory import EpisodicMemory
from udmm2.memory.models import Episode

@pytest.fixture
def em():
    """Provides a clean EpisodicMemory instance for each test."""
    return EpisodicMemory()

def test_add_and_get_episode(em: EpisodicMemory):
    episode = Episode(description="Agent explored forest", context="NaturalEnv")
    eid = em.add_episode(episode)
    fetched = em.get_episode(eid)
    assert fetched is not None
    assert fetched.description == "Agent explored forest"
    assert fetched.id == eid

def test_query_by_context(em: EpisodicMemory):
    ep1 = Episode(description="Event 1", context="NaturalEnv")
    ep2 = Episode(description="Event 2", context="TrapEnv")
    em.add_episode(ep1)
    em.add_episode(ep2)

    result = em.query_by_context("NaturalEnv")
    assert len(result) == 1
    assert result[0].description == "Event 1"

def test_query_by_time_range(em: EpisodicMemory):
    now = datetime.now(timezone.utc)

    past_episode = Episode(description="Past Event", context="NaturalEnv")
    past_episode.timestamp = now - timedelta(days=2)
    em.add_episode(past_episode)

    recent_episode = Episode(description="Recent Event", context="NaturalEnv")
    em.add_episode(recent_episode)

    start = now - timedelta(days=1)
    end = now + timedelta(days=1)
    result = em.query_by_time_range(start, end)

    assert len(result) == 1
    assert result[0].description == "Recent Event"

def test_query_by_concept(em: EpisodicMemory):
    concept_id = uuid4()
    linked_episode = Episode(
        description="Linked Event",
        context="NaturalEnv",
        linked_concepts=[concept_id]
    )
    unlinked_episode = Episode(
        description="Unlinked Event",
        context="NaturalEnv"
    )
    em.add_episode(linked_episode)
    em.add_episode(unlinked_episode)

    result = em.query_by_concept(concept_id)
    assert len(result) == 1
    assert result[0].description == "Linked Event"
