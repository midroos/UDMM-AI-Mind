from typing import Any, Dict, List, Optional
from uuid import uuid4
from datetime import datetime, timezone
import math

from .working_memory import WorkingMemory, WMItem
from ..memory.episodic_memory import EpisodicMemory
from ..memory.models import Episode
from ..memory.semantic_memory import SemanticMemory
from ..body.body_model import BodyModel
from ..envs.natural_env import NaturalEnv

def utcnow_iso():
    return datetime.now(timezone.utc).isoformat()

class UDMMAgent:
    def __init__(self, env: Optional[NaturalEnv] = None):
        self.working_memory = WorkingMemory()
        self.episodic_memory = EpisodicMemory()
        self.semantic_memory = SemanticMemory()
        self.body = BodyModel()
        self.env = env or NaturalEnv()
        self._precision_gain = 1.0
        self.cycle = 0

        try:
            self.semantic_memory.add_concept(
                label="move_forward",
                description="action leading to forward displacement",
                attributes={"type": "action", "effect": "position_delta"},
                relations=[]
            )
        except Exception:
            pass

    def generate_expectation(self, perception: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        exp = {}
        active = self.working_memory.get_active_items()
        for it in active:
            if it.type == "action" and "move_forward" in it.content:
                step = 1.0
                rad = math.radians(self.body.orientation_deg)
                exp["predicted_body_delta"] = {"dx_est": step * math.cos(rad), "dy_est": step * math.sin(rad)}

        if perception:
            for k, v in perception.items():
                if isinstance(v, str):
                    try:
                        related = self.semantic_memory.get_related(v)
                        if related:
                            exp[f"{k}_related"] = related
                    except Exception:
                        pass
        exp["predicted_body_state"] = self.body.get_state()
        exp["prediction_error"] = 0.0
        return exp

    def select_action(self, intentions: Optional[List[Any]] = None) -> Dict[str, Any]:
        gain = max(0.5, min(2.0, getattr(self, "_precision_gain", 1.0)))
        if self.body.energy < 0.15:
            return {"type": "idle"}
        step = 0.5 * gain
        return {"type": "move_forward", "step": step}

    def apply_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        body_before = self.body.get_state()
        result_body = {}
        if action.get("type") == "move_forward":
            result_body = self.body.move_forward(float(action.get("step", 0.5)))
        elif action.get("type") == "turn":
            result_body = self.body.turn(float(action.get("angle", 90.0)))
        else:
            result_body = {"status": "noop"}

        body_after = self.body.get_state()
        env_feedback = self.env.step(body_after)
        return {
            "body_before": body_before,
            "body_after": body_after,
            "body_delta": result_body,
            "env_feedback": env_feedback
        }

    def set_precision(self, gain: float):
        self._precision_gain = float(gain)

    def observe(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        item = WMItem(id=uuid4(), type="observation", content=str(observation), activation=1.0)
        self.working_memory.add_item(item)
        return observation

    def update_model(self, observation: Dict[str, Any], precision_gain: float = 1.0, emotion_signal: float = 0.0):
        body_before = observation.get("body_before", {})
        body_after = observation.get("body_after", {})
        self.episodic_memory.add_episode(
            description="embodied-cycle",
            context="NaturalEnv",
            body_before=body_before,
            body_after=body_after,
            emotion_signal=emotion_signal
        )

    def step(self, perception: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self.cycle += 1
        if perception:
            item = WMItem(id=uuid4(), type="perception", content=str(perception), activation=1.0)
            self.working_memory.add_item(item)

        expectations = self.generate_expectation(perception)
        action = self.select_action()

        # Add action to working memory
        action_item = WMItem(id=uuid4(), type="action", content=str(action), activation=1.0)
        self.working_memory.add_item(action_item)

        result = self.apply_action(action)

        b_before = result.get("body_before", {})
        b_after = result.get("body_after", {})
        arousal = math.sqrt((b_after.get("x",0)-b_before.get("x",0))**2 + (b_after.get("y",0)-b_before.get("y",0))**2)
        precision_gain = 1.0 + min(1.0, arousal)
        self.set_precision(precision_gain)

        observation = result
        self.observe(observation)
        self.update_model(observation, precision_gain=precision_gain, emotion_signal=arousal)

        return {
            "cycle": self.cycle,
            "perception": perception,
            "expectations": expectations,
            "action": action,
            "result": result,
            "precision_gain": precision_gain
        }
