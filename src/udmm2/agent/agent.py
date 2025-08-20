import math
from typing import Any, Dict, List
from uuid import uuid4
from datetime import datetime, timezone

from .body_model import BodyModel
from .working_memory import WorkingMemory, WMItem
from ..memory.episodic_memory import EpisodicMemory
from ..memory.semantic_memory import SemanticMemory
from ..memory.models import Episode
# The agent itself no longer directly manages goals or intentions
from ..intent.api_models import Intention

class UDMMAgent:
    def __init__(self, name: str = "UDMMAgent"):
        self.name = name
        self.body = BodyModel()
        self.working_memory = WorkingMemory()
        self.episodic_memory = EpisodicMemory()
        self.semantic_memory = SemanticMemory()
        self.current_state = {}
        self._precision_gain = 1.0

    def perceive(self, inputs: Dict):
        self.current_state.update(inputs)
        self.current_state.update({"body": self.body.get_state()})
        perception_item = WMItem(type="perception", content=str(self.current_state))
        self.working_memory.add_item(perception_item)

    def generate_expectation(self, perception: Dict) -> Dict[str, List[str]]:
        expectations = {}
        for key, value in perception.items():
            if isinstance(value, str):
                related = self.semantic_memory.get_related(value)
                if related:
                    expectations[key + "_related"] = related
        return expectations

    def select_action(self, intentions: List[Intention]) -> Dict:
        # Simple selection: pick highest strength intention, or default explore
        if not intentions:
            return {"type": "explore", "step": 0.5 * self._precision_gain}

        # For now, just use the description as a cue
        best_intention = max(intentions, key=lambda i: i.strength)
        action_desc = best_intention.description.lower()

        if "refine" in action_desc:
            return {"type": "cognitive_focus", "target": "model"}
        else:
            # Scale movement by precision gain
            step_size = 1.0 * self._precision_gain
            return {"type": "move_forward", "step": step_size}

    def apply_action(self, action: dict) -> dict:
        """Applies a structured action to the body model."""
        kind = action.get("type", "noop")
        if kind == "move_forward":
            step = action.get("step", 1.0)
            self.body.move(step)
            return {"status": "ok", "info": f"moved forward by {step}"}
        elif kind == "rotate":
            angle = action.get("angle", 0.1)
            self.body.rotate(angle)
            return {"status": "ok", "info": f"rotated by {angle}"}
        return {"status": "noop", "info": "no physical action taken"}

    def observe(self, action_result: Dict) -> Dict:
        self.current_state.update(action_result)
        observation_item = WMItem(type="observation", content=str(action_result))
        self.working_memory.add_item(observation_item)
        return self.current_state

    def set_precision(self, gain: float):
        """Emotion-as-precision: modulates internal weighting."""
        self._precision_gain = float(gain)

    def update_model(self, observation: dict, precision_gain: float, emotion_signal: float):
        """The bridge calls this, but the agent itself doesn't do learning yet."""
        # This is where future learning logic would go, weighted by precision_gain.
        pass
