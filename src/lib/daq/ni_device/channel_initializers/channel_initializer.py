import nidaqmx
from abc import ABC, abstractmethod


class ChannelInitializer(ABC):
    @abstractmethod
    def add_channel(self, task: nidaqmx.Task, physical_channel: str, **kwargs) -> None:
        pass
