import matplotlib.pyplot as plt
from udmm2.agent.legacy_agent import LegacyUDMMAgent
from udmm2.envs.natural_env import NaturalEnv
from udmm2.experiment.runner import ExperimentRunner

def main():
    env = NaturalEnv(objects=[{"id":"food","x":1.0,"y":0.0,"tags":["food"]}])
    agent = LegacyUDMMAgent(env=env)

    # seed a simple rule for 'food'
    try:
        agent.semantic_memory.add_rule(conditions=["near(concept('food'))"], actions=["approach"], priority=1, confidence=0.3, source="experiential")
    except Exception as e:
        print(f"Could not seed rule (this might be ok if method name changed): {e}")

    # Run experiment
    runner = ExperimentRunner(env=env, steps=60)
    # Provide a consistent perception to see how the agent learns about it
    perceptions = [{"objects": ["food"]}] * 60
    metrics = runner.run(agent, perceptions=perceptions)

    # Plotting
    if not metrics or not metrics.get("prediction_error"):
        print("No metrics recorded, cannot generate plots.")
        return

    t_err = range(len(metrics.get("prediction_error", [])))
    t_gain = range(len(metrics.get("precision_gain", [])))
    t_conf = range(len(metrics.get("rule_confidence", [])))

    plt.figure(figsize=(12, 8))

    plt.subplot(3, 1, 1)
    plt.plot(t_err, metrics.get("prediction_error", []), label="prediction_error", color='r')
    plt.xlabel("Step")
    plt.ylabel("Error")
    plt.legend()
    plt.title("Learning Dynamics Over Time")

    plt.subplot(3, 1, 2)
    plt.plot(t_gain, metrics.get("precision_gain", []), label="precision_gain", color='g')
    plt.xlabel("Step")
    plt.ylabel("Gain")
    plt.legend()

    if metrics.get("rule_confidence"):
        plt.subplot(3, 1, 3)
        plt.plot(t_conf, metrics["rule_confidence"], label="rule_confidence", color='b')
        plt.xlabel("Update Index")
        plt.ylabel("Confidence")
        plt.legend()

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
