from udmm2.agent.agent import UDMMAgent

def test_agent_basic_cycle():
    agent = UDMMAgent()
    result = agent.step()
    assert "cycle" in result
    assert result["cycle"] == 1
    assert "expectation" in result
    assert "action" in result
    assert "observation" in result
