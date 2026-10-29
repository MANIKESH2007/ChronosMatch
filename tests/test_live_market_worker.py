import threading
import time
from unittest.mock import patch

import pytest

from chronos.live_market_worker import LiveMarketWorker


@pytest.fixture
def worker():
    return LiveMarketWorker(max_trades=3, reconnect_delay=0.1)


def make_trade(price):
    return {
        "symbol": "BTCUSDT",
        "price": float(price),
        "quantity": 0.01,
        "timestamp": 1_800_000_000_000,
        "aggressor_side": "BUY",
    }


def test_worker_initial_status(worker):
    assert worker.status == "Stopped"
    assert worker.last_error is None
    assert worker.received_count == 0
    assert worker.is_running is False


def test_worker_rejects_invalid_max_trades():
    for value in (0, -1, 1.5, True, "3"):
        with pytest.raises(ValueError):
            LiveMarketWorker(max_trades=value)


def test_worker_rejects_invalid_reconnect_delay():
    for value in (-1, float("inf"), float("nan"), True, "1"):
        with pytest.raises(ValueError):
            LiveMarketWorker(reconnect_delay=value)


def test_worker_rejects_invalid_stop_timeout(worker):
    for value in (-1, float("inf"), float("nan"), True, "1"):
        with pytest.raises(ValueError):
            worker.stop(timeout=value)


def test_worker_rejects_invalid_trade_limit(worker):
    for value in (0, -1, 1.5, True, "2"):
        with pytest.raises(ValueError):
            worker.get_trades(limit=value)


def test_get_trades_returns_most_recent_trades(worker):
    with worker._lock:
        worker._trades.extend(
            [make_trade(100), make_trade(200), make_trade(300)]
        )

    trades = worker.get_trades(limit=2)

    assert [trade["price"] for trade in trades] == [200.0, 300.0]


def test_trade_storage_is_bounded(worker):
    with worker._lock:
        worker._trades.extend(
            [make_trade(100), make_trade(200), make_trade(300)]
        )
        worker._trades.append(make_trade(400))

    trades = worker.get_trades()

    assert len(trades) == 3
    assert [trade["price"] for trade in trades] == [
        200.0,
        300.0,
        400.0,
    ]


def test_get_trades_returns_copies(worker):
    with worker._lock:
        worker._trades.append(make_trade(100))

    trades = worker.get_trades()
    trades[0]["price"] = -1

    assert worker.get_trades()[0]["price"] == 100.0


def test_clear_trades_does_not_reset_received_count(worker):
    with worker._lock:
        worker._trades.append(make_trade(100))
        worker._received_count = 1

    worker.clear_trades()

    assert worker.get_trades() == []
    assert worker.received_count == 1


def test_start_is_idempotent(worker):
    started = threading.Event()
    release = threading.Event()

    def fake_thread_main():
        started.set()
        release.wait(timeout=2)

    with patch.object(worker, "_thread_main", side_effect=fake_thread_main):
        worker.start()
        assert started.wait(timeout=1)

        first_thread = worker._thread
        worker.start()

        assert worker._thread is first_thread

        release.set()
        first_thread.join(timeout=1)

    assert not worker.is_running


def test_stop_without_started_thread(worker):
    worker.stop()

    assert worker.status == "Stopped"
    assert worker.is_running is False


def test_worker_records_trades_from_async_stream(worker):
    async def fake_stream(reconnect_delay=3.0):
        yield make_trade(100)
        yield make_trade(200)

        while True:
            import asyncio
            await asyncio.sleep(0.05)

    with patch(
        "chronos.live_market_worker.stream_live_trades",
        side_effect=fake_stream,
    ):
        worker.start()

        deadline = time.monotonic() + 2

        while worker.received_count < 2 and time.monotonic() < deadline:
            time.sleep(0.01)

        worker.stop(timeout=2)

    assert worker.received_count == 2
    assert [trade["price"] for trade in worker.get_trades()] == [
        100.0,
        200.0,
    ]
    assert worker.status == "Stopped"


def test_worker_records_unexpected_errors(worker):
    def fail():
        raise RuntimeError("simulated worker failure")

    with patch.object(worker, "_consume_trades", side_effect=fail):
        worker.start()

        deadline = time.monotonic() + 2

        while worker.is_running and time.monotonic() < deadline:
            time.sleep(0.01)

    assert worker.status == "Error"
    assert worker.last_error == "simulated worker failure"


def test_start_does_not_restart_worker_after_stop_timeout(worker):
    started = threading.Event()
    release = threading.Event()

    def fake_thread_main():
        started.set()
        release.wait(timeout=5)

    with patch.object(worker, "_thread_main", side_effect=fake_thread_main):
        worker.start()
        assert started.wait(timeout=1)

        first_thread = worker._thread

        worker.stop(timeout=0)

        assert first_thread.is_alive()

        worker.start()

        assert worker._thread is first_thread

        release.set()
        first_thread.join(timeout=1)

    assert not worker.is_running
