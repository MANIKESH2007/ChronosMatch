"""
Historical Binance BTCUSDT aggregate-trade data loader.

Processes large CSV files in chunks to avoid loading the entire
historical dataset into memory.
"""

from pathlib import Path
from typing import Iterator

import pandas as pd


HISTORICAL_DATA_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "BTCUSDT-aggTrades-2026-09.csv"
)

HISTORICAL_TRADE_COLUMNS = [
    "agg_trade_id",
    "price",
    "quantity",
    "first_trade_id",
    "last_trade_id",
    "timestamp",
    "is_buyer_maker",
    "is_best_match",
]

HISTORICAL_TRADE_DTYPES = {
    "agg_trade_id": "int64",
    "price": "float64",
    "quantity": "float64",
    "first_trade_id": "int64",
    "last_trade_id": "int64",
    "timestamp": "int64",
    "is_buyer_maker": "bool",
    "is_best_match": "bool",
}


def iter_historical_trades(
    path: str | Path = HISTORICAL_DATA_PATH,
    chunksize: int = 100_000,
) -> Iterator[pd.DataFrame]:
    """
    Read historical trades in chunks.

    Binance timestamps are converted from microseconds to UTC datetime.
    """

    path = Path(path)

    if not path.is_file():
        raise FileNotFoundError(f"Historical dataset not found: {path}")

    if isinstance(chunksize, bool) or not isinstance(chunksize, int):
        raise ValueError("chunksize must be a positive integer")

    if chunksize <= 0:
        raise ValueError("chunksize must be a positive integer")

    reader = pd.read_csv(
        path,
        header=None,
        names=HISTORICAL_TRADE_COLUMNS,
        dtype=HISTORICAL_TRADE_DTYPES,
        chunksize=chunksize,
    )

    for chunk in reader:
        if chunk.empty:
            continue

        if (chunk["price"] <= 0).any():
            raise ValueError("Historical dataset contains invalid prices")

        if (chunk["quantity"] <= 0).any():
            raise ValueError("Historical dataset contains invalid quantities")

        if (chunk["timestamp"] < 0).any():
            raise ValueError("Historical dataset contains invalid timestamps")

        chunk["timestamp"] = pd.to_datetime(
            chunk["timestamp"],
            unit="us",
            utc=True,
        )

        chunk["aggressor_side"] = chunk["is_buyer_maker"].map(
            {True: "SELL", False: "BUY"}
        )

        yield chunk


def summarize_historical_trades(
    path: str | Path = HISTORICAL_DATA_PATH,
    chunksize: int = 100_000,
) -> dict:
    """
    Calculate historical trading statistics using chunk processing.

    Returns aggregate statistics without storing the entire dataset.
    """

    total_trades = 0
    total_quantity = 0.0
    total_quote_volume = 0.0

    buy_quantity = 0.0
    sell_quantity = 0.0

    min_price = float("inf")
    max_price = float("-inf")

    first_timestamp = None
    last_timestamp = None

    for chunk in iter_historical_trades(path, chunksize):
        total_trades += len(chunk)

        total_quantity += chunk["quantity"].sum()

        total_quote_volume += (
            chunk["price"] * chunk["quantity"]
        ).sum()

        min_price = min(min_price, chunk["price"].min())
        max_price = max(max_price, chunk["price"].max())

        buy_quantity += chunk.loc[
            chunk["aggressor_side"] == "BUY", "quantity"
        ].sum()

        sell_quantity += chunk.loc[
            chunk["aggressor_side"] == "SELL", "quantity"
        ].sum()

        if first_timestamp is None:
            first_timestamp = chunk["timestamp"].iloc[0]

        last_timestamp = chunk["timestamp"].iloc[-1]

    if total_trades == 0:
        raise ValueError("Historical dataset contains no trades")

    return {
        "Total Trades": int(total_trades),
        "Minimum Price": float(min_price),
        "Maximum Price": float(max_price),
        "Total Quantity": float(total_quantity),
        "Total Quote Volume": float(total_quote_volume),
        "VWAP": float(total_quote_volume / total_quantity),
        "Buy Quantity": float(buy_quantity),
        "Sell Quantity": float(sell_quantity),
        "First Timestamp": first_timestamp,
        "Last Timestamp": last_timestamp,
    }