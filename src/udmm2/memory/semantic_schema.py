from pydantic import BaseModel, Field
from typing import List, Dict
from datetime import datetime

class Link(BaseModel):
    source: str
    target: str
    type: str
    weight: float = 0.5

class SemanticSchema(BaseModel):
    id: str
    concepts: List[str] = Field(default_factory=list)
    rules: List[str] = Field(default_factory=list)
    links: List[Link] = Field(default_factory=list)
    context: str = "NaturalEnv"
    modifiable_by_agent: bool = True
    last_updated: datetime = Field(default_factory=datetime.utcnow)
