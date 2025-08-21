from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from uuid import UUID
# The new agent doesn't use the GoalManager/Intentionality models directly in its step
# from ..intent.api_models import GoalIn, GoalOut, AttractorConfig
# from ..intent.goal_service import GoalManager
from ..agent.legacy_agent import LegacyUDMMAgent

router = APIRouter(prefix="/agent", tags=["Agent"])

# Singleton agent for the API
_agent = LegacyUDMMAgent()

@router.post("/step", summary="Run one full agent cycle")
def agent_step(perception: Dict[str, Any]):
    """
    Run one full embodied step of the agent.

    - **perception**: A dictionary of sensory inputs, e.g., `{"objects": ["tree"]}`.
    - **Returns**: A summary of the cognitive cycle.
    """
    # The new agent step is self-contained
    return _agent.step(perception)

# Commenting out goal-related endpoints as they are not compatible
# with the latest agent refactor. This can be added back later.
# _gm = GoalManager()
# @router.post("/goals", response_model=GoalOut)
# def create_goal(payload: GoalIn):
#     return _gm.add_goal(payload)
# ... and so on
