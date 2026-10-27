import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from chronos.market_data import parse_trade_message, stream_live_trades


@pytest.fixture
def valid_trade():
    """Return a valid Binance BTC/USDT trade message."""
    return {
        "e": "trade",
        "s": "BTCUSDT",
        "p": "67000.50",
        "q": "0.002",
        "T": 1720000000000,
        "m": False,
    }


def test_parse_valid_trade(valid_trade):
    result = parse_trade_message(json.dumps(valid_trade))

    assert result == {
        "symbol": "BTCUSDT",
        "price": 67000.50,
        "quantity": 0.002,
        "timestamp": 1720000000000,
        "aggressor_side": "BUY",
    }


def test_parse_bytes_message(valid_trade):
    message = json.dumps(valid_trade).encode("utf-8")

    result = parse_trade_message(message)

    assert result["symbol"] == "BTCUSDT"
    assert result["price"] == 67000.50


def test_buyer_was_maker_means_sell_aggressor(valid_trade):
    valid_trade["m"] = True

    result = parse_trade_message(json.dumps(valid_trade))

    assert result["aggressor_side"] == "SELL"


def test_buyer_was_not_maker_means_buy_aggressor(valid_trade):
    valid_trade["m"] = False

    result = parse_trade_message(json.dumps(valid_trade))

    assert result["aggressor_side"] == "BUY"


@pytest.mark.parametrize(
    "message",
    [
        "{invalid json}",
        "[]",
        "null",
    ],
)
def test_reject_invalid_json_or_non_object(message):
    with pytest.raises(ValueError):
        parse_trade_message(message)


def test_reject_missing_required_field(valid_trade):
    del valid_trade["p"]

    with pytest.raises(ValueError, match="missing required fields"):
        parse_trade_message(json.dumps(valid_trade))


def test_reject_non_trade_event(valid_trade):
    valid_trade["e"] = "aggTrade"

    with pytest.raises(ValueError, match="not a trade event"):
        parse_trade_message(json.dumps(valid_trade))


def test_reject_unsupported_symbol(valid_trade):
    valid_trade["s"] = "ETHUSDT"

    with pytest.raises(ValueError, match="Only BTCUSDT"):
        parse_trade_message(json.dumps(valid_trade))


@pytest.mark.parametrize("price", ["0", "-1", "nan", "inf", "-inf"])
def test_reject_invalid_price(valid_trade, price):
    valid_trade["p"] = price

    with pytest.raises(ValueError):
        parse_trade_message(json.dumps(valid_trade))


@pytest.mark.parametrize("quantity", ["0", "-1", "nan", "inf", "-inf"])
def test_reject_invalid_quantity(valid_trade, quantity):
    valid_trade["q"] = quantity

    with pytest.raises(ValueError):
        parse_trade_message(json.dumps(valid_trade))


@pytest.mark.parametrize("timestamp", [-1, 1.5, True, "1720000000000"])
def test_reject_invalid_timestamp(valid_trade, timestamp):
    valid_trade["T"] = timestamp

    with pytest.raises(ValueError, match="Timestamp"):
        parse_trade_message(json.dumps(valid_trade))


@pytest.mark.parametrize("maker_flag", ["false", 0, None])
def test_reject_invalid_buyer_maker_flag(valid_trade, maker_flag):
    valid_trade["m"] = maker_flag

    with pytest.raises(ValueError, match="boolean"):
        parse_trade_message(json.dumps(valid_trade))


def test_reject_non_string_message():
    with pytest.raises(ValueError, match="string or bytes"):
        parse_trade_message(123)


def test_reject_invalid_utf8_bytes():
    with pytest.raises(ValueError, match="Invalid JSON"):
        parse_trade_message(b"\xff")

@pytest.mark.parametrize("delay", [-1, float("inf"), float("nan"), True, "3"])
def test_stream_rejects_invalid_reconnect_delay(delay):
    async def run_test():
        with pytest.raises(ValueError, match="Reconnect delay"):
            stream = stream_live_trades(reconnect_delay=delay)
            await anext(stream)


    asyncio.run(run_test())


def test_stream_delivers_valid_trade_and_skips_invalid_message(valid_trade):
    async def run_test():
        valid_message = json.dumps(valid_trade)


        websocket = MagicMock()
        websocket.__aiter__.return_value = iter(
            [
                "{invalid json}",
                valid_message,
            ]
        )

        connection = AsyncMock()
        connection.__aenter__.return_value = websocket
        connection.__aexit__.return_value = False

        with patch(
            "chronos.market_data.websockets.connect",
            return_value=connection,
        ):
            stream = stream_live_trades()

            try:
                result = await anext(stream)

                assert result["symbol"] == "BTCUSDT"
                assert result["price"] == 67000.50
                assert result["aggressor_side"] == "BUY"

            finally:
                await stream.aclose()

    asyncio.run(run_test())


def test_stream_reconnects_after_connection_failure(valid_trade):
    async def run_test():
        valid_message = json.dumps(valid_trade)


        websocket = MagicMock()
        websocket.__aiter__.return_value = iter([valid_message])

        successful_connection = AsyncMock()
        successful_connection.__aenter__.return_value = websocket
        successful_connection.__aexit__.return_value = False

        with (
            patch(
                "chronos.market_data.websockets.connect",
                side_effect=[
                    OSError("Simulated connection failure"),
                    successful_connection,
                ],
            ) as mock_connect,
            patch(
                "chronos.market_data.asyncio.sleep",
                new_callable=AsyncMock,
            ) as mock_sleep,
        ):
            stream = stream_live_trades(reconnect_delay=0.1)

            try:
                result = await anext(stream)

                assert result["symbol"] == "BTCUSDT"
                assert result["price"] == 67000.50

                assert mock_connect.call_count == 2
                mock_sleep.assert_awaited_once_with(0.1)

            finally:
                await stream.aclose()

    asyncio.run(run_test())

