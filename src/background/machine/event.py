from enum import Enum, auto


class Event(Enum):
    DataUpdate      : int = auto()
    FaultDetect     : int = auto()
