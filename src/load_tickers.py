import asyncio
import asyncpg
import aiofiles
import os
import pandas as pd
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")
DB_CONFIG = {
    "user": os.getenv('POSTGRES_USER', 'postgres'),
    "password": os.getenv('POSTGRES_PASSWORD', ''),
    "database": os.getenv('POSTGRES_DB', ''),
    "host": os.getenv('POSTGRES_HOST', 'localhost'),
    "port": os.getenv('POSTGRES_PORT', '5432'),
}

BASE_FOLDER = "./sp500_data"  # 📂 Root folder for subfolders with OHLCV data
TIMEFRAMES = {
    "2y": "ohlcv_1d",
    "1h": "ohlcv_1h",
    "5m": "ohlcv_5m",
}


# Mandatory fields in CSV files: Date,Open,High,Low,Close,Volume
CSV_COLUMNS = ['Ticker', 'Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']


async def insert_dataframe(pool, table, df):
    async with pool.acquire() as conn:
        async with conn.transaction():
            values = [
                (
                    str(row['Ticker']),
                    pd.to_datetime(row['Datetime']),
                    float(row['Open']),
                    float(row['High']),
                    float(row['Low']),
                    float(row['Close']),
                    int(row['Volume']),
                )
                for _, row in df.iterrows()
            ]
            await conn.executemany(
                f"""
                INSERT INTO {table} (ticker, timestamp, open, high, low, close, volume)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (ticker, timestamp) DO NOTHING;
                """,
                values
            )


async def load_csvs_from_folder(pool, timeframe, table_name):
    folder = Path(BASE_FOLDER) / timeframe
    start_time = time.perf_counter()

    tasks = []

    for file in folder.glob("*.csv"):
        symbol = file.stem.upper()
        df = pd.read_csv(file)

        if not all(col in df.columns for col in CSV_COLUMNS):
            print(f"Skip.. (missed required fields): {file.name}")
            continue

        task = insert_dataframe(pool, table_name, df)
        tasks.append(task)

    await asyncio.gather(*tasks)

    elapsed = time.perf_counter() - start_time
    print(" ============================================== ")
    print(f" Loading {timeframe}: {elapsed:.2f} seconds")
    print(" ============================================== ")


async def main():
    pool = await asyncpg.create_pool(**DB_CONFIG)

    for timeframe, table in TIMEFRAMES.items():
        await load_csvs_from_folder(pool, timeframe, table)

    await pool.close()


if __name__ == "__main__":
    asyncio.run(main())
