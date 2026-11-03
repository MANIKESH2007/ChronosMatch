import pandas as pd
import pytest

from chronos.historical_data import (
    HISTORICAL_TRADE_COLUMNS,
    aggregate_historical_trades,
    iter_historical_trades,
    summarize_historical_trades,
)


@pytest.fixture
def sample_csv(tmp_path):
    """Create a small historical trades CSV for testing."""

    data = [
        [1, 100.0, 2.0, 10, 10, 1788220800322740, False, True],
        [2, 110.0, 3.0, 11, 11, 1788220800491646, True, True],
        [3, 120.0, 1.0, 12, 12, 1788220800533037, False, True],
    ]

    file_path = tmp_path / "sample_trades.csv"

    pd.DataFrame(data).to_csv(
        file_path,
        header=False,
        index=False,
    )

    return file_path


def test_load_historical_trades(sample_csv):
    chunks = list(iter_historical_trades(sample_csv, chunksize=2))

    assert len(chunks) == 2
    assert len(chunks[0]) == 2
    assert len(chunks[1]) == 1


def test_historical_trade_columns(sample_csv):
    chunk = next(iter_historical_trades(sample_csv))

    assert list(chunk.columns) == HISTORICAL_TRADE_COLUMNS + [
        "aggressor_side"
    ]


def test_timestamp_converted_to_utc(sample_csv):
    chunk = next(iter_historical_trades(sample_csv))

    assert isinstance(chunk["timestamp"].iloc[0], pd.Timestamp)
    assert str(chunk["timestamp"].dt.tz) == "UTC"


def test_aggressor_side_identification(sample_csv):
    chunk = next(iter_historical_trades(sample_csv))

    assert chunk["aggressor_side"].tolist() == [
        "BUY",
        "SELL",
        "BUY",
    ]


def test_historical_summary(sample_csv):
    summary = summarize_historical_trades(sample_csv, chunksize=2)

    assert summary["Total Trades"] == 3
    assert summary["Minimum Price"] == 100.0
    assert summary["Maximum Price"] == 120.0
    assert summary["Total Quantity"] == 6.0
    assert summary["Total Quote Volume"] == 650.0
    assert summary["VWAP"] == pytest.approx(650 / 6)
    assert summary["Buy Quantity"] == 3.0
    assert summary["Sell Quantity"] == 3.0


def test_missing_file_raises_error(tmp_path):
    missing_file = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError):
        list(iter_historical_trades(missing_file))


@pytest.mark.parametrize("chunksize", [0, -1, 1.5, True])
def test_invalid_chunksize_raises_error(sample_csv, chunksize):
    with pytest.raises(ValueError, match="chunksize"):
        list(iter_historical_trades(sample_csv, chunksize))


def test_empty_dataset_raises_error(tmp_path):
    empty_file = tmp_path / "empty.csv"
    empty_file.write_text("")

    with pytest.raises(ValueError, match="no trades"):
        summarize_historical_trades(empty_file)


@pytest.mark.parametrize(
    "price, quantity",
    [
        (0, 1),
        (-10, 1),
        (100, 0),
        (100, -2),
    ],
)
def test_invalid_price_or_quantity_raises_error(
    tmp_path, price, quantity
):
    file_path = tmp_path / "invalid.csv"

    row = [
        1, price, quantity, 10, 10,
        1788220800322740, False, True,
    ]

    pd.DataFrame([row]).to_csv(
        file_path,
        header=False,
        index=False,
    )

    with pytest.raises(ValueError):
        list(iter_historical_trades(file_path))


def test_historical_ohlcv_aggregation_across_chunks(sample_csv):
    candles = aggregate_historical_trades(
        sample_csv,
        chunksize=1,
        frequency="1h",
    )

    assert len(candles) == 1

    candle = candles.iloc[0]

    assert candle["open"] == 100.0
    assert candle["high"] == 120.0
    assert candle["low"] == 100.0
    assert candle["close"] == 120.0
    assert candle["quantity"] == 6.0
    assert candle["quote_volume"] == 650.0
    assert candle["trade_count"] == 3

    assert candle["timestamp"] == pd.Timestamp(
        "2026-09-01 00:00:00",
        tz="UTC",
    )


def test_historical_aggregation_empty_dataset_raises_error(tmp_path):
    empty_file = tmp_path / "empty.csv"
    empty_file.write_text("")

    with pytest.raises(ValueError, match="no trades"):
        aggregate_historical_trades(empty_file)
