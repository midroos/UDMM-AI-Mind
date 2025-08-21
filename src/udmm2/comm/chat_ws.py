from __future__ import annotations
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from pydantic import BaseModel
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
import json
import asyncio
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ws", tags=["ws"])

@dataclass
class WSClient:
    ws: WebSocket
    id: str

class CommHub:
    """
    Lightweight hub for broadcasting agent events (inner dialogue, state updates)
    and receiving user messages via WebSocket.
    """
    def __init__(self):
        self._clients: List[WSClient] = []
        self.on_user_message: Optional[Callable[[str], Any]] = None

    async def connect(self, ws: WebSocket, client_id: str):
        await ws.accept()
        self._clients.append(WSClient(ws=ws, id=client_id))
        await self._safe_send(ws, {"type":"system","text":"connected"})
        logger.info("WS connected: %s", client_id)

    def disconnect(self, ws: WebSocket):
        self._clients = [c for c in self._clients if c.ws != ws]
        logger.info("WS disconnected")

    async def broadcast(self, payload: Dict[str, Any]):
        dead = []
        for c in self._clients:
            try:
                await self._safe_send(c.ws, payload)
            except Exception:
                dead.append(c)
        if dead:
            for d in dead:
                self._clients.remove(d)

    async def _safe_send(self, ws: WebSocket, payload: Dict[str, Any]):
        try:
            await ws.send_text(json.dumps(payload, ensure_ascii=False))
        except RuntimeError:
            # closed
            pass

    # called by agent/dialogue layer:
    async def broadcast_ws(self, payload: Dict[str, Any]):
        await self.broadcast(payload)

# Singleton-ish hub (imported by app/agent)
comm_hub = CommHub()

@router.websocket("/chat")
async def ws_chat(ws: WebSocket):
    client_id = ws.headers.get("x-client-id") or "anon"
    await comm_hub.connect(ws, client_id)
    try:
        while True:
            data = await ws.receive_text()
            try:
                # raw string input from user; route to agent layer
                if comm_hub.on_user_message:
                    await comm_hub.on_user_message(data)
                # echo for UX
                await comm_hub.broadcast({"type":"user","text":data})
            except Exception:
                logger.exception("Failed processing user message")
    except WebSocketDisconnect:
        comm_hub.disconnect(ws)
    except Exception:
        comm_hub.disconnect(ws)
