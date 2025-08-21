from udmm2.agent.legacy_agent import LegacyUDMMAgent
from udmm2.envs.natural_env import NaturalEnv
from udmm2.goals.attractor import AttractorModel

def demo():
    env = NaturalEnv(objects=[])
    agent = LegacyUDMMAgent(env=env)

    # set a hierarchical attractor at (5,5) with 4 sub-steps
    attractor = AttractorModel(target_x=5.0, target_y=5.0)
    hi = agent.set_hierarchical_attractor(attractor, n_steps=4)

    print("--- Starting Hierarchical Intent Demo ---")
    print(f"Ultimate Goal: ({attractor.target_x}, {attractor.target_y})")
    print("Generated Subgoals:", [(round(s.target_x, 2), round(s.target_y, 2)) for s in hi.subgoals])
    print("-" * 20)

    for i in range(50): # Max steps
        out = agent.step(perception={})
        st = agent.body.get_state()
        print(f"Step {i+1:02d}: pos=({st['x']:.2f}, {st['y']:.2f}) | orientation={st['orientation_deg']:.1f}° | energy={st['energy']:.2f} | current_subgoal_idx={agent.hierarchical_intent.current_index}")

        if agent.hierarchical_intent.is_finished():
            print("\n--- All subgoals completed. Reached final goal. ---")
            break

if __name__ == "__main__":
    demo()
