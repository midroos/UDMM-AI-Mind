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
from ..affect.emotion import EmotionModel
from ..goals.attractor import AttractorModel

def utcnow_iso():
    return datetime.now(timezone.utc).isoformat()

class UDMMAgent:
    def __init__(self, env: Optional[NaturalEnv] = None):
        self.working_memory = WorkingMemory()
        self.episodic_memory = EpisodicMemory()
        self.semantic_memory = SemanticMemory()
        self.body = BodyModel()
        self.env = env or NaturalEnv()
        self.emotion_model = EmotionModel(alpha=0.9, max_gain=3.0)
        self.attractor: Optional[AttractorModel] = None
        self._precision_gain = 1.0
        self.cycle = 0
        self._last_expectation = {}
        self._last_observation = {}
        self._last_prediction_error = 0.0
        self._metrics = {"prediction_error": [], "precision_gain": [], "rule_confidence": []}

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
        self._last_expectation = exp  # Store for use in update_model
        return exp

    def set_attractor(self, x: float, y: float, weight: float = 1.0):
        self.attractor = AttractorModel(target_x=x, target_y=y, weight=weight)

    def select_action(self, intentions: Optional[List[Any]] = None) -> Dict[str, Any]:
        gain = getattr(self, "_precision_gain", 1.0)
        if self.body.energy < 0.15:
            return {"type": "idle"}

        if self.attractor:
            current_pos = self.body.get_state()
            dx = self.attractor.target_x - current_pos["x"]
            dy = self.attractor.target_y - current_pos["y"]

            target_angle_rad = math.atan2(dy, dx)
            target_angle_deg = math.degrees(target_angle_rad)

            current_angle_deg = self.body.orientation_deg
            angle_diff = (target_angle_deg - current_angle_deg + 180) % 360 - 180

            if abs(angle_diff) > 5.0: # Turn if not facing the target
                return {"type": "turn", "angle": angle_diff * 0.5} # Turn halfway
            else: # Move if facing the target
                dist = self.attractor.distance(current_pos)
                pull = self.attractor.pull_strength(current_pos)
                # Step size is proportional to pull strength, but capped by max_step
                effective_step = self.body.max_step * min(1.0, pull)
                step = min(dist, effective_step * gain)
                return {"type": "move_forward", "step": step}

        # Default exploratory action if no attractor
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
        attractor_boost = 1.0
        if self.attractor:
            pull = self.attractor.pull_strength(self.body.get_state())
            attractor_boost = 1.0 + 0.5 * min(1.0, pull) # Boost up to 50%

        self._precision_gain = float(gain) * attractor_boost

    def observe(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        item = WMItem(id=uuid4(), type="observation", content=str(observation), activation=1.0)
        self.working_memory.add_item(item)
        return observation

    def update_model(self, observation: Dict[str, Any], reward: Optional[float] = None):
        """
        Active-Inference style update:
        - compute prediction_error between last predicted_body_state and observed body_after
        - compute emotion signal (precision) from body deltas and prediction error
        - update semantic memory rule confidences or edge weights proportionally to (learning_rate * precision_gain * prediction_error)
        """
        try:
            predicted_state = self._last_expectation.get("predicted_body_state", {})
            observed_body = observation.get("body_after", {})
            px, py = predicted_state.get("x", 0.0), predicted_state.get("y", 0.0)
            ox, oy = observed_body.get("x", 0.0), observed_body.get("y", 0.0)
            pred_err = ((px - ox)**2 + (py - oy)**2)**0.5
        except Exception:
            pred_err = 0.0

        em = self.emotion_model.compute(observation.get("body_before", {}), observed_body, pred_err, reward_signal=(reward or 0.0))
        self.set_precision(em.precision_gain)

        learning_rate = 0.05 * em.precision_gain
        try:
            last_perc_item = next((item for item in reversed(self.working_memory.items.values()) if item.type == "perception"), None)
            if last_perc_item:
                for concept_label in self.semantic_memory.search_labels_in_string(last_perc_item.content):
                    rule_ids = self.semantic_memory.rules_related_to_label(concept_label)
                    for rid in rule_ids:
                        r = self.semantic_memory.get_rule_by_id(rid)
                        if not r: continue
                        current_conf = r.get("confidence", 0.5)
                        direction = -1.0 if pred_err > 0.5 else 1.0
                        delta = learning_rate * direction * (1.0 - current_conf)
                        new_conf = max(0.0, min(1.0, current_conf + delta))
                        self.semantic_memory.set_rule_confidence(rid, new_conf)
        except Exception:
            pass

        self.episodic_memory.add_episode(
            description="embodied-update-cycle",
            context=self.env.__class__.__name__,
            perception=self._last_observation.get("perception"),
            action=str(self._last_observation.get("action")),
            result=observation,
            body_before=observation.get("body_before", {}),
            body_after=observed_body,
            emotion_signal=em.arousal
        )
        # Log metrics for this cycle
        self._metrics["prediction_error"].append(pred_err)
        self._metrics["precision_gain"].append(em.precision_gain)

        self._last_observation = observation
        self._last_prediction_error = pred_err

    def get_metrics(self) -> dict:
        return dict(self._metrics)

    def step(self, perception: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self.cycle += 1
        if perception:
            item = WMItem(id=uuid4(), type="perception", content=str(perception), activation=1.0)
            self.working_memory.add_item(item)
            self._last_observation = {"perception": perception} # Store perception

        expectations = self.generate_expectation(perception)
        action = self.select_action()

        action_item = WMItem(id=uuid4(), type="action", content=str(action), activation=1.0)
        self.working_memory.add_item(action_item)
        self._last_observation["action"] = action # Store action

        result = self.apply_action(action)

        observation = result
        self.observe(observation)

        # update_model now computes its own emotion signal
        self.update_model(observation)

        return {
            "cycle": self.cycle,
            "perception": perception,
            "expectations": expectations,
            "action": action,
            "result": result,
            "precision_gain": self._precision_gain,
            "prediction_error": self._last_prediction_error
        }
