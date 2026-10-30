from chronos.order import Order
from chronos.matching_engine import MatchingEngine
from chronos.dashboard_data import (
    get_order_book_data,
    get_trade_history_data,
    get_dashboard_summary,
)


def test_complete_order_matching_and_dashboard_workflow():
    engine = MatchingEngine()

    buy_order = Order(1, "BUY", 105, 10)
    sell_order_1 = Order(2, "SELL", 100, 4)
    sell_order_2 = Order(3, "SELL", 102, 3)

    engine.add_order(buy_order)
    engine.add_order(sell_order_1)
    engine.add_order(sell_order_2)

    # Verify matching results
    assert len(engine.trades) == 2
    assert engine.trades[0]["quantity"] == 4
    assert engine.trades[1]["quantity"] == 3

    # Verify remaining order
    assert buy_order.quantity == 3
    assert len(engine.order_book.buy_orders) == 1
    assert len(engine.order_book.sell_orders) == 0

    # Verify dashboard order book
    order_data = get_order_book_data(engine)
    assert len(order_data) == 1
    assert order_data.iloc[0]["Order ID"] == 1
    assert order_data.iloc[0]["Remaining Quantity"] == 3

    # Verify dashboard trade history
    trade_data = get_trade_history_data(engine)
    assert len(trade_data) == 2
    assert list(trade_data["Quantity"]) == [4, 3]
    assert list(trade_data["Price"]) == [100.0, 102.0]

    # Verify dashboard summary
    summary = get_dashboard_summary(engine)
    assert summary == {
        "Active Orders": 1,
        "Active Buy Orders": 1,
        "Active Sell Orders": 0,
        "Executed Trades": 2,
    }
