from abc import ABC, abstractmethod
from common.models import Bar, BarDataRequest

class BarDataFetcher(ABC):
    @abstractmethod
    def get_data(self, request: BarDataRequest) -> list[Bar]:
        pass

    @abstractmethod
    def push_data(self, data: list[Bar]):
        pass
