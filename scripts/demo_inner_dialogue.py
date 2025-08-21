from udmm2.agent.legacy_agent import LegacyUDMMAgent
from udmm2.envs.natural_env import NaturalEnv
from udmm2.goals.attractor import AttractorModel
import time

def demo():
    print("--- Starting Inner Dialogue Demo ---")
    env = NaturalEnv(objects=[])
    agent = LegacyUDMMAgent(env=env)

    attractor = AttractorModel(target_x=3.0, target_y=0.0)
    agent.set_hierarchical_attractor(attractor, n_steps=3)

    print(f"Agent created. Target set to ({attractor.target_x}, {attractor.target_y}) with 3 subgoals.")
    print("-" * 20)
    time.sleep(1)

    for i in range(15):
        # Clear history for this step to only show new utterances
        agent.dialogue.inner_history.clear()

        print(f"\n>>> Cycle {i+1}")
        out = agent.step(perception={})

        if agent.dialogue.inner_history:
            for utt in agent.dialogue.inner_history:
                print(f"  INNER DIALOGUE ({utt.trigger}): {utt.text}")
        else:
            print("  (No new inner dialogue triggered this step)")

        if agent.hierarchical_intent and agent.hierarchical_intent.is_finished():
            print("\n--- Final goal reached. ---")
            break

        time.sleep(0.5)

if __name__ == "__main__":
    demo()
