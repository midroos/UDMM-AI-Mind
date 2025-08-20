from typing import Any, Dict
from uuid import uuid4
from datetime import datetime, timezone

from udmm2.memory.semantic_memory import SemanticMemory
from udmm2.memory.episodic_memory import EpisodicMemory
from udmm2.memory.models import Episode
from udmm2.agent.working_memory import WorkingMemory, WMItem

class UDMMAgent:
    def __init__(self):
        self.semantic_memory = SemanticMemory()
        self.episodic_memory = EpisodicMemory()
        self.working_memory = WorkingMemory()
        self.cycle_count = 0

    def generate_expectation(self) -> str:
        active_items = self.working_memory.get_active_items()
        if active_items:
            return f"Expect related to: {[item.content for item in active_items]}"
        return "No specific expectation"

    def select_action(self) -> str:
        # For now, pick a simple exploratory action
        return "explore_environment"

    def observe(self, observation: str) -> WMItem:
        obs_item = WMItem(type="observation", content=observation)
        self.working_memory.add_item(obs_item)
        return obs_item

    def update_model(self, action: str, observation: str):
        # Store episode
        episode = Episode(
            description=f"Action '{action}' led to '{observation}'",
            context="NaturalEnv",
            action=action,
            result=observation
        )
        self.episodic_memory.add_episode(episode)

    def step(self) -> Dict[str, Any]:
        self.cycle_count += 1
        expectation = self.generate_expectation()
        action = self.select_action()
        observation = f"Perceived after {action}"
        self.observe(observation)
        self.update_model(action, observation)
        self.working_memory.decay_activation()
        return {
            "cycle": self.cycle_count,
            "expectation": expectation,
            "action": action,
            "observation": observation
        }
