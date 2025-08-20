from typing import Dict, List, Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class WMItem(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    type: str  # concept, action, observation
    content: str
    activation: float = 1.0
    linked_items: List[UUID] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class WorkingMemory:
    def __init__(self):
        self.items: Dict[UUID, WMItem] = {}

    def add_item(self, item: WMItem) -> UUID:
        self.items[item.id] = item
        return item.id

    def link_items(self, source_id: UUID, target_id: UUID):
        if source_id in self.items and target_id in self.items:
            self.items[source_id].linked_items.append(target_id)

    def get_active_items(self, threshold: float = 0.5) -> List[WMItem]:
        return [item for item in self.items.values() if item.activation >= threshold]

    def decay_activation(self, rate: float = 0.1):
        for item in self.items.values():
            item.activation = max(0, item.activation - rate)
