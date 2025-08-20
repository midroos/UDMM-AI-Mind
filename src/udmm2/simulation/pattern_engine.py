from typing import Dict, Any, Tuple
from udmm2.memory.long_term_memory import LongTermMemory

class PatternEngine:
    def __init__(self, ltm: LongTermMemory):
        self.ltm = ltm

    def estimate(self, state: Dict[str, Any], action: str) -> Tuple[float, float, float]:
        # تقدير بدائي: يعتمد على وجود مفاهيم/قواعد معروفة
        novelty = 1.0 - min(1.0, self.ltm.knownness(state))
        risk = 0.5 if "hot" in str(state).lower() else 0.2
        reward = 0.6 if "reward" in str(state).lower() or action.startswith("get") else 0.4
        return novelty, risk, reward
