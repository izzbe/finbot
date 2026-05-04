import os

import psycopg2

DDL = """
CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS ohlcv (
    symbol TEXT,
    ts TIMESTAMPTZ,
    open NUMERIC,
    close NUMERIC,
    high NUMERIC,
    low NUMERIC,
    volume NUMERIC,
    num_transactions INT,
    volume_weighted_average_price NUMERIC,
    PRIMARY KEY (symbol, ts)
) WITH (
  timescaledb.hypertable,
  timescaledb.partition_column = 'ts'
);

CREATE INDEX IF NOT EXISTS ohlcv_symbol_ts_idx
    ON ohlcv (symbol, ts DESC);
"""

if __name__ == "__main__":
    conn = psycopg2.connect(
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.environ["POSTGRES_HOST"],
        port=5432,
    )

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(DDL)
    finally:
        conn.close()
