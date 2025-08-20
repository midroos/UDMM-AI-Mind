from fastapi import FastAPI, HTTPException, Query
from typing import Optional, Dict, List
from uuid import UUID

# Use a shared service instance for the app lifecycle
from ..memory.schema_service import SemanticService
from ..memory.episodic_memory import EpisodicMemory
from ..memory.embodied_memory import EmbodiedMemory

# Import API models
from ..memory.api_models import (
    ConceptIn, ConceptOut, RuleIn, RuleOut,
    SemanticSchemaIn, SemanticSchemaOut,
    EmbodiedExperienceIn, EmbodiedExperienceOut,
    EpisodicSnapshotIn, EpisodicSnapshotOut # Note: We adapt this to the main Episode model
)
# Import the main Episode model used by the agent
from ..memory.models import Episode


app = FastAPI(title="UDMM Memory API", version="0.1.0")

# Instantiate services that will be used by the API endpoints
semantic_service = SemanticService()
episodic_memory = EpisodicMemory()
embodied_memory = EmbodiedMemory()


# ---- Concepts ----
@app.post("/memory/concepts", response_model=ConceptOut, tags=["Concepts"])
def create_concept(payload: ConceptIn):
    return semantic_service.create_concept(payload)

@app.get("/memory/concepts/{concept_id}", response_model=ConceptOut, tags=["Concepts"])
def get_concept(concept_id: UUID):
    concept = semantic_service.get_concept(concept_id)
    if not concept:
        raise HTTPException(404, "Concept not found")
    return concept

@app.put("/memory/concepts/{concept_id}", response_model=ConceptOut, tags=["Concepts"])
def update_concept(concept_id: UUID, patch: Dict):
    concept = semantic_service.update_concept(concept_id, patch)
    if not concept:
        raise HTTPException(404, "Concept not found or not updated")
    return concept

# ---- Rules ----
@app.post("/memory/rules", response_model=RuleOut, tags=["Rules"])
def create_rule(payload: RuleIn):
    return semantic_service.create_rule(payload)

@app.get("/memory/rules/{rule_id}", response_model=RuleOut, tags=["Rules"])
def get_rule(rule_id: UUID):
    rule = semantic_service.get_rule(rule_id)
    if not rule:
        raise HTTPException(404, "Rule not found")
    return rule

# ---- Semantic Schemas ----
@app.post("/memory/schemas", response_model=SemanticSchemaOut, tags=["Schemas"])
def create_schema(payload: SemanticSchemaIn):
    return semantic_service.create_schema(payload)

@app.get("/memory/schemas/{schema_id}", response_model=SemanticSchemaOut, tags=["Schemas"])
def get_schema(schema_id: UUID):
    sch = semantic_service.get_schema(schema_id)
    if not sch:
        raise HTTPException(404, "Schema not found")
    return sch

@app.post("/memory/schemas/{schema_id}/activate", response_model=SemanticSchemaOut, tags=["Schemas"])
def activate_schema(schema_id: UUID, delta: float = 0.1):
    sch = semantic_service.bump_activation(schema_id, delta)
    if not sch:
        raise HTTPException(404, "Schema not found")
    return sch

# ---- Smart query ----
@app.post("/memory/query", tags=["Query"])
def smart_query(payload: Dict):
    if payload.get("find") == "rules":
        where = payload.get("where", {})
        concept_id_str = where.get("related_to_concept")
        if not concept_id_str:
            raise HTTPException(400, "Missing 'related_to_concept' in where clause")

        concept_id = UUID(concept_id_str)
        min_conf = float(where.get("min_confidence", 0.0))
        sort_by = payload.get("sort_by", "priority") == "priority"
        rules = semantic_service.find_rules_related_to_concept(concept_id, min_conf, sort_by)
        return {"items": rules}
    return {"items": []}

# ---- Embodied Experiences ----
@app.post("/memory/embodied_experiences", response_model=EmbodiedExperienceOut, tags=["Experiences"])
def create_embodied_experience(payload: EmbodiedExperienceIn):
    return embodied_memory.add_experience(payload)

@app.get("/memory/embodied_experiences", response_model=List[EmbodiedExperienceOut], tags=["Experiences"])
def list_embodied_experiences(limit: int = Query(50, ge=1, le=500)):
    return embodied_memory.list_experiences(limit)

# ---- Episodic Memory ----
@app.post("/memory/episodes", response_model=Episode, tags=["Episodes"])
def create_episode(payload: Episode):
    # This endpoint accepts a full Episode object, which is more aligned with the agent's usage
    eid = episodic_memory.add_episode(payload)
    return episodic_memory.get_episode(eid)

@app.get("/memory/episodes", response_model=List[Episode], tags=["Episodes"])
def list_episodes(limit: int = Query(50, ge=1, le=500)):
    return episodic_memory.list_episodes(limit)
