from pydantic import BaseModel, PositiveInt, PositiveFloat, Field, field_validator, model_validator
from datetime import datetime

class Bar(BaseModel):
    ticker: str = Field(alias="T")
    volume: PositiveFloat = Field(alias="v")
    volume_weighted_average_price: PositiveFloat = Field(alias="vw")
    open_price: PositiveFloat = Field(alias="o")
    close_price: PositiveFloat = Field(alias="c")
    high_price: PositiveFloat = Field(alias="h")
    low_price: PositiveFloat = Field(alias="l")
    timestamp: int = Field(alias="t")
    num_transactions: PositiveInt = Field(alias="n")

class BarDataRequest(BaseModel):
    symbol: str
    start: datetime
    end: datetime | None = None
    timespan: str = "day"

    @field_validator("timespan")
    @classmethod
    def valid_timespan(cls, value: str):
        allowed = {"1min", "5min", "15min", "1hr", "day", "week", "month", "year"}
        if value not in allowed:
            raise ValueError(f"level must be one of {allowed}")
        return value


    @model_validator(mode="before")
    def check_start_before_end(self):
        if self.start > self.end:
            raise ValueError("Start time must be before end time")
        return self

