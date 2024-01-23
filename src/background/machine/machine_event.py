from enum import Enum, auto


class MachineEvent(Enum):
    DataUpdate      : int = auto()
    FaultDetect     : int = auto()
