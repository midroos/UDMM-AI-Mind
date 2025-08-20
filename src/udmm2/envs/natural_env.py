from typing import Dict, Any, List, Tuple
from math import hypot

class NaturalEnv:
    """
    Simple 2D grid-like environment.
    The environment doesn't enforce collisions for now.
    It can return exteroceptive cues (nearby objects within radius).
    """

    def __init__(self, objects: List[Dict[str, Any]] | None = None):
        # objects: dicts like {"id": "rock1", "x": 2.0, "y": 1.0, "tags": ["rock"]}
        self.objects = objects or []
        self.sense_radius = 2.0

    def step(self, body_state: Dict[str, float]) -> Dict[str, Any]:
        """
        Given a body state (with x,y), return exteroceptive feedback:
        - nearby: list of object ids within sense_radius
        - distances: mapping id -> distance
        """
        x = float(body_state.get("x", 0.0))
        y = float(body_state.get("y", 0.0))
        nearby = []
        distances = {}
        for obj in self.objects:
            ox = float(obj.get("x", 0.0))
            oy = float(obj.get("y", 0.0))
            d = hypot(ox - x, oy - y)
            distances[obj.get("id")] = d
            if d <= self.sense_radius:
                nearby.append({"id": obj.get("id"), "tags": obj.get("tags", []), "distance": d})
        return {
            "nearby": nearby,
            "distances": distances,
            "terrain": "plain"
        }

    def add_object(self, obj: Dict[str, Any]) -> None:
        self.objects.append(obj)
