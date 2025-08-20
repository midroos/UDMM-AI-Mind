from typing import List, Dict, Any
from udmm2.core.body_model import BodyModel
from udmm2.core.self_identity import SelfIdentity
from udmm2.simulation.hybrid_sim import HybridSimulator

class GenerativeSimulator:
    def __init__(self, body_model: BodyModel, lu):
        self.body_model = body_model
        self.hybrid = HybridSimulator(body_model, lu.mem)

    def propose_action(self, state: Dict[str, Any], actions: List[str], identity: SelfIdentity) -> str:
        scored = []
        for a in actions:
            reward, risk, effort = self.hybrid.quick_evaluate(state, a, identity)
            score = reward - (risk * (1.0 - identity.risk_tolerance)) - effort
            scored.append((score, a))
        scored.sort(reverse=True)
        return scored[0][1] if scored else (actions[0] if actions else "noop")

    def learn(self, action: str, reward: float, next_state: Dict[str, Any]) -> None:
        # TODO: تغذية راجعة لتحديث القواعد/الأوزان
        pass
