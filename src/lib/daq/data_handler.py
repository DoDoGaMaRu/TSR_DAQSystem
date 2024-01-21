from abc import ABC, abstractmethod
from typing import List, Dict


class DataHandler(ABC):
    @abstractmethod
    async def data_update(self, device_name: str, named_datas: Dict[str, List[float]]) -> None:
        pass
