from fetchers.base import BarDataFetcher
import os
import httpx
from datetime import datetime
from common.models import Bar
from pydantic import TypeAdapter

class MassiveFetcher(BarDataFetcher):
    def __init__(self):
        self.auth = {"Authorization": f"Bearer {os.environ["MASSIVE_API_KEY"]}"}

    def get_data(
            self,
            symbol: str,
            start: datetime,
            end: datetime | None = None,
            timespan: str = "day",
            ) -> list[Bar]:
        url = (
            f"https://api.massive.com/v2/aggs/ticker/"
            f"{symbol}"
            f"/range/1/{timespan}"
            f"/{start.strftime("%Y-%m-%d")}"
            f"/{end.strftime("%Y-%m-%d")}"
        )

        response = httpx.get(url, headers=self.auth)
        response.raise_for_status()
        data = response.json()['results']
        for d in data:
            d["T"] = response.json()["ticker"]
        list_of_bar = TypeAdapter(list[Bar])
        result = list_of_bar.validate_python(data)
        return result

