from dataclasses import dataclass, asdict
from math import cos, sin, radians
from datetime import datetime, timezone

@dataclass
class BodyModel:
    x: float = 0.0
    y: float = 0.0
    orientation_deg: float = 0.0  # 0 = facing +x
    energy: float = 1.0  # 0..1
    max_step: float = 1.0

    def get_state(self) -> dict:
        return {
            "x": float(self.x),
            "y": float(self.y),
            "orientation_deg": float(self.orientation_deg),
            "energy": float(self.energy),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def move_forward(self, distance: float) -> dict:
        # clamp distance
        d = max(-self.max_step, min(self.max_step, float(distance)))
        rad = radians(self.orientation_deg)
        dx = d * cos(rad)
        dy = d * sin(rad)
        self.x += dx
        self.y += dy
        # energy cost proportional to distance
        self.energy = max(0.0, min(1.0, self.energy - abs(d) * 0.02))
        return {"dx": dx, "dy": dy, "energy_delta": -abs(d) * 0.02}

    def turn(self, angle_deg: float) -> dict:
        a = float(angle_deg)
        self.orientation_deg = (self.orientation_deg + a) % 360.0
        # small energy cost
        self.energy = max(0.0, min(1.0, self.energy - abs(a) * 0.0005))
        return {"dtheta": a, "energy_delta": -abs(a) * 0.0005}

    def adjust_energy(self, delta: float) -> dict:
        old = self.energy
        self.energy = max(0.0, min(1.0, self.energy + float(delta)))
        return {"energy_delta": self.energy - old}
