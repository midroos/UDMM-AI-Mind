from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from .attractor import AttractorModel
from ..memory.semantic_memory import SemanticMemory

def utcnow():
    return datetime.now(timezone.utc)

class Subgoal(BaseModel):
    target_x: float
    target_y: float
    associated_concept: Optional[str] = None
    weight: float = 1.0
    completed: bool = False

class HierarchicalIntent(BaseModel):
    ultimate_attractor: AttractorModel
    subgoals: List[Subgoal] = []
    current_index: int = 0
    timestamp: datetime = Field(default_factory=utcnow)

    def generate_subgoals(self, state: Dict[str,float], semantic_memory: SemanticMemory, n_steps: int = 3):
        # تقسيم المسافة إلى n_steps نقاط متساوية
        dx = self.ultimate_attractor.target_x - state["x"]
        dy = self.ultimate_attractor.target_y - state["y"]
        self.subgoals = []
        for i in range(1, n_steps+1):
            sx = state["x"] + dx*i/n_steps
            sy = state["y"] + dy*i/n_steps
            concept = None
            if hasattr(semantic_memory, "closest_concept"):
                concept = semantic_memory.closest_concept(x=sx, y=sy)
            self.subgoals.append(Subgoal(target_x=sx, target_y=sy, associated_concept=concept))
        self.current_index = 0

    def current_subgoal(self) -> Optional[Subgoal]:
        if self.current_index < len(self.subgoals):
            return self.subgoals[self.current_index]
        return None

    def advance_subgoal(self):
        if self.current_index < len(self.subgoals):
            self.subgoals[self.current_index].completed = True
            self.current_index += 1
