import pandas as pd

from chronos.order import Order
from chronos.matching_engine import MatchingEngine
from chronos.dashboard_data import (
    get_order_book_data,
    get_trade_history_data,
    get_dashboard_summary,
)


def test_order_book_data_with_active_orders():
    engine = MatchingEngine()

    engine.add_order(Order(1, "BUY", 150, 10))
    engine.add_order(Order(2, "SELL", 160, 5))

    data = get_order_book_data(engine)

    assert isinstance(data, pd.DataFrame)
    assert len(data) == 2
    assert list(data.columns) == [
        "Order ID",
        "Side",
        "Price",
        "Remaining Quantity",
        "Order Type",
    ]
    assert set(data["Side"]) == {"BUY", "SELL"}


def test_order_book_data_when_empty():
    engine = MatchingEngine()

    data = get_order_book_data(engine)

    assert isinstance(data, pd.DataFrame)
    assert data.empty
    assert "Order ID" in data.columns


def test_trade_history_data_after_matching():
    engine = MatchingEngine()

    engine.add_order(Order(1, "BUY", 150, 10))
    engine.add_order(Order(2, "SELL", 140, 5))

    data = get_trade_history_data(engine)

    assert isinstance(data, pd.DataFrame)
    assert len(data) == 1
    assert data.iloc[0]["Buy Order ID"] == 1
    assert data.iloc[0]["Sell Order ID"] == 2
    assert data.iloc[0]["Price"] == 140.0
    assert data.iloc[0]["Quantity"] == 5


def test_trade_history_data_when_empty():
    engine = MatchingEngine()

    data = get_trade_history_data(engine)

    assert isinstance(data, pd.DataFrame)
    assert data.empty
    assert "Quantity" in data.columns


def test_dashboard_summary():
    engine = MatchingEngine()

    engine.add_order(Order(1, "BUY", 150, 10))
    engine.add_order(Order(2, "SELL", 160, 5))

    summary = get_dashboard_summary(engine)

    assert summary == {
        "Active Orders": 2,
        "Active Buy Orders": 1,
        "Active Sell Orders": 1,
        "Executed Trades": 0,
    }


def test_dashboard_summary_after_trade():
    engine = MatchingEngine()

    engine.add_order(Order(1, "BUY", 150, 10))
    engine.add_order(Order(2, "SELL", 140, 5))

    summary = get_dashboard_summary(engine)

    assert summary == {
        "Active Orders": 1,
        "Active Buy Orders": 1,
        "Active Sell Orders": 0,
        "Executed Trades": 1,
    }
