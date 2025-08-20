import pytest
import math
from udmm2.agent.body_model import BodyModel

@pytest.fixture
def body():
    """Provides a default BodyModel instance for each test."""
    return BodyModel()

def test_body_initial_state(body: BodyModel):
    state = body.get_state()
    assert state["position"]["x"] == 0.0
    assert state["position"]["y"] == 0.0
    assert state["orientation"] == 0.0
    assert state["energy"] == 100.0

def test_body_move(body: BodyModel):
    # Move 1 unit along the x-axis (angle = 0)
    dx, dy = body.move(1.0)
    assert dx == 1.0
    assert dy == 0.0
    assert body.x == 1.0
    assert body.y == 0.0
    # Check energy consumption
    assert body.energy < 100.0

def test_body_rotate_and_move(body: BodyModel):
    # Rotate 90 degrees (pi/2 radians)
    body.rotate(math.pi / 2)
    assert body.angle == pytest.approx(math.pi / 2)

    # Move 1 unit along the new y-axis
    dx, dy = body.move(1.0)
    assert dx == pytest.approx(0.0)
    assert dy == pytest.approx(1.0)
    assert body.x == pytest.approx(0.0)
    assert body.y == pytest.approx(1.0)

def test_adjust_energy(body: BodyModel):
    body.adjust_energy(-20)
    assert body.energy == 80.0
    body.adjust_energy(30)
    assert body.energy == 110.0
    # Test energy doesn't go below zero
    body.adjust_energy(-200)
    assert body.energy == 0.0
