from pydantic import BaseModel, Field
from typing import List, Dict, Literal, Optional
from datetime import datetime, timezone

class EmbodiedExperience(BaseModel):
    id: str
    state_before: Dict[str, object]
    action: str
    state_after: Dict[str, object]
    outcome: Literal["success", "failure"]
    cost: Dict[str, float]
    context: Dict[str, object]
    adaptations: List[str] = []
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
