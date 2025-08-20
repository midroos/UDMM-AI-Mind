from typing import Dict, Any, List
from ..agent.agent import UDMMAgent
from ..envs.natural_env import NaturalEnv

class ExperimentRunner:
    def __init__(self, env: NaturalEnv | None = None, steps: int = 50):
        self.env = env or NaturalEnv(objects=[])
        self.steps = int(steps)

    def run(self, agent: UDMMAgent, perceptions: List[Dict[str,Any]] | None = None) -> Dict[str, Any]:
        perceptions = perceptions or [{} for _ in range(self.steps)]
        for i in range(self.steps):
            agent.step(perception=perceptions[i] if i < len(perceptions) else {})
        # The agent needs a get_metrics method for this to work
        if hasattr(agent, "get_metrics"):
            return agent.get_metrics()
        return {}
