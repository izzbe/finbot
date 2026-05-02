from pydantic import BaseModel, PositiveInt, PositiveFloat, Field

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

