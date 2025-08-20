from typing import Any, Dict, List
from uuid import uuid4
from datetime import datetime, timezone

from .working_memory import WorkingMemory, WMItem
from ..memory.episodic_memory import EpisodicMemory
from ..memory.semantic_memory import SemanticMemory
from ..memory.models import Episode
from .goal_manager import GoalManager, Intention


class UDMMAgent:
    def __init__(self, name: str, reference_state: Dict):
        self.name = name
        self.working_memory = WorkingMemory()
        self.episodic_memory = EpisodicMemory()
        self.goal_manager = GoalManager(reference_state)
        self.semantic_memory = SemanticMemory()
        self.current_state = {}  # Simplified representation of agent state

    def perceive(self, inputs: Dict):
        # Update current state and working memory
        self.current_state.update(inputs)
        perception_item = WMItem(type="perception", content=str(inputs))
        self.working_memory.add_item(perception_item)

    def generate_expectation(self) -> Dict[str, List[str]]:
        """
        Generate expectations based on semantic relationships.
        If the agent perceives a concept, predict related concepts.
        """
        expectations = {}
        # Assuming current_state values are concept labels
        for key, value in self.current_state.items():
            if isinstance(value, str):
                related = self.semantic_memory.get_related(value)
                if related:
                    expectations[key + "_related"] = related
        return expectations

    def select_action(self, intentions: List[Intention]) -> str:
        # Select highest priority intention and convert to action
        if intentions:
            return intentions[0].description
        return "Idle"

    def observe(self, action_result: Dict):
        # Update current state with result of action
        self.current_state.update(action_result)
        observation_item = WMItem(type="observation", content=str(action_result))
        self.working_memory.add_item(observation_item)

    def update_model(self, discrepancy: float):
        # If discrepancy high, adjust internal reference (simulate learning)
        if discrepancy > 0.7:
            for key, value in self.current_state.items():
                self.goal_manager.reference_state[key] = value

    def step(self, inputs: Dict, action_result: Dict) -> Dict[str, Any]:
        # 1. Perceive
        self.perceive(inputs)

        # 2. Compute discrepancy and intentions
        discrepancy = self.goal_manager.evaluate_discrepancy(self.current_state)
        intentions = self.goal_manager.generate_intentions(discrepancy)

        # 3. Generate expectations based on current state
        expectations = self.generate_expectation()

        # 4. Select and perform action
        action = self.select_action(intentions)

        # 5. Observe results
        self.observe(action_result)

        # 6. Update model if needed
        self.update_model(discrepancy)

        # 7. Save episode
        episode = Episode(
            context="agent_cycle",
            perception=inputs,
            action=action,
            result=action_result,
        )
        self.episodic_memory.add_episode(episode)

        return {
            "discrepancy": discrepancy,
            "selected_action": action,
            "intentions": [i.model_dump() for i in intentions],
            "expectations": expectations,
        }
