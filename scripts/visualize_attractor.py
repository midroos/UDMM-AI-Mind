import matplotlib.pyplot as plt
from udmm2.agent.legacy_agent import LegacyUDMMAgent
from udmm2.envs.natural_env import NaturalEnv

def main():
    env = NaturalEnv(objects=[])
    agent = LegacyUDMMAgent(env=env)

    # Set the attractor
    attractor_pos = (5.0, 5.0)
    agent.set_attractor(x=attractor_pos[0], y=attractor_pos[1], weight=2.0)

    positions = []
    # Run the agent for enough steps to see the behavior
    for _ in range(50):
        agent.step()
        st = agent.body.get_state()
        positions.append((st["x"], st["y"]))
        # Stop if the agent is very close to the attractor
        if agent.attractor.distance(st) < 0.1:
            break

    xs, ys = zip(*positions)

    plt.figure(figsize=(8, 8))
    plt.plot(xs, ys, 'o-', label="agent path", markersize=4)
    plt.scatter([xs[0]], [ys[0]], color="green", s=100, zorder=5, label="start")
    plt.scatter([attractor_pos[0]], [attractor_pos[1]], color="red", s=200, zorder=5, marker='*', label="attractor")

    plt.xlabel("X Position")
    plt.ylabel("Y Position")
    plt.title("Agent Trajectory toward Virtual Attractor")
    plt.legend()
    plt.grid(True)
    plt.axis('equal')
    plt.show()

if __name__ == "__main__":
    main()
