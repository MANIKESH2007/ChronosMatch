import pandas as pd


def get_order_book_data(engine):
    """Convert active buy and sell orders into a DataFrame."""

    orders = engine.order_book.get_all_orders()

    order_data = [
        {
            "Order ID": order.order_id,
            "Side": order.side,
            "Price": order.price,
            "Remaining Quantity": order.quantity,
            "Order Type": order.order_type,
        }
        for order in orders
    ]

    columns = [
        "Order ID",
        "Side",
        "Price",
        "Remaining Quantity",
        "Order Type",
    ]

    return pd.DataFrame(order_data, columns=columns)


def get_trade_history_data(engine):
    """Convert executed trades into a DataFrame."""

    trade_data = [
        {
            "Buy Order ID": trade["buy_order_id"],
            "Sell Order ID": trade["sell_order_id"],
            "Price": trade["price"],
            "Quantity": trade["quantity"],
        }
        for trade in engine.trades
    ]

    columns = [
        "Buy Order ID",
        "Sell Order ID",
        "Price",
        "Quantity",
    ]

    return pd.DataFrame(trade_data, columns=columns)


def get_dashboard_summary(engine):
    """Return basic summary statistics for the dashboard."""

    active_orders = engine.order_book.get_all_orders()

    return {
        "Active Orders": len(active_orders),
        "Active Buy Orders": len(engine.order_book.buy_orders),
        "Active Sell Orders": len(engine.order_book.sell_orders),
        "Executed Trades": len(engine.trades),
    }
