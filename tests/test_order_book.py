import pytest
from chronos.order import Order
from chronos.order_book import OrderBook


def create_order(order_id, side, price, quantity=10, order_type="LIMIT"):
    return Order(
        order_id=order_id,
        side=side,
        price=price,
        quantity=quantity,
        order_type=order_type,
    )


def test_add_buy_order():
    book = OrderBook()
    order = create_order(1, "BUY", 100)

    book.add_order(order)

    assert len(book.get_all_orders()) == 1
    assert book.get_all_orders()[0] == order


def test_add_sell_order():
    book = OrderBook()
    order = create_order(2, "SELL", 105)

    book.add_order(order)

    assert len(book.get_all_orders()) == 1
    assert book.get_all_orders()[0] == order


def test_buy_orders_sorted_highest_price_first():
    book = OrderBook()

    book.add_order(create_order(1, "BUY", 100))
    book.add_order(create_order(2, "BUY", 110))
    book.add_order(create_order(3, "BUY", 105))

    buy_orders = book.buy_orders

    assert [order.price for order in buy_orders] == [110, 105, 100]


def test_sell_orders_sorted_lowest_price_first():
    book = OrderBook()

    book.add_order(create_order(1, "SELL", 110))
    book.add_order(create_order(2, "SELL", 100))
    book.add_order(create_order(3, "SELL", 105))

    sell_orders = book.sell_orders

    assert [order.price for order in sell_orders] == [100, 105, 110]


def test_equal_buy_prices_preserve_arrival_order():
    book = OrderBook()

    first = create_order(1, "BUY", 100)
    second = create_order(2, "BUY", 100)

    book.add_order(first)
    book.add_order(second)

    assert book.buy_orders == [first, second]


def test_equal_sell_prices_preserve_arrival_order():
    book = OrderBook()

    first = create_order(1, "SELL", 100)
    second = create_order(2, "SELL", 100)

    book.add_order(first)
    book.add_order(second)

    assert book.sell_orders == [first, second]


def test_get_best_buy():
    book = OrderBook()

    book.add_order(create_order(1, "BUY", 100))
    book.add_order(create_order(2, "BUY", 110))
    book.add_order(create_order(3, "BUY", 105))

    best_buy = book.get_best_buy()

    assert best_buy.price == 110
    assert best_buy.order_id == 2


def test_get_best_sell():
    book = OrderBook()

    book.add_order(create_order(1, "SELL", 110))
    book.add_order(create_order(2, "SELL", 100))
    book.add_order(create_order(3, "SELL", 105))

    best_sell = book.get_best_sell()

    assert best_sell.price == 100
    assert best_sell.order_id == 2


def test_cancel_order():
    book = OrderBook()
    order = create_order(1, "BUY", 100)

    book.add_order(order)

    result = book.cancel_order(1)

    assert result is True
    assert book.get_all_orders() == []


def test_cancel_nonexistent_order():
    book = OrderBook()

    result = book.cancel_order(999)

    assert result is False


def test_best_orders_when_book_is_empty():
    book = OrderBook()

    assert book.get_best_buy() is None
    assert book.get_best_sell() is None


def test_get_all_orders():
    book = OrderBook()

    buy = create_order(1, "BUY", 100)
    sell = create_order(2, "SELL", 105)

    book.add_order(buy)
    book.add_order(sell)

    all_orders = book.get_all_orders()

    assert len(all_orders) == 2
    assert buy in all_orders
    assert sell in all_orders


def test_duplicate_order_id_rejected_on_same_side():
    order_book = OrderBook()

    order_book.add_order(create_order(1, "BUY", 150))

    with pytest.raises(ValueError, match="already exists"):
        order_book.add_order(create_order(1, "BUY", 160))


def test_duplicate_order_id_rejected_on_opposite_side():
    order_book = OrderBook()

    order_book.add_order(create_order(1, "BUY", 150))

    with pytest.raises(ValueError, match="already exists"):
        order_book.add_order(create_order(1, "SELL", 140))


def test_add_invalid_object_raises_type_error():
    book = OrderBook()
    with pytest.raises(TypeError, match="Expected an Order object"):
        book.add_order("not an order")

    assert book.get_all_orders() == []

