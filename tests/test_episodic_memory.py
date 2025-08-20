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
    """Test that an episode can be added and retrieved."""
    episode = Episode(
        context="test_env",
        perception={"state": "initial"},
        action="do_something",
        result={"state": "final"},
        body_before={},
        body_after={},
        emotion_signal=0.1
    )
    eid = em.add_episode(episode)
    fetched = em.get_episode(eid)
    assert fetched is not None
    assert fetched.action == "do_something"
    assert fetched.id == eid

def test_query_by_context(em: EpisodicMemory):
    """Test querying episodes by their context."""
    ep1 = Episode(context="NaturalEnv", perception={}, action="a1", result={}, body_before={}, body_after={}, emotion_signal=0.2)
    ep2 = Episode(context="TrapEnv", perception={}, action="a2", result={}, body_before={}, body_after={}, emotion_signal=0.3)
    em.add_episode(ep1)
    em.add_episode(ep2)

    result = em.query_by_context("NaturalEnv")
    assert len(result) == 1
    assert result[0].action == "a1"

def test_query_by_time_range(em: EpisodicMemory):
    """Test querying episodes by a time range."""
    now = datetime.now(timezone.utc)

    past_episode = Episode(context="time_test", perception={}, action="past_action", result={}, body_before={}, body_after={}, emotion_signal=0.4)
    past_episode.timestamp = now - timedelta(days=2)
    em.add_episode(past_episode)

    recent_episode = Episode(context="time_test", perception={}, action="recent_action", result={}, body_before={}, body_after={}, emotion_signal=0.5)
    em.add_episode(recent_episode)

    start = now - timedelta(days=1)
    end = now + timedelta(days=1)
    result = em.query_by_time_range(start, end)

    assert len(result) == 1
    assert result[0].action == "recent_action"
