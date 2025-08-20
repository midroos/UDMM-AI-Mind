from typing import List, Dict, Optional
from datetime import datetime
from uuid import UUID

from udmm2.memory.models import Episode

class EpisodicMemory:
    """
    Stores and retrieves agent experiences (episodes) over time.
    """

    def __init__(self):
        """Initializes the episodic memory store."""
        self.episodes: Dict[UUID, Episode] = {}

    def add_episode(
        self,
        description: str,
        context: str,
        linked_concepts: Optional[List[UUID]] = None,
    ) -> UUID:
        """
        Creates and stores a new episode.

        Args:
            description: A textual description of the event.
            context: The environment or situation context.
            linked_concepts: A list of concept UUIDs related to this episode.

        Returns:
            The unique ID of the newly created episode.
        """
        episode = Episode(
            description=description,
            context=context,
            linked_concepts=linked_concepts or [],
        )
        self.episodes[episode.id] = episode
        return episode.id

    def get_episode(self, episode_id: UUID) -> Optional[Episode]:
        """
        Retrieves a single episode by its unique ID.

        Args:
            episode_id: The ID of the episode to retrieve.

        Returns:
            The Episode object, or None if not found.
        """
        return self.episodes.get(episode_id)

    def query_by_context(self, context: str) -> List[Episode]:
        """
        Finds all episodes that occurred in a specific context.

        Args:
            context: The context to search for.

        Returns:
            A list of matching Episode objects.
        """
        return [ep for ep in self.episodes.values() if ep.context == context]

    def query_by_time_range(self, start_time: datetime, end_time: datetime) -> List[Episode]:
        """
        Finds all episodes within a given time range.

        Args:
            start_time: The start of the time window.
            end_time: The end of the time window.

        Returns:
            A list of matching Episode objects.
        """
        return [
            ep
            for ep in self.episodes.values()
            if start_time <= ep.timestamp <= end_time
        ]

    def query_by_concept(self, concept_id: UUID) -> List[Episode]:
        """
        Finds all episodes linked to a specific concept.

        Args:
            concept_id: The concept UUID to search for.

        Returns:
            A list of matching Episode objects.
        """
        return [
            ep
            for ep in self.episodes.values()
            if concept_id in ep.linked_concepts
        ]
