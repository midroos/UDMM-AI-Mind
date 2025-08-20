from typing import Dict, Any, Tuple
from udmm2.core.body_model import BodyModel
from udmm2.memory.long_term_memory import LongTermMemory
from udmm2.simulation.pattern_engine import PatternEngine
from udmm2.simulation.embodied_engine import EmbodiedEngine

class HybridSimulator:
    def __init__(self, body_model: BodyModel, ltm: LongTermMemory):
        self.pattern = PatternEngine(ltm)
        self.embodied = EmbodiedEngine(body_model)

    def quick_evaluate(self, state: Dict[str, Any], action: str, identity) -> Tuple[float, float, float]:
        novelty, risk, reward = self.pattern.estimate(state, action)
        if novelty > 0.6 or risk > 0.6:
            reward_e, risk_e, effort = self.embodied.simulate(state, action)
            # دمج بسيط
            reward = (reward + reward_e) / 2
            risk = max(risk, risk_e)
            return reward, risk, effort
        return reward, risk, 0.05
