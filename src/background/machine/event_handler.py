from typing import Dict
from abc import ABC, abstractmethod

from .machine_event import MachineEvent


class EventHandler(ABC):
    @abstractmethod
    async def event_handle(self, event: MachineEvent, data: Dict) -> None:
        pass
