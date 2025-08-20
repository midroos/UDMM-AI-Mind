from typing import List, Dict
from uuid import UUID, uuid4
from .api_models import EmbodiedExperienceIn, EmbodiedExperienceOut, utcnow

class EmbodiedMemory:
    def __init__(self):
        self.experiences: Dict[UUID, EmbodiedExperienceOut] = {}

    def add_experience(self, exp_in: EmbodiedExperienceIn) -> EmbodiedExperienceOut:
        """Adds a new embodied experience to the memory."""
        eid = uuid4()
        exp_out = EmbodiedExperienceOut(
            id=eid,
            timestamp=utcnow(),
            **exp_in.model_dump()
        )
        self.experiences[eid] = exp_out
        return exp_out

    def list_experiences(self, limit: int = 50) -> List[EmbodiedExperienceOut]:
        """Returns a list of the most recent embodied experiences."""
        sorted_exp = sorted(self.experiences.values(), key=lambda exp: exp.timestamp, reverse=True)
        return sorted_exp[:limit]
