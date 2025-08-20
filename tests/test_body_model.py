import pytest
import math
from udmm2.body.body_model import BodyModel

def test_move_and_turn():
    b = BodyModel(x=0.0, y=0.0, orientation_deg=0.0, energy=1.0)

    # Test move
    res = b.move_forward(1.0)
    assert res["dx"] == pytest.approx(1.0)
    assert res["dy"] == pytest.approx(0.0)
    assert b.x == pytest.approx(1.0)
    assert 0.0 <= b.energy < 1.0

    # Test turn
    t_res = b.turn(90)
    assert t_res["dtheta"] == 90.0
    assert b.orientation_deg == 90.0

    # Test move after turning
    res2 = b.move_forward(1.0)
    assert res2["dx"] == pytest.approx(0.0)
    assert res2["dy"] == pytest.approx(1.0)
    assert b.x == pytest.approx(1.0)
    assert b.y == pytest.approx(1.0)

def test_get_state(body: BodyModel = BodyModel()):
    state = body.get_state()
    assert "x" in state
    assert "y" in state
    assert "orientation_deg" in state
    assert "energy" in state
    assert "timestamp" in state
