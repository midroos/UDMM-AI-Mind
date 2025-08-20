from typing import List
from uuid import uuid4
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class Intention(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: str  # "environmental_action" or "cognitive_action"
    description: str
    priority: float
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class GoalManager:
    def __init__(self, reference_state: dict):
        # reference_state represents the ideal internal model (target sync)
        self.reference_state = reference_state

    def evaluate_discrepancy(self, current_state: dict) -> float:
        """
        Compute a simple discrepancy measure between current_state and reference_state.
        Currently uses overlap ratio of keys/values. Can be extended to semantic similarity.
        """
        if not self.reference_state:
            return 0.0 if not current_state else 1.0

        score = 0
        for key in self.reference_state:
            if key in current_state and current_state[key] == self.reference_state[key]:
                score += 1
        return 1 - (score / len(self.reference_state))

    def generate_intentions(self, discrepancy: float) -> List[Intention]:
        """
        Generate intentions based on discrepancy.
        High discrepancy -> more cognitive actions (learning).
        Low discrepancy -> environmental exploration.
        """
        intentions = []
        if discrepancy > 0.5:
            intentions.append(Intention(
                type="cognitive_action",
                description="Update internal model to reduce mismatch",
                priority=discrepancy
            ))
        intentions.append(Intention(
            type="environmental_action",
            description="Explore environment for better alignment",
            priority=max(0.1, discrepancy / 2)
        ))
        return sorted(intentions, key=lambda x: x.priority, reverse=True)
