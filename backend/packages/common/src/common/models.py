from datetime import datetime, timezone

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PositiveFloat,
    PositiveInt,
    field_validator,
    model_validator,
)


class Bar(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    ticker: str = Field(alias="T")
    volume: PositiveFloat = Field(alias="v")
    volume_weighted_average_price: PositiveFloat | None = Field(alias="vw")
    open_price: PositiveFloat = Field(alias="o")
    close_price: PositiveFloat = Field(alias="c")
    high_price: PositiveFloat = Field(alias="h")
    low_price: PositiveFloat = Field(alias="l")
    timestamp: datetime = Field(alias="t")
    num_transactions: PositiveInt = Field(alias="n")

    @field_validator("timestamp", mode="before")
    @classmethod
    def convert_to_unix(cls, value: int | datetime):
        if isinstance(value, datetime):
            return value
        return datetime.fromtimestamp(value / 1000, tz=timezone.utc)


class BarDataRequest(BaseModel):
    symbol: str
    start: datetime
    end: datetime | None = None
    timespan: str = "day"
    timespan_multiplier: int = 1

    @field_validator("timespan")
    @classmethod
    def valid_timespan(cls, value: str):
        allowed = {"min", "hr", "day", "week", "month", "year"}
        if value not in allowed:
            raise ValueError(f"level must be one of {allowed}")
        return value

    @model_validator(mode="after")
    def check_start_before_end(self):
        if self.end is None:
            return self
        if self.start > self.end:
            raise ValueError("Start time must be before end time")
        return self
