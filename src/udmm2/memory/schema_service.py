from __future__ import annotations
from typing import List, Dict, Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone

from .api_models import (
    ConceptIn, ConceptOut,
    RuleIn, RuleOut,
    SemanticSchemaIn, SemanticSchemaOut
)
from .semantic_memory import SemanticMemory

def utcnow():
    return datetime.now(timezone.utc)

class SemanticService:
    """
    Thin service façade over the networkx-based SemanticMemory providing:
    - Concept/Rule CRUD
    - Schema CRUD with activation/confidence tracking
    - Smart queries
    """
    def __init__(self, mem: Optional[SemanticMemory] = None):
        self.mem = mem or SemanticMemory()
        self.schemas: Dict[UUID, Dict] = {}  # in-memory schema registry

    # ---- Concepts ----
    def create_concept(self, data: ConceptIn) -> ConceptOut:
        cid = self.mem.add_concept(
            label=data.label,
            description=data.description or "",
            attributes=data.attributes,
            relations=data.relations,
            confidence=0.95
        )
        c = self.mem.get_concept_by_id(cid)
        return ConceptOut(**c)

    def get_concept(self, concept_id: UUID) -> Optional[ConceptOut]:
        c = self.mem.get_concept_by_id(concept_id)
        return ConceptOut(**c) if c else None

    def update_concept(self, concept_id: UUID, patch: Dict) -> Optional[ConceptOut]:
        updated = self.mem.update_concept(concept_id, **patch)
        return ConceptOut(**updated) if updated else None

    # ---- Rules ----
    def create_rule(self, data: RuleIn) -> RuleOut:
        rid = self.mem.add_rule(
            conditions=data.conditions,
            actions=data.actions,
            priority=data.priority,
            confidence=data.confidence,
            source=data.source
        )
        r = self.mem.get_rule_by_id(rid)
        return RuleOut(**r)

    def get_rule(self, rule_id: UUID) -> Optional[RuleOut]:
        r = self.mem.get_rule_by_id(rule_id)
        return RuleOut(**r) if r else None

    # ---- Schemas ----
    def create_schema(self, data: SemanticSchemaIn) -> SemanticSchemaOut:
        sid = uuid4()
        now = utcnow()
        record = {
            "schema_id": sid,
            "version": 1,
            "activation_level": 0.0,
            "confidence_score": 0.7,
            "usage_frequency": 0,
            "created_at": now,
            "updated_at": now,
            **data.model_dump()
        }
        self.schemas[sid] = record
        return SemanticSchemaOut(**record)

    def get_schema(self, schema_id: UUID) -> Optional[SemanticSchemaOut]:
        rec = self.schemas.get(schema_id)
        return SemanticSchemaOut(**rec) if rec else None

    def bump_activation(self, schema_id: UUID, delta: float = 0.1) -> Optional[SemanticSchemaOut]:
        rec = self.schemas.get(schema_id)
        if not rec:
            return None
        rec["activation_level"] = max(0.0, min(1.0, rec["activation_level"] + delta))
        rec["usage_frequency"] += 1
        rec["updated_at"] = utcnow()
        return SemanticSchemaOut(**rec)

    # ---- Smart query ----
    def find_rules_related_to_concept(self, concept_id: UUID, min_confidence: float = 0.0, sort_by_priority: bool = True):
        related_rule_ids = self.mem.rules_related_to_concept(concept_id)
        rules = []
        for rid in related_rule_ids:
            r = self.mem.get_rule_by_id(rid)
            if r and r["confidence"] >= min_confidence:
                rules.append(r)
        if sort_by_priority:
            rules.sort(key=lambda x: (-x["priority"], -x["confidence"]))
        return [RuleOut(**r) for r in rules]
