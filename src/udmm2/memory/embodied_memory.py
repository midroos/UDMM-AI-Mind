from typing import List
from udmm2.linguistic.schemas import EmbodiedExperience

class EmbodiedMemory:
    def __init__(self):
        self.experiences: List[EmbodiedExperience] = []

    def add(self, exp: EmbodiedExperience) -> None:
        self.experiences.append(exp)
