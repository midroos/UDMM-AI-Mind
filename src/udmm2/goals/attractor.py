from pydantic import BaseModel, Field
from typing import Dict
from datetime import datetime, timezone

def utcnow():
    return datetime.now(timezone.utc)

class AttractorModel(BaseModel):
    target_x: float
    target_y: float
    weight: float = 1.0
    timestamp: datetime = Field(default_factory=utcnow)

    def distance(self, state: Dict[str,float]) -> float:
        dx = float(state.get("x", 0.0)) - self.target_x
        dy = float(state.get("y", 0.0)) - self.target_y
        return ((dx**2)+(dy**2))**0.5

    def pull_strength(self, state: Dict[str,float], epsilon: float = 1e-6) -> float:
        d = self.distance(state)
        return self.weight / (d + epsilon)
