from typing import List, Dict, Optional
from uuid import UUID

from udmm2.memory.models import Episode

class EpisodicMemory:
    """
    Stores and retrieves agent experiences (episodes) over time.
    """
    def __init__(self):
        self.episodes: Dict[UUID, Episode] = {}

    def add_episode(self, **kwargs) -> UUID:
        """
        Creates and stores a new episode from keyword arguments.
        """
        episode = Episode(**kwargs)
        self.episodes[episode.id] = episode
        return episode.id

    def get_episode(self, episode_id: UUID) -> Optional[Episode]:
        return self.episodes.get(episode_id)

    def list_episodes(self, limit: int = 50) -> List[Episode]:
        sorted_episodes = sorted(self.episodes.values(), key=lambda ep: ep.timestamp, reverse=True)
        return sorted_episodes[:limit]
