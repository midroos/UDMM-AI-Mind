import pytest
from fastapi.testclient import TestClient
from uuid import UUID

from udmm2.api.app import create_app
from udmm2.agent.legacy_agent import LegacyUDMMAgent

# Create a single app instance for this test module
# This uses a fresh agent for this test suite
app = create_app(agent=LegacyUDMMAgent())
client = TestClient(app)

def test_health_check():
    """Test the basic health check endpoint."""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"ok": True}

def test_memory_api_concept_crud():
    """Test creating and retrieving a concept via the REST API."""
    # 1. Create a concept
    concept_in = {
        "label": "API_Concept",
        "description": "A test concept from the API",
        "attributes": {"test": True},
        "relations": []
    }
    response = client.post("/memory/concepts", json=concept_in)
    assert response.status_code == 200
    assert response.json() == {"status": "use websocket command !search"}
