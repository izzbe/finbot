from fastapi import FastAPI, Depends, HTTPException
from common.models import BarDataRequest, Bar
from fetchers.data import MassiveFetcher
from contextlib import asynccontextmanager
import asyncpg
import os
from pydantic import TypeAdapter
from datetime import datetime, timezone

async def get_conn():
    async with app.state.pool.acquire() as conn:
        async with conn.transaction():
            yield conn

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await asyncpg.create_pool(
        (
            f"postgres://{os.environ["POSTGRES_USER"]}:"
            f"{os.environ["POSTGRES_PASSWORD"]}"
            f"@{os.environ["POSTGRES_HOST"]}:5432"
            f"/{os.environ["POSTGRES_DB"]}"
        )
    )
    app.state.fetcher = MassiveFetcher()
    yield
    await app.state.pool.close()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/data/post_historical/")
async def post_historical(request: BarDataRequest, conn = Depends(get_conn)):
    payload: list[Bar] = app.state.fetcher.get_data(request.symbol,
                                          request.start,
                                          request.end,
                                          request.timespan
                                          )
    dumps = [bar.model_dump(by_alias=True) for bar in payload]
    insert_values = [(dump["T"],
                      dump["t"],
                      dump["o"],
                      dump["c"],
                      dump["h"],
                      dump["l"],
                      dump["v"],
                      dump["n"],
                      dump["vw"])
                     for dump in dumps]
    statement = """
    INSERT INTO ohlcv (symbol, ts, open, close, high, low, volume, num_transactions, volume_weighted_average_price)
    VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9)
    ON CONFLICT (symbol, ts)
    DO NOTHING
    """

    await conn.executemany(statement, insert_values)

    return {"rows": len(insert_values)}

@app.get("/data/get_historical/{ticker}", response_model=list[Bar])
async def get_historical(ticker: str,
                         start: datetime,
                         end: datetime=datetime.now(tz=timezone.utc),
                         timespan: str = "day",
                         timespan_mult: int = 1,
                         order: str = "ASC",
                         conn = Depends(get_conn)) -> list[Bar]:

    if order not in ["ASC", "DESC"]:
        raise HTTPException(422, "order must be one of ASC, DESC")

    if timespan not in {"min", "hr", "day", "week", "month", "year"}:
        raise HTTPException(422, "timespan must be one of min, hr, day, week, month, year")

    time_bucket_select = f"{str(timespan_mult)} {timespan}"
    cols = ["open", "close", "high", "low", "volume", "num_transactions"]
    aggregation = ["first", "last", "max", "min", "sum", "sum"]
    aliases = ["open_price", "close_price", "high_price", "low_price", "volume", "num_transactions"]
    column_select = ""
    for col, alias, agg in zip(cols, aliases, aggregation):
        if col in ["open", "close"]:
            column_select += f"{agg}({col}, ts) as {alias}"
        else:
            column_select += f"{agg}({col}) as {alias}"
        column_select += ",\n"

    column_select += "SUM(volume_weighted_average_price * volume) / NULLIF(SUM(volume), 0) AS volume_weighted_average_price"

    query = f"""
    SELECT time_bucket('{time_bucket_select}', ts) as timestamp,
    symbol as ticker,
    {column_select}
    from ohlcv
    WHERE ts between $1 AND $2
    AND symbol = $3
    GROUP BY timestamp, symbol
    ORDER BY timestamp {order};
    """

    raw = await conn.fetch(query, start, end, ticker)
    result = [dict(row) for row in raw]
    list_of_bar = TypeAdapter(list[Bar])
    result_parsed = list_of_bar.validate_python(result)
    return result_parsed

