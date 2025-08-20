from __future__ import annotations
from uuid import UUID, uuid4
from typing import Dict, List, Optional
from datetime import datetime, timezone
from .api_models import GoalIn, GoalOut, Intention, AttractorConfig, PrecisionSignal

def utcnow():
    return datetime.now(timezone.utc)

class GoalManager:
    def __init__(self, attractor: Optional[AttractorConfig]=None):
        self._goals: Dict[UUID, GoalOut] = {}
        self.attractor = attractor or AttractorConfig()

    def add_goal(self, g: GoalIn) -> GoalOut:
        gid = uuid4()
        out = GoalOut(id=gid, created_at=utcnow(), **g.model_dump())
        self._goals[gid] = out
        return out

    def get_goal(self, gid: UUID) -> Optional[GoalOut]:
        return self._goals.get(gid)

    def list_goals(self) -> List[GoalOut]:
        return list(self._goals.values())

    def delete_goal(self, gid: UUID) -> bool:
        return self._goals.pop(gid, None) is not None

    def compute_discrepancy(self, signals: Dict[str, float]) -> float:
        """Scalar discrepancy toward the attractor (lower is better)."""
        w = self.attractor.weights
        # Example blend: prediction_error + (1-activation) + body_homeostasis deviation
        pe = signals.get("prediction_error", 0.0)
        act = signals.get("schema_activation", 0.0)
        body_dev = signals.get("body_deviation", 0.0)
        # Ensure discrepancy is non-negative
        return max(0.0, w.get("prediction_error", 1.0) * pe + w.get("schema_alignment", 0.7) * (1.0 - act) + w.get("body_homeostasis", 0.8) * body_dev)

    def intentions_from_state(self, signals: Dict[str, float], goals: Optional[List[GoalOut]]=None) -> List[Intention]:
        """Map discrepancy & goals to actionable intentions."""
        disc = self.compute_discrepancy(signals)
        base_strength = min(1.0, max(0.0, 1.0 - disc))  # higher strength if small discrepancy
        out: List[Intention] = []
        goals = goals or self.list_goals()
        if not goals:
            out.append(Intention(modality="cognitive", description="Refine predictive model", strength=base_strength))
            return out
        for g in goals:
            desc = f"Drive toward goal: {g.label}"
            mod = "environmental" if g.kind == "environmental" else "cognitive"
            stren = min(1.0, g.priority/3.0 + base_strength*0.5)
            out.append(Intention(derived_from_goal=g.id, modality=mod, description=desc, strength=stren))
        return out

    def precision_from_body(self, body_before: Dict, body_after: Dict) -> PrecisionSignal:
        """First-order emotion: arousal = distance moved + |Δenergy|; precision_gain = 1+arousal."""
        def pos(b): return (b.get("position", {}).get("x",0.0), b.get("position", {}).get("y",0.0))
        def dist(a,b):
            return ((a[0]-b[0])**2 + (a[1]-b[1])**2) ** 0.5

        arousal = dist(pos(body_before), pos(body_after)) + abs((body_after.get("energy",0)-body_before.get("energy",0)))
        gain = 1.0 + min(1.0, arousal) # Cap gain contribution
        return PrecisionSignal(arousal=arousal, valence=0.0, precision_gain=gain)
