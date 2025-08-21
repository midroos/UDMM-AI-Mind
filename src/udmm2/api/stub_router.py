# This file contains stub endpoints for testing the Streamlit UI.
# Provided by the user to accelerate development.

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
import asyncio
import json
import time
import random

router = APIRouter()

@router.post("/dialogue/chat")
async def dialogue_chat(payload: dict):
    user = payload.get("text","")
    return {"reply": f"سمعتك تقول: {user}. (ردّ مؤقت من الـ API)"}

_keys = {"google_api_key": False, "openai_api_key": False, "huggingface_api_key": False}

@router.get("/config/keys")
async def get_keys():
    return _keys

@router.post("/config/keys")
async def set_key(p: dict):
    svc = p.get("service"); key = p.get("key")
    if svc in _keys:
        _keys[svc] = True if key else False
    return {"status":"success"}

# A simple streaming endpoint for demonstration
@router.websocket("/stream")
async def stream(ws: WebSocket):
    await ws.accept()
    try:
        x, y, energy = 0.0, 0.0, 1.0
        while True:
            x += random.uniform(-0.1, 0.1)
            y += random.uniform(-0.1, 0.1)
            energy = max(0.0, min(1.0, energy - random.uniform(0.0, 0.01)))
            msg = {
                "type":"agent_cycle",
                "timestamp": time.time(),
                "body_after":{"x":x,"y":y,"energy":energy},
                "emotion_signal": random.uniform(0,1),
                "active_goals":[
                    {"id":"g-root","name":"Explore","status":"in_progress","progress":random.uniform(0,1),
                     "subgoals":[{"id":"g-1","name":"Scan A","status":"done","progress":1.0}]}
                ],
                "semantic_memory":{
                    "concepts":[{"id":"fire","label":"Fire"},{"id":"heat","label":"Heat"}],
                    "links":[{"source":"fire","target":"heat","type":"causes"}]
                }
            }
            await ws.send_text(json.dumps(msg))
            await asyncio.sleep(1.0)
    except WebSocketDisconnect:
        pass
