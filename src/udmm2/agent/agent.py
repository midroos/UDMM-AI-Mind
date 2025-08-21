from typing import Any, Dict, List
from udmm2.core.self_identity import SelfIdentity
from udmm2.core.body_model import BodyModel
from udmm2.linguistic.linguistic_understanding import LinguisticUnderstanding
from udmm2.simulation.gsm import GenerativeSimulator

class UDMMAgent:
    def __init__(self, body_config: Dict[str, Any] | None = None):
        self.identity = SelfIdentity()
        self.body_model = BodyModel(**(body_config or {}))
        self.linguistic_understanding = LinguisticUnderstanding()
        self.generative_simulator = GenerativeSimulator(self.body_model, self.linguistic_understanding)

        self.state: Dict[str, Any] = {}

    def perceive(self, world_perception: Dict[str, Any]) -> None:
        self.state.update(world_perception)

    def ingest_text(self, text: str) -> None:
        deltas = self.linguistic_understanding.ingest_text(text)
        if deltas:
            self.identity.update_from_language(deltas)

    def choose_action(self, available_actions: List[str]) -> str:
        return self.generative_simulator.propose_action(self.state, available_actions, self.identity)

    def learn(self, action: str, reward: float, next_state: Dict[str, Any]) -> None:
        self.generative_simulator.learn(action, reward, next_state)
        self.state.update(next_state)
