class NaturalEnv:
    def observe(self):
        return {"terrain": "forest", "weather": "sunny", "distance": 1.5, "near": ["water", "fruit"]}

    def actions(self):
        return ["move", "gather_fruit", "drink_water"]
