from abc import ABC, abstractmethod
from datetime import datetime

from common.models import Bar


class BarDataFetcher(ABC):
    @abstractmethod
    def get_data(
        self,
        symbol: str,
        start: datetime,
        end: datetime | None = None,
        timespan: str = "day",
    ) -> list[Bar]:
        pass
