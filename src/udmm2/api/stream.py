from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Any

# Re-using the same pattern of singletons for the stream
from ..intent.goal_service import GoalManager
from ..agent.agent import UDMMAgent
from ..agent.agent_intent_integration import AgentIntentBridge

router = APIRouter(prefix="/stream", tags=["Streaming"])

# The WebSocket gets its own instances of the agent components
# to avoid state conflicts with the REST API for this demo.
_stream_gm = GoalManager()
_stream_agent = UDMMAgent(name="Stream-Agent")
_stream_bridge = AgentIntentBridge(agent=_stream_agent, goal_manager=_stream_gm)

@router.websocket("/cycle")
async def cycle_stream(ws: WebSocket):
    """
    Provides a live stream of the agent's cognitive cycle.

    - **Connect**: Establish a WebSocket connection to this endpoint.
    - **Send**: Send a JSON object representing a perception, e.g., `{"object": "rock"}`.
    - **Receive**: The server will respond with a full snapshot of the cognitive
      cycle triggered by your perception.
    """
    await ws.accept()
    try:
        while True:
            # Expect a perception dict from client each tick
            data = await ws.receive_json()
            out: Dict[str, Any] = _stream_bridge.step_with_intentions(data)

            # Convert UUIDs to strings for JSON serialization
            def make_json_safe(d):
                for k, v in d.items():
                    if isinstance(v, UUID):
                        d[k] = str(v)
                    elif isinstance(v, dict):
                        make_json_safe(v)
                    elif isinstance(v, list):
                        for item in v:
                            if isinstance(item, dict):
                                make_json_safe(item)
                return d

            await ws.send_json(make_json_safe(out))
    except WebSocketDisconnect:
        print("Client disconnected from cycle stream.")
        pass
