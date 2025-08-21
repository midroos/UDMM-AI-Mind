def test_imports():
    import udmm2
    from udmm2.agent.agent import UDMMAgent
    from udmm2.linguistic.linguistic_understanding import LinguisticUnderstanding
    from udmm2.simulation.gsm import GenerativeSimulator
    from udmm2.envs.natural_env import NaturalEnv

    agent = UDMMAgent()
    env = NaturalEnv()

    # Test that the agent and its components can be initialized
    assert isinstance(agent, UDMMAgent)
    assert isinstance(agent.linguistic_understanding, LinguisticUnderstanding)
    assert isinstance(agent.generative_simulator, GenerativeSimulator)

    # Test the basic agent API
    state = env.step(body_state={})
    agent.perceive(state)

    # Provide a dummy list of actions
    action = agent.choose_action(["move", "turn"])
    assert isinstance(action, str)

    # Test the learn method
    agent.learn(action, 1.0, {})
