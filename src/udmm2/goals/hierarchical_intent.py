from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import uuid4, UUID
from datetime import datetime, timezone
import math

from .attractor import AttractorModel
# Use a forward reference for SemanticMemory to avoid circular import issues if needed
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..memory.semantic_memory import SemanticMemory

def utcnow():
    return datetime.now(timezone.utc)

class SubGoal(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    target_x: float = 0.0
    target_y: float = 0.0
    associated_concept: Optional[str] = None
    weight: float = 1.0
    tolerance: float = 0.2
    completed: bool = False

    def distance_to(self, state: Dict[str, float]) -> float:
        dx = self.target_x - float(state.get("x", 0.0))
        dy = self.target_y - float(state.get("y", 0.0))
        return math.hypot(dx, dy)

    def is_reached(self, state: Dict[str, float]) -> bool:
        return self.distance_to(state) <= self.tolerance

class HierarchicalIntent(BaseModel):
    ultimate_attractor: AttractorModel
    subgoals: List[SubGoal] = Field(default_factory=list)
    current_index: int = 0
    created_at: datetime = Field(default_factory=utcnow)

    def generate_linear_subgoals(self, current_state: Dict[str, float], n_steps: int = 3,
                                 semantic_memory: Optional["SemanticMemory"] = None,
                                 associate_by_proximity: bool = True):
        cx = float(current_state.get("x", 0.0))
        cy = float(current_state.get("y", 0.0))
        tx = self.ultimate_attractor.target_x
        ty = self.ultimate_attractor.target_y

        dx = tx - cx
        dy = ty - cy

        self.subgoals = []
        for i in range(1, n_steps + 1):
            sx = cx + dx * (i / n_steps)
            sy = cy + dy * (i / n_steps)
            assoc = None
            if semantic_memory and associate_by_proximity and hasattr(semantic_memory, "closest_concept"):
                try:
                    assoc = semantic_memory.closest_concept(x=sx, y=sy)
                except Exception:
                    assoc = None
            sg = SubGoal(target_x=sx, target_y=sy, associated_concept=assoc)
            self.subgoals.append(sg)
        self.current_index = 0
        return self.subgoals

    def current_subgoal(self) -> Optional[SubGoal]:
        if 0 <= self.current_index < len(self.subgoals):
            return self.subgoals[self.current_index]
        return None

    def advance_if_reached(self, state: Dict[str, float]) -> bool:
        sg = self.current_subgoal()
        if sg and sg.is_reached(state):
            sg.completed = True
            self.current_index += 1
            return True
        return False

    def is_finished(self) -> bool:
        return self.current_index >= len(self.subgoals)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ultimate": {"x": self.ultimate_attractor.target_x, "y": self.ultimate_attractor.target_y},
            "current_index": self.current_index,
            "n_subgoals": len(self.subgoals),
            "subgoals": [s.model_dump() for s in self.subgoals]
        }
