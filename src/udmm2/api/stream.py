from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Any
from uuid import UUID

from ..agent.agent import UDMMAgent

router = APIRouter(prefix="/stream", tags=["Streaming"])

# The WebSocket gets its own instance of the agent to maintain state per-session.
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
    # Create a new agent instance for each WebSocket session
    agent = UDMMAgent()
    try:
        while True:
            data = await ws.receive_json()
            out: Dict[str, Any] = agent.step(data)

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
