"""
ChronosMatch - Live Market Data Connection Test.

Connects to Binance's public BTC/USDT trade stream and prints
up to five trades. This script does not place orders.
"""

import asyncio
from datetime import datetime, timezone

from chronos.market_data import stream_live_trades

async def main():
    print("Connecting to Binance public BTC/USDT trade stream...")
    print("Waiting for up to 5 live trades. Press Ctrl+C to stop.\n")


    trade_count = 0
    stream = stream_live_trades(reconnect_delay=3.0)

    try:
        async for trade in stream:
            timestamp = datetime.fromtimestamp(
                trade["timestamp"] / 1000,
                tz=timezone.utc,
            )

            trade_count += 1

            print(
                f"Trade {trade_count}/5 | "
                f"Time: {timestamp.isoformat()} | "
                f"Symbol: {trade['symbol']} | "
                f"Price: ${trade['price']:,.2f} | "
                f"Quantity: {trade['quantity']:.6f} | "
                f"Aggressor: {trade['aggressor_side']}"
            )

            if trade_count >= 5:
                print("\nSuccessfully received 5 live trades.")
                break

    except asyncio.CancelledError:
        print("\nLive market data stream cancelled.")
        raise

    except KeyboardInterrupt:
        print("\nStopped by user.")

    finally:
        await stream.aclose()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nLive market data test stopped.")
