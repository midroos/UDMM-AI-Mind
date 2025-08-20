import math
from typing import Any, Dict, List
from uuid import uuid4
from datetime import datetime, timezone

from .body_model import BodyModel
from .working_memory import WorkingMemory, WMItem
from ..memory.episodic_memory import EpisodicMemory
from ..memory.semantic_memory import SemanticMemory
from ..memory.models import Episode
from .goal_manager import GoalManager, Intention


class UDMMAgent:
    def __init__(self, name: str, reference_state: Dict):
        self.name = name
        self.body = BodyModel()
        self.working_memory = WorkingMemory()
        self.episodic_memory = EpisodicMemory()
        self.goal_manager = GoalManager(reference_state)
        self.semantic_memory = SemanticMemory()
        self.current_state = {}  # Simplified representation of agent state

    def perceive(self, inputs: Dict):
        # Update current state with external inputs and internal body state
        self.current_state.update(inputs)
        self.current_state.update({"body": self.body.get_state()})

        perception_content = {**inputs, "body": self.body.get_state()}
        perception_item = WMItem(type="perception", content=str(perception_content))
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

    def _execute_action(self, action: str) -> Dict[str, Any]:
        """Translates a string action into a physical body action."""
        dx, dy, d_energy = 0.0, 0.0, 0.0

        if "Explore" in action:
            dx, dy = self.body.move(distance=0.5)
            self.body.rotate(dtheta=0.1)
            d_energy = -0.5  # Assumed energy cost

        # Simple emotion signal calculation
        arousal = math.sqrt(dx**2 + dy**2) + abs(d_energy)

        return {"dx": dx, "dy": dy, "d_energy": d_energy, "emotion_signal": arousal}

    def step(self, inputs: Dict, action_result: Dict) -> Dict[str, Any]:
        # 1. Perceive world and own body state
        self.perceive(inputs)
        body_before = self.body.get_state()

        # 2. Reason about state and generate intentions
        discrepancy = self.goal_manager.evaluate_discrepancy(self.current_state)
        intentions = self.goal_manager.generate_intentions(discrepancy)
        expectations = self.generate_expectation()

        # 3. Select and execute a bodily action
        action_str = self.select_action(intentions)
        action_effects = self._execute_action(action_str)
        body_after = self.body.get_state()

        # 4. Observe external results of action
        self.observe(action_result)

        # 5. Update internal models based on discrepancy
        self.update_model(discrepancy)

        # 6. Save a rich, embodied episode
        episode = Episode(
            context="agent_cycle",
            perception=inputs,
            action=action_str,
            result=action_result,
            body_before=body_before,
            body_after=body_after,
            emotion_signal=action_effects["emotion_signal"]
        )
        self.episodic_memory.add_episode(episode)

        return {
            "discrepancy": discrepancy,
            "selected_action": action_str,
            "intentions": [i.model_dump() for i in intentions],
            "expectations": expectations,
            "emotion_signal": action_effects["emotion_signal"]
        }
