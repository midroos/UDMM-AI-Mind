from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Dict
from math import copysign

def utcnow():
    return datetime.now(timezone.utc)

class EmotionSignal(BaseModel):
    arousal: float = 0.0   # 0..+inf, bounded in practice
    valence: float = 0.0   # -1..+1
    precision_gain: float = 1.0
    timestamp: datetime = Field(default_factory=utcnow)

class EmotionModel:
    """
    Compute emotion signal from body deltas + prediction error.
    - arousal is driven by magnitude of body change + surprise
    - valence can be approximated from directionality: improvement vs degradation (negative vs positive reward)
    - precision_gain = 1.0 + clamp(arousal, 0, 2) * alpha (alpha small)
    """
    def __init__(self, alpha: float = 0.8, max_gain: float = 3.0):
        self.alpha = float(alpha)
        self.max_gain = float(max_gain)

    @staticmethod
    def body_arousal(body_before: Dict, body_after: Dict) -> float:
        dx = body_after.get("x", 0.0) - body_before.get("x", 0.0)
        dy = body_after.get("y", 0.0) - body_before.get("y", 0.0)
        energy_delta = body_after.get("energy", 0.0) - body_before.get("energy", 0.0)
        spatial = (dx*dx + dy*dy) ** 0.5
        # combine spatial movement and absolute energy change
        return spatial + abs(energy_delta)

    def compute(self, body_before: Dict, body_after: Dict, prediction_error: float, reward_signal: float = 0.0) -> EmotionSignal:
        # base arousal from body
        ar = self.body_arousal(body_before, body_after)
        # surprise contribution
        surprise = abs(prediction_error)
        ar_total = ar + 0.5 * surprise
        # valence: use reward_signal (positive -> positive valence), reward may be None
        val = float(reward_signal)
        # precision gain mapping (nonlinear soft clamp)
        gain = 1.0 + min(self.max_gain - 1.0, self.alpha * ar_total)
        return EmotionSignal(arousal=ar_total, valence=val, precision_gain=gain)
