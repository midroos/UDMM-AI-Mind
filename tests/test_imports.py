def test_imports():
    import udmm2
    from udmm2.core.udmm_agent import UDMMv2Agent
    from udmm2.linguistic.linguistic_understanding import LinguisticUnderstanding
    from udmm2.simulation.gsm import GenerativeSimulator
    from udmm2.envs.natural_env import NaturalEnv

    agent = UDMMv2Agent()
    env = NaturalEnv()
    state = env.observe()
    agent.perceive(state)
    action = agent.choose_action(env.actions())
    assert isinstance(action, str)
