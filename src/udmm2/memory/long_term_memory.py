from typing import Dict, List
from udmm2.linguistic.schemas import Concept, Rule

class LongTermMemory:
    def __init__(self):
        self.concepts: Dict[str, Concept] = {}
        self.rules: Dict[str, Rule] = {}

    def add_concept(self, c: Concept) -> None:
        self.concepts[c.id] = c

    def add_rule(self, r: Rule) -> None:
        self.rules[r.id] = r

    def knownness(self, state: dict) -> float:
        text = str(state).lower()
        hits = sum(1 for c in self.concepts.values() if c.label in text)
        return min(1.0, hits / max(1, len(self.concepts)))
