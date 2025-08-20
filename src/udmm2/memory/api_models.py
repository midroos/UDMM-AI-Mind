from __future__ import annotations
from typing import List, Dict, Optional, Literal
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from datetime import datetime, timezone

def utcnow():
    return datetime.now(timezone.utc)

# ---- Core entities (API layer views) ----

class ConceptIn(BaseModel):
    label: str
    description: Optional[str] = None
    attributes: Dict[str, object] = Field(default_factory=dict)
    # Keeping relations simple for the API layer, assuming UUIDs are passed as strings
    relations: List[Dict[str, str]] = Field(default_factory=list)

class ConceptOut(BaseModel):
    id: UUID
    label: str
    description: Optional[str]
    attributes: Dict[str, object]
    relations: List[Dict[str, str]]
    confidence: float
    created_at: datetime

class RuleIn(BaseModel):
    conditions: List[str]
    actions: List[str]
    priority: int = 1
    confidence: float = 0.88
    source: Literal["linguistic", "experiential", "synthetic"] = "linguistic"

class RuleOut(BaseModel):
    id: UUID
    conditions: List[str]
    actions: List[str]
    priority: int
    confidence: float
    source: str
    last_updated: datetime

class EmbodiedExperienceIn(BaseModel):
    state_before: Dict[str, object]
    action: str
    state_after: Dict[str, object]
    outcome: Literal["success", "failure", "unknown"] = "unknown"
    cost: Dict[str, float] = Field(default_factory=dict)
    context: Dict[str, object] = Field(default_factory=dict)

class EmbodiedExperienceOut(EmbodiedExperienceIn):
    id: UUID
    timestamp: datetime

class EpisodicSnapshotIn(BaseModel):
    perception: Dict[str, object]
    action: str
    result: str
    reward: Optional[float] = None

class EpisodicSnapshotOut(EpisodicSnapshotIn):
    id: UUID
    timestamp: datetime

# ---- Semantic Schema ----

class SchemaNode(BaseModel):
    node_id: UUID
    label: str
    role_in_schema: Literal["central_subject", "attribute", "consequence", "context"] = "context"

class SchemaEdge(BaseModel):
    edge_id: UUID = Field(default_factory=uuid4)
    from_node: UUID
    to_node: UUID
    relation: Literal["causes", "has_property", "is_a", "part_of", "enables", "associates"] = "associates"
    weight: float = 1.0

class AssociatedRuleRef(BaseModel):
    rule_id: UUID
    relevance: float = 1.0
    trigger_conditions: List[Dict[str, object]] = Field(default_factory=list)

class SemanticSchemaIn(BaseModel):
    topic: str
    description: Optional[str] = None
    source: Dict[str, str] = Field(default_factory=lambda: {"type": "synthetic", "reference": ""})
    nodes: List[SchemaNode] = Field(default_factory=list)
    edges: List[SchemaEdge] = Field(default_factory=list)
    associated_rules: List[AssociatedRuleRef] = Field(default_factory=list)
    parent_schema_id: Optional[UUID] = None
    sub_schema_ids: List[UUID] = Field(default_factory=list)

class SemanticSchemaOut(SemanticSchemaIn):
    schema_id: UUID
    version: int
    activation_level: float
    confidence_score: float
    usage_frequency: int
    created_at: datetime
    updated_at: datetime
