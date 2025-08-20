from pydantic import BaseModel, Field
from typing import List, Dict, Literal, Optional
from datetime import datetime, timezone
from uuid import UUID, uuid4

# Type Aliases
Modality = Literal["visual", "linguistic", "motor"]
ConceptType = Literal["entity", "action", "property"]

class Concept(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    label: str
    description: str | None = None
    attributes: Dict[str, object] = Field(default_factory=dict)
    relations: List[Dict[str, str]] = Field(default_factory=list)
    confidence: float = 1.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Rule(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    if_: List[str] = Field(default_factory=list, alias="if")
    then: List[str] = Field(default_factory=list)
    priority: int = 1
    confidence: float = 1.0
    source: Literal["linguistic", "experiential", "synthetic"] = "linguistic"
    adaptable: bool = True
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SemanticLink(BaseModel):
    source: UUID
    target: UUID
    type: str
    weight: float = 0.5

class SemanticSchema(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    concepts: List[str] = Field(default_factory=list)
    rules: List[str] = Field(default_factory=list)
    links: List[SemanticLink] = Field(default_factory=list)
    context: str = "NaturalEnv"
    modifiable_by_agent: bool = True
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Episode(BaseModel):
    """Represents a single event or experience in the agent's memory."""
    id: UUID = Field(default_factory=uuid4)
    context: str
    perception: dict
    action: str
    result: dict
    body_before: Dict = Field(default_factory=dict)
    body_after: Dict = Field(default_factory=dict)
    emotion_signal: float = 0.0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
