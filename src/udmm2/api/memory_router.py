from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, List
from uuid import UUID

# Import services and models
from ..memory.schema_service import SemanticService
from ..memory.episodic_memory import EpisodicMemory
from ..memory.embodied_memory import EmbodiedMemory
from ..memory.api_models import (
    ConceptIn, ConceptOut, RuleIn, RuleOut,
    SemanticSchemaIn, SemanticSchemaOut,
    EmbodiedExperienceIn, EmbodiedExperienceOut
)
from ..memory.models import Episode

router = APIRouter(prefix="/memory", tags=["Memory (Legacy)"])

# Instantiate services that will be used by the API endpoints
semantic_service = SemanticService()
episodic_memory = EpisodicMemory()
embodied_memory = EmbodiedMemory()

# ---- Concepts ----
@router.post("/concepts", response_model=ConceptOut)
def create_concept(payload: ConceptIn):
    return semantic_service.create_concept(payload)

@router.get("/concepts/{concept_id}", response_model=ConceptOut)
def get_concept(concept_id: UUID):
    concept = semantic_service.get_concept(concept_id)
    if not concept:
        raise HTTPException(status_code=404, detail="Concept not found")
    return concept

@router.put("/concepts/{concept_id}", response_model=ConceptOut)
def update_concept(concept_id: UUID, patch: Dict):
    concept = semantic_service.update_concept(concept_id, patch)
    if not concept:
        raise HTTPException(status_code=404, detail="Concept not found or not updated")
    return concept

# ---- Rules ----
@router.post("/rules", response_model=RuleOut)
def create_rule(payload: RuleIn):
    return semantic_service.create_rule(payload)

@router.get("/rules/{rule_id}", response_model=RuleOut)
def get_rule(rule_id: UUID):
    rule = semantic_service.get_rule(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule

# ---- Semantic Schemas ----
@router.post("/schemas", response_model=SemanticSchemaOut)
def create_schema(payload: SemanticSchemaIn):
    return semantic_service.create_schema(payload)

@router.get("/schemas/{schema_id}", response_model=SemanticSchemaOut)
def get_schema(schema_id: UUID):
    sch = semantic_service.get_schema(schema_id)
    if not sch:
        raise HTTPException(status_code=404, detail="Schema not found")
    return sch

@router.post("/schemas/{schema_id}/activate", response_model=SemanticSchemaOut)
def activate_schema(schema_id: UUID, delta: float = 0.1):
    sch = semantic_service.bump_activation(schema_id, delta)
    if not sch:
        raise HTTPException(status_code=404, detail="Schema not found")
    return sch

# ---- Smart query ----
@router.post("/query")
def smart_query(payload: Dict):
    if payload.get("find") == "rules":
        where = payload.get("where", {})
        concept_id_str = where.get("related_to_concept")
        if not concept_id_str:
            raise HTTPException(status_code=400, detail="Missing 'related_to_concept' in where clause")

        concept_id = UUID(concept_id_str)
        min_conf = float(where.get("min_confidence", 0.0))
        sort_by = payload.get("sort_by", "priority") == "priority"
        rules = semantic_service.find_rules_related_to_concept(concept_id, min_conf, sort_by)
        return {"items": rules}
    return {"items": []}

# ---- Embodied Experiences ----
@router.post("/embodied_experiences", response_model=EmbodiedExperienceOut)
def create_embodied_experience(payload: EmbodiedExperienceIn):
    return embodied_memory.add_experience(payload)

@router.get("/embodied_experiences", response_model=List[EmbodiedExperienceOut])
def list_embodied_experiences(limit: int = Query(50, ge=1, le=500)):
    return embodied_memory.list_experiences(limit)

# ---- Episodic Memory ----
@router.post("/episodes", response_model=Episode)
def create_episode(payload: Episode):
    eid = episodic_memory.add_episode(**payload.model_dump())
    return episodic_memory.get_episode(eid)

@router.get("/episodes", response_model=List[Episode])
def list_episodes(limit: int = Query(50, ge=1, le=500)):
    return episodic_memory.list_episodes(limit)
