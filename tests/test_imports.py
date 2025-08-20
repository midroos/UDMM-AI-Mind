def test_imports():
    import udmm2
    from udmm2.core.udmm_agent import UDMMv2Agent
    from udmm2.linguistic.linguistic_understanding import LinguisticUnderstanding
    from udmm2.simulation.gsm import GenerativeSimulator
    from udmm2.envs.natural_env import NaturalEnv

    agent = UDMMv2Agent()
    env = NaturalEnv()
    # The new NaturalEnv has a `step` method, not `observe`.
    # It also doesn't have an `actions` method. This test is becoming obsolete.
    # I will adapt it to the new interface for now.
    state = env.step(body_state={})
    agent.perceive(state)
    # The new env doesn't define actions, so I'll provide a dummy list.
    action = agent.choose_action(["move", "turn"])
    assert isinstance(action, str)
