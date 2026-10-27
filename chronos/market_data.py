"""
ChronosMatch - Public cryptocurrency market data.

Parses public Binance trade messages and provides an asynchronous
client for receiving live BTC/USDT trades.

This module does not place orders or execute trades.
"""

import asyncio
import json
import math
from collections.abc import AsyncIterator
from typing import Any

import websockets
from websockets.exceptions import WebSocketException


BINANCE_TRADE_STREAM_URL = "wss://stream.binance.com:9443/ws/btcusdt@trade"


def parse_trade_message(message: str | bytes) -> dict[str, Any]:
    """
    Parse a Binance BTC/USDT trade-stream message.

    Returns:
        A dictionary containing symbol, price, quantity,
        timestamp, and aggressor side.

    Raises:
        ValueError: If the message is malformed or contains invalid data.
    """
    try:
        if isinstance(message, bytes):
            message = message.decode("utf-8")

        if not isinstance(message, str):
            raise ValueError("Message must be a string or bytes")

        payload = json.loads(message)

    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Invalid JSON trade message") from exc

    if not isinstance(payload, dict):
        raise ValueError("Trade message must be a JSON object")

    required_fields = {"e", "s", "p", "q", "T", "m"}

    if not required_fields.issubset(payload):
        raise ValueError("Trade message is missing required fields")

    if payload["e"] != "trade":
        raise ValueError("Message is not a trade event")

    symbol = payload["s"]

    if symbol != "BTCUSDT":
        raise ValueError("Only BTCUSDT trade messages are supported")

    try:
        price = float(payload["p"])
        quantity = float(payload["q"])
        timestamp = payload["T"]
    except (TypeError, ValueError) as exc:
        raise ValueError("Invalid price or quantity") from exc

    if not math.isfinite(price) or price <= 0:
        raise ValueError("Price must be a finite positive number")

    if not math.isfinite(quantity) or quantity <= 0:
        raise ValueError("Quantity must be a finite positive number")

    if (
        not isinstance(timestamp, int)
        or isinstance(timestamp, bool)
        or timestamp < 0
    ):
        raise ValueError("Timestamp must be a non-negative integer")

    if not isinstance(payload["m"], bool):
        raise ValueError("Buyer-maker flag must be a boolean")

    # m=True means the buyer was the maker, so the seller
    # was the aggressor.
    aggressor_side = "SELL" if payload["m"] else "BUY"

    return {
        "symbol": symbol,
        "price": price,
        "quantity": quantity,
        "timestamp": timestamp,
        "aggressor_side": aggressor_side,
    }


async def stream_live_trades(
    reconnect_delay: float = 3.0,
) -> AsyncIterator[dict[str, Any]]:
    """
    Yield validated BTC/USDT trades from Binance's public WebSocket.

    Reconnect after network or WebSocket errors. Invalid individual
    messages are skipped without terminating the stream.

    Stop the consumer by cancelling its task or closing the
    asynchronous generator.
    """
    if (
        not isinstance(reconnect_delay, (int, float))
        or isinstance(reconnect_delay, bool)
        or not math.isfinite(reconnect_delay)
        or reconnect_delay < 0
    ):
        raise ValueError("Reconnect delay must be a finite non-negative number")

    while True:
        try:
            async with websockets.connect(
                BINANCE_TRADE_STREAM_URL,
                open_timeout=10,
                close_timeout=5,
                ping_interval=20,
                ping_timeout=20,
            ) as websocket:
                async for message in websocket:
                    try:
                        trade = parse_trade_message(message)
                    except ValueError:
                        # Ignore malformed or unexpected messages.
                        continue

                    yield trade

        except asyncio.CancelledError:
            # Preserve cancellation so callers can stop cleanly.
            raise

        except (OSError, WebSocketException, asyncio.TimeoutError):
            # Retry after a network interruption or connection failure.
            await asyncio.sleep(reconnect_delay)
