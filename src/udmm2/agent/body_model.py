import math
from typing import Dict, Any

class BodyModel:
    """
    Represents the agent's physical state in a simple simulated 2D space.
    """
    def __init__(self, x: float = 0.0, y: float = 0.0, angle: float = 0.0, energy: float = 100.0):
        """
        Initializes the body model.

        Args:
            x: Initial x-coordinate.
            y: Initial y-coordinate.
            angle: Initial orientation angle in radians.
            energy: Initial energy level.
        """
        self.x = x
        self.y = y
        self.angle = angle  # in radians
        self.energy = energy

    def move(self, distance: float):
        """
        Moves the agent forward by a given distance along its current orientation.

        Args:
            distance: The distance to move.
        """
        dx = distance * math.cos(self.angle)
        dy = distance * math.sin(self.angle)
        self.x += dx
        self.y += dy
        # Moving consumes energy
        self.adjust_energy(-abs(distance) * 0.5)
        return dx, dy

    def rotate(self, dtheta: float):
        """
        Rotates the agent by a given angle.

        Args:
            dtheta: The angle to rotate by, in radians.
        """
        self.angle = (self.angle + dtheta) % (2 * math.pi)
        # Rotating also consumes a small amount of energy
        self.adjust_energy(-abs(dtheta) * 0.1)

    def adjust_energy(self, delta: float):
        """
        Adjusts the agent's energy level.

        Args:
            delta: The amount to change the energy by (can be negative).
        """
        self.energy = max(0, self.energy + delta)

    def get_state(self) -> Dict[str, Any]:
        """
        Returns a dictionary representing the current state of the body.
        """
        return {
            "position": {"x": self.x, "y": self.y},
            "orientation": self.angle,
            "energy": self.energy,
        }
