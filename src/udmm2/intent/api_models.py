from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, Literal, Dict, List
from uuid import UUID, uuid4
from datetime import datetime, timezone

def utcnow():
    return datetime.now(timezone.utc)

class AttractorConfig(BaseModel):
    """Virtual Attractor: soft target for the agent to move towards."""
    id: UUID = Field(default_factory=uuid4)
    description: str = "Global coherence / saturated world"
    # Weighted aspects of discrepancy the agent tries to reduce
    weights: Dict[str, float] = Field(default_factory=lambda: {
        "prediction_error": 1.0,
        "schema_alignment": 0.7,
        "body_homeostasis": 0.8
    })
    target: Dict[str, float] = Field(default_factory=lambda: {
        "energy_min": 0.3, "energy_max": 0.9, "activation": 0.6
    })
    created_at: datetime = Field(default_factory=utcnow)

class GoalIn(BaseModel):
    """User/system-declared goal."""
    label: str
    kind: Literal["cognitive", "environmental", "exploratory"] = "cognitive"
    priority: int = 1
    constraints: Dict[str, float] = Field(default_factory=dict)  # e.g. {"risk_max": 0.6}
    target_state: Dict[str, float] = Field(default_factory=dict) # e.g. {"activation":"Fire Safety", "min":0.7}
    horizon_steps: int = 5

class GoalOut(GoalIn):
    id: UUID
    created_at: datetime

class Intention(BaseModel):
    """Generated intention: operationalized direction for next step(s)."""
    id: UUID = Field(default_factory=uuid4)
    derived_from_goal: Optional[UUID] = None
    modality: Literal["cognitive","environmental"] = "cognitive"
    description: str = ""
    strength: float = 1.0
    created_at: datetime = Field(default_factory=utcnow)

class PrecisionSignal(BaseModel):
    """Emotion-as-precision: scalar(s) modulating inference/action."""
    arousal: float = 0.0     # from body deltas
    valence: float = 0.0     # optional future use
    precision_gain: float = 1.0  # multiplier on rule weighting / action selection
