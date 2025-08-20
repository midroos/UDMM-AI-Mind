from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from uuid import UUID
from ..intent.api_models import GoalIn, GoalOut, AttractorConfig
from ..intent.goal_service import GoalManager
from ..agent.agent import UDMMAgent
from ..agent.agent_intent_integration import AgentIntentBridge

router = APIRouter(prefix="/intent", tags=["Intentionality"])

# Singletons (for demo scope)
# The GoalManager is now initialized by the bridge or can be passed in.
_gm = GoalManager()
# The agent's __init__ is now simpler.
_agent = UDMMAgent(name="API-Agent")
_bridge = AgentIntentBridge(agent=_agent, goal_manager=_gm)

@router.get("/attractor", response_model=AttractorConfig)
def get_attractor():
    return _gm.attractor

@router.post("/goals", response_model=GoalOut)
def create_goal(payload: GoalIn):
    return _gm.add_goal(payload)

@router.get("/goals", response_model=List[GoalOut])
def list_goals():
    return _gm.list_goals()

@router.delete("/goals/{goal_id}")
def delete_goal(goal_id: UUID):
    ok = _gm.delete_goal(goal_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Goal not found")
    return {"ok": True}

@router.post("/agent/step", summary="Run one full agent cycle")
def agent_step(perception: Dict[str, Any]):
    """
    Run one full intention-driven step of the agent.

    - **perception**: A dictionary of sensory inputs, e.g., `{"objects": ["tree"]}`.
    - **Returns**: A summary of the cognitive cycle, including intentions,
      actions, and the resulting change in body state and emotion.
    """
    return _bridge.step_with_intentions(perception)
