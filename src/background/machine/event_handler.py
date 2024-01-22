from typing import Dict
from abc import ABC, abstractmethod

from .event import Event


class EventHandler(ABC):
    @abstractmethod
    async def event_handle(self, event: Event, data: Dict) -> None:
        pass
