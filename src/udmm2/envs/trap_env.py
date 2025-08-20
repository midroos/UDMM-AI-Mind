class TrapEnv:
    def observe(self):
        return {"objects": ["trap", "wall"], "risk": "high", "distance": 2.0}

    def actions(self):
        return ["avoid", "disarm_trap", "get_reward"]
