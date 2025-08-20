from __future__ import annotations
from typing import Dict, Any

from .agent import UDMMAgent
from ..intent.goal_service import GoalManager
from ..intent.api_models import PrecisionSignal
from ..memory.models import Episode

class AgentIntentBridge:
    """Bridges UDMMAgent with GoalManager for intention-driven steps."""
    def __init__(self, agent: UDMMAgent, goal_manager: GoalManager):
        self.agent = agent
        self.gm = goal_manager

    def step_with_intentions(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        # 1) perceive
        self.agent.perceive(perception)

        # 2) expectations (already integrated with SemanticMemory)
        expectations = self.agent.generate_expectation(perception)

        # 3) compute signals for discrepancy:
        # TODO: These signals should be computed based on actual model differences
        signals = {
            "prediction_error": float(expectations.get("prediction_error", 0.1)),
            "schema_activation": float(expectations.get("schema_activation", 0.5)),
            "body_deviation": float(self.agent.body.energy / 100.0 - 0.5) # Example
        }

        # 4) intentions from GM
        goals = self.gm.list_goals()
        intentions = self.gm.intentions_from_state(signals, goals)

        # 5) select action (modulated by intentions)
        action = self.agent.select_action(intentions=intentions)

        # 6) apply to body & get before/after
        body_before = self.agent.body.get_state()
        result = self.agent.apply_action(action)
        body_after = self.agent.body.get_state()

        # 7) emotion-as-precision
        ps: PrecisionSignal = self.gm.precision_from_body(body_before, body_after)
        self.agent.set_precision(ps.precision_gain)

        # 8) observe & update (store episode incl. emotion signal)
        observation = self.agent.observe(result)
        # The agent's own update_model is a placeholder, but we call it for consistency
        self.agent.update_model(observation, precision_gain=ps.precision_gain, emotion_signal=ps.arousal)

        # The bridge is responsible for creating the rich episode
        episode = Episode(
            context="agent_cycle_bridged",
            perception=perception,
            action=str(action),  # stringify action dict
            result=result,
            body_before=body_before,
            body_after=body_after,
            emotion_signal=ps.arousal
        )
        self.agent.episodic_memory.add_episode(episode)

        # 9) return cycle summary
        return {
            "perception": perception,
            "expectations": expectations,
            "intentions": [i.model_dump() for i in intentions],
            "action": action,
            "result": result,
            "body_before": body_before,
            "body_after": body_after,
            "precision": ps.model_dump()
        }
