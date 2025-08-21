from __future__ import annotations
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from uuid import uuid4
from datetime import datetime, timezone
import logging

# Forward reference for the agent to avoid circular imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..agent.legacy_agent import LegacyUDMMAgent

logger = logging.getLogger(__name__)

def utcnow_iso():
    return datetime.now(timezone.utc).isoformat()

class InnerUtterance(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    text: str
    trigger: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=utcnow_iso)

class DialogueManager:
    def __init__(self, agent: "LegacyUDMMAgent", prediction_error_threshold: float = 0.5, heartbeat_period: int = 10):
        self.agent = agent
        self.prediction_error_threshold = float(prediction_error_threshold)
        self.heartbeat_period = int(heartbeat_period)
        self._ticks = 0
        self.inner_history: list[InnerUtterance] = []

    def on_prediction_error(self, pred_err: float, context: Optional[Dict[str,Any]] = None) -> Optional[InnerUtterance]:
        if pred_err >= self.prediction_error_threshold:
            summary = self._compose_surprise(pred_err, context)
            utt = InnerUtterance(text=summary, trigger="prediction_error", metadata={"pred_err": pred_err, **(context or {})})
            self._record_and_inject(utt)
            return utt
        return None

    def on_subgoal_completed(self, subgoal: Any, context: Optional[Dict[str,Any]] = None) -> Optional[InnerUtterance]:
        txt = self._compose_subgoal_completion(subgoal)
        utt = InnerUtterance(text=txt, trigger="subgoal_completed", metadata={"subgoal": self._sg_to_dict(subgoal), **(context or {})})
        self._record_and_inject(utt)
        return utt

    def on_emotion_change(self, emotion_signal: Dict[str,Any], context: Optional[Dict[str,Any]] = None) -> Optional[InnerUtterance]:
        ar = float(emotion_signal.get("arousal", 0.0))
        val = float(emotion_signal.get("valence", 0.0))
        if ar < 0.1: return None # Don't report on minor fluctuations
        txt = self._compose_emotion_comment(ar, val)
        utt = InnerUtterance(text=txt, trigger="emotion_change", metadata={"emotion": emotion_signal, **(context or {})})
        self._record_and_inject(utt)
        return utt

    def heartbeat(self, context: Optional[Dict[str,Any]] = None) -> Optional[InnerUtterance]:
        self._ticks += 1
        if (self._ticks % self.heartbeat_period) != 0:
            return None
        summary = self._self_state_summary(context)
        utt = InnerUtterance(text=summary, trigger="heartbeat", metadata=context or {})
        self._record_and_inject(utt)
        return utt

    def _compose_surprise(self, pred_err: float, context: Optional[Dict[str,Any]] = None) -> str:
        return f"انحراف تنبؤي كبير: {pred_err:.3f}. يجب إعادة تقييم النموذج."

    def _compose_subgoal_completion(self, subgoal: Any) -> str:
        sg = self._sg_to_dict(subgoal)
        return f"أنجزت هدفًا فرعيًا عند ({sg.get('x'):.2f},{sg.get('y'):.2f})."

    def _compose_emotion_comment(self, arousal: float, valence: float) -> str:
        tone = "مستثار" if arousal > 1.0 else "متيقظ"
        return f"الحالة العاطفية: {tone} (تنبيه={arousal:.2f})."

    def _self_state_summary(self, context: Optional[Dict[str,Any]] = None) -> str:
        try:
            body = self.agent.body.get_state()
            hi = getattr(self.agent, "hierarchical_intent", None)
            goals_info = f"subgoal {hi.current_index}/{len(hi.subgoals)}" if hi and hi.subgoals else "no goal"
            pos = f"pos=({body.get('x', '?'):.2f},{body.get('y', '?'):.2f})"
            energy = f"energy={body.get('energy', '?'):.2f}"
            return f"ملخص ذاتي: {pos}, {energy}, {goals_info}."
        except Exception:
            return "ملخص ذاتي: فشل."

    def _sg_to_dict(self, sg: Any) -> Dict[str,Any]:
        if hasattr(sg, "target_x"):
            return {"x": sg.target_x, "y": sg.target_y, "concept": getattr(sg, "associated_concept", None)}
        return {}

    def _record_and_inject(self, utt: InnerUtterance):
        self.inner_history.append(utt)
        if self.agent and hasattr(self.agent, "episodic_memory"):
            try:
                # Align with the EpisodicMemory.add_episode(**kwargs) signature
                self.agent.episodic_memory.add_episode(
                    description=f"inner_dialogue: {utt.trigger}",
                    context="inner_dialogue",
                    perception={"text": utt.text, "metadata": utt.metadata},
                )
            except Exception:
                logger.exception("Failed to persist inner utterance to episodic memory.")
