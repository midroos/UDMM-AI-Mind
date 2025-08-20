from dataclasses import dataclass

@dataclass
class BodyModel:
    mass: float = 70.0
    max_force: float = 500.0
    size: tuple = (0.5, 0.3, 1.7)
    grip_strength: float = 0.6
    caution_bias: float = 0.5

    def effort_cost(self, distance: float) -> float:
        return distance * self.mass * 0.01
