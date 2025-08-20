from pydantic import BaseModel, Field
from typing import List, Dict, Literal, Optional
from datetime import datetime

# Type Aliases
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

class SemanticLink(BaseModel):
    source: str
    target: str
    type: str
    weight: float = 0.5

class SemanticSchema(BaseModel):
    id: str
    concepts: List[str] = Field(default_factory=list)
    rules: List[str] = Field(default_factory=list)
    links: List[SemanticLink] = Field(default_factory=list)
    context: str = "NaturalEnv"
    modifiable_by_agent: bool = True
    last_updated: datetime = Field(default_factory=datetime.utcnow)
