from typing import List
from udmm2.linguistic.schemas import EpisodicSnapshot

class EpisodicMemory:
    def __init__(self):
        self.snaps: List[EpisodicSnapshot] = []

    def add(self, snap: EpisodicSnapshot) -> None:
        self.snaps.append(snap)
