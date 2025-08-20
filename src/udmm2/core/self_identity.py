from dataclasses import dataclass

@dataclass
class SelfIdentity:
    curiosity: float = 0.5
    risk_tolerance: float = 0.5
    values: dict = None

    def update_from_language(self, deltas: dict) -> None:
        self.curiosity = max(0.0, min(1.0, deltas.get("curiosity", self.curiosity)))
        self.risk_tolerance = max(0.0, min(1.0, deltas.get("risk_tolerance", self.risk_tolerance)))
        if deltas.get("values"):
            self.values = {**(self.values or {}), **deltas["values"]}
