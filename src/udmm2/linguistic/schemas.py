from pydantic import BaseModel, Field
from typing import List, Dict, Literal, Optional
from datetime import datetime

Modality = Literal["visual", "linguistic", "motor"]
ConceptType = Literal["entity", "action", "property"]

class Concept(BaseModel):
    id: str
    label: str
    description: str | None = None
    attributes: Dict[str, object] = Field(default_factory=dict)
    relations: List[Dict[str, str]] = Field(default_factory=list)
    confidence: float = 1.0
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Rule(BaseModel):
    id: str
    if_: List[str] = Field(default_factory=list, alias="if")
    then: List[str] = Field(default_factory=list)
    priority: int = 1
    confidence: float = 1.0
    source: Literal["linguistic", "experiential"] = "linguistic"
    adaptable: bool = True
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class EmbodiedExperience(BaseModel):
    id: str
    state_before: Dict[str, object]
    action: str
    state_after: Dict[str, object]
    outcome: Literal["success", "failure"]
    cost: Dict[str, float]
    context: Dict[str, object]
    adaptations: List[str] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class EpisodicSnapshot(BaseModel):
    id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    perception: Dict[str, object]
    action: Optional[str] = None
    result: Optional[str] = None
    reward: Optional[float] = None
