import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from udmm2.memory.episodic_memory import EpisodicMemory

def test_add_and_get_episode():
    em = EpisodicMemory()
    eid = em.add_episode(description="Agent explored forest", context="NaturalEnv")
    fetched = em.get_episode(eid)
    assert fetched.description == "Agent explored forest"

def test_query_by_context():
    em = EpisodicMemory()
    em.add_episode("Event 1", "NaturalEnv")
    em.add_episode("Event 2", "TrapEnv")
    result = em.query_by_context("NaturalEnv")
    assert len(result) == 1
    assert result[0].description == "Event 1"

def test_query_by_time_range():
    em = EpisodicMemory()
    # Use timezone-aware datetimes to avoid DeprecationWarning
    now = datetime.now(timezone.utc)

    # Manually create and add an episode to control its timestamp
    past_episode = em.episodes[em.add_episode("Past Event", "NaturalEnv")]
    past_episode.timestamp = now - timedelta(days=2)

    em.add_episode("Recent Event", "NaturalEnv")

    start = now - timedelta(days=1)
    end = now + timedelta(days=1)
    result = em.query_by_time_range(start, end)
    assert len(result) == 1
    assert result[0].description == "Recent Event"

def test_query_by_concept():
    em = EpisodicMemory()
    concept_id = uuid4()
    em.add_episode("Linked Event", "NaturalEnv", linked_concepts=[concept_id])
    em.add_episode("Unlinked Event", "NaturalEnv")
    result = em.query_by_concept(concept_id)
    assert len(result) == 1
    assert result[0].description == "Linked Event"
