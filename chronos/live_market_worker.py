"""
ChronosMatch - Background live market-data worker.

Receives public Binance BTC/USDT trades in a background thread
and exposes them through a bounded, thread-safe queue.

This component does not place orders or modify the matching engine.
"""

import asyncio
import logging
import math
import threading
from collections import deque
from collections.abc import Callable
from typing import Any

from chronos.market_data import stream_live_trades


logger = logging.getLogger(__name__)


class LiveMarketWorker:
    """Manage a background Binance market-data stream."""

    def __init__(
        self,
        max_trades: int = 500,
        reconnect_delay: float = 3.0,
    ) -> None:
        if (
            not isinstance(max_trades, int)
            or isinstance(max_trades, bool)
            or max_trades < 1
        ):
            raise ValueError("max_trades must be a positive integer")

        if (
            not isinstance(reconnect_delay, (int, float))
            or isinstance(reconnect_delay, bool)
            or not math.isfinite(reconnect_delay)
            or reconnect_delay < 0
        ):
            raise ValueError(
                "reconnect_delay must be a finite non-negative number"
            )

        self.max_trades = max_trades
        self.reconnect_delay = float(reconnect_delay)

        self._trades: deque[dict[str, Any]] = deque(
            maxlen=max_trades
        )
        self._lock = threading.Lock()
        self._stop_event = threading.Event()

        self._thread: threading.Thread | None = None
        self._status = "Stopped"
        self._last_error: str | None = None
        self._received_count = 0

    @property
    def status(self) -> str:
        """Return the current connection status."""
        with self._lock:
            return self._status

    @property
    def last_error(self) -> str | None:
        """Return the latest recorded error, if any."""
        with self._lock:
            return self._last_error

    @property
    def received_count(self) -> int:
        """Return the total number of trades received since startup."""
        with self._lock:
            return self._received_count

    @property
    def is_running(self) -> bool:
        """Return whether the worker thread is alive."""
        thread = self._thread
        return thread is not None and thread.is_alive()

    def start(self) -> None:
        """Start the background worker if it is not already running."""
        if self.is_running:
            return

        self._stop_event.clear()

        with self._lock:
            self._status = "Connecting"
            self._last_error = None

        self._thread = threading.Thread(
            target=self._thread_main,
            name="chronos-live-market-data",
            daemon=True,
        )
        self._thread.start()

    def stop(self, timeout: float = 7.0) -> None:
        """Request shutdown and wait briefly for the worker to exit."""
        if (
            not isinstance(timeout, (int, float))
            or isinstance(timeout, bool)
            or not math.isfinite(timeout)
            or timeout < 0
        ):
            raise ValueError("timeout must be a finite non-negative number")

        self._stop_event.set()

        thread = self._thread

        if thread is not None and thread.is_alive():
            thread.join(timeout=float(timeout))

        if thread is None or not thread.is_alive():
            with self._lock:
                self._status = "Stopped"

    def get_trades(self, limit: int = 100) -> list[dict[str, Any]]:
        """
        Return the most recent trades without removing them.

        The oldest retained trades are omitted when the requested
        limit is smaller than the queue size.
        """
        if (
            not isinstance(limit, int)
            or isinstance(limit, bool)
            or limit < 1
        ):
            raise ValueError("limit must be a positive integer")

        with self._lock:
            return [dict(trade) for trade in list(self._trades)[-limit:]]

    def clear_trades(self) -> None:
        """Clear retained display data without stopping the stream."""
        with self._lock:
            self._trades.clear()

    def _set_status(
        self,
        status: str,
        error: str | None = None,
    ) -> None:
        with self._lock:
            self._status = status
            self._last_error = error

    def _thread_main(self) -> None:
        """Run the asynchronous consumer inside the background thread."""
        try:
            asyncio.run(self._consume_trades())

        except Exception as exc:
            logger.exception("Live market-data worker failed")
            self._set_status("Error", str(exc))

        finally:
            if self._stop_event.is_set():
                self._set_status("Stopped")

    async def _consume_trades(self) -> None:
        """Consume validated trades until shutdown is requested."""
        stream = stream_live_trades(
            reconnect_delay=self.reconnect_delay
        )

        async def receive_trades() -> None:
            async for trade in stream:
                if self._stop_event.is_set():
                    break

                with self._lock:
                    self._trades.append(dict(trade))
                    self._received_count += 1
                    self._status = "Connected"
                    self._last_error = None

        consumer = asyncio.create_task(receive_trades())

        try:
            while not self._stop_event.is_set() and not consumer.done():
                await asyncio.sleep(0.1)

            if consumer.done() and not self._stop_event.is_set():
                try:
                    await consumer
                except StopAsyncIteration:
                    self._set_status("Disconnected")

        except asyncio.CancelledError:
            raise

        except Exception as exc:
            logger.exception("Error receiving live market data")
            self._set_status("Error", str(exc))

        finally:
            if not consumer.done():
                consumer.cancel()

            try:
                await consumer
            except asyncio.CancelledError:
                pass
            except Exception:
                logger.debug(
                    "Live market-data consumer ended during cleanup",
                    exc_info=True,
                )

            try:
                await stream.aclose()
            finally:
                if self._stop_event.is_set():
                    self._set_status("Stopped")

