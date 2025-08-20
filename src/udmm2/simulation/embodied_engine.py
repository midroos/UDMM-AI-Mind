from typing import Dict, Any, Tuple
from udmm2.core.body_model import BodyModel

class EmbodiedEngine:
    def __init__(self, body_model: BodyModel):
        self.body = body_model

    def simulate(self, state: Dict[str, Any], action: str) -> Tuple[float, float, float]:
        distance = float(state.get("distance", 1.0))
        effort = self.body.effort_cost(distance)
        # تبسيط: كلما زادت المسافة زاد الجهد/المخاطرة وانخفضت المكافأة
        risk = min(1.0, 0.2 + distance * 0.1)
        reward = max(0.0, 0.7 - distance * 0.05)
        return reward, risk, effort
