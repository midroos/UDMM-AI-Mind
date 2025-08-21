import pytest
from fastapi.testclient import TestClient

from udmm2.api.app import create_app
from udmm2.envs.natural_env import NaturalEnv
from udmm2.agent.agent import UDMMAgent
from udmm2.goals.attractor import AttractorModel

class DummySemanticMemory:
    def __init__(self):
        self.added = []
    def add_concept(self, label, description=None, attributes=None, relations=None, confidence=0.9):
        self.added.append((label, attributes or {}))

from pydantic import BaseModel

class DummyWebResult(BaseModel):
    title: str
    url: str
    content: str

class DummyWebModule:
    def search(self, query: str, k: int = 1):
        return [DummyWebResult(title=f"Mock result for {query}", url="http://mock.com", content="mock content")]

    def to_concepts(self, results):
        return [{"label": r.title, "description": r.content} for r in results]

@pytest.fixture
def agent():
    env = NaturalEnv(objects=[])
    ag = UDMMAgent(env=env)
    # Attach dummy semantic memory for test isolation
    ag.semantic_memory = DummySemanticMemory()
    ag.web = DummyWebModule()
    return ag

def test_ws_search_command(agent):
    app = create_app(agent=agent)
    client = TestClient(app)
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_text("!search cognitive architectures")
        # The app should broadcast two messages: the user echo and the search results
        # We listen for the search results
        for _ in range(2):
            msg = ws.receive_json()
            if msg.get("type") == "search_results":
                assert msg["query"] == "cognitive architectures"
                assert len(msg["results"]) > 0
                assert len(agent.semantic_memory.added) >= 1
                return
        pytest.fail("Did not receive search_results message from WebSocket")

def test_ws_goal_command(agent):
    app = create_app(agent=agent)
    client = TestClient(app)
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_text("!goal 2.0 1.0")
        # The app should broadcast two messages: user echo and intent confirmation
        for _ in range(2):
            msg = ws.receive_json()
            if msg.get("type") == "intent":
                assert "target set to (2.0,1.0)" in msg["text"]
                # Check that the agent's attractor was actually set
                assert agent.hierarchical_intent is not None
                assert agent.hierarchical_intent.ultimate_attractor.target_x == 2.0
                return
        pytest.fail("Did not receive intent confirmation message from WebSocket")
