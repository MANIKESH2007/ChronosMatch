import pytest
from chronos.order import Order


def test_create_valid_order():
    order = Order(101, "BUY", 150.50, 10)

    assert order.order_id == 101
    assert order.side == "BUY"
    assert order.price == 150.50
    assert order.quantity == 10
    assert order.order_type == "LIMIT"


def test_create_sell_order():
    order = Order(102, "SELL", 200, 5, "MARKET")

    assert order.side == "SELL"
    assert order.order_type == "MARKET"


def test_invalid_order_id():
    with pytest.raises(ValueError):
        Order(0, "BUY", 100, 10)


def test_invalid_side():
    with pytest.raises(ValueError):
        Order(103, "HOLD", 100, 10)


def test_invalid_price():
    with pytest.raises(ValueError):
        Order(104, "BUY", -100, 10)


def test_invalid_quantity():
    with pytest.raises(ValueError):
        Order(105, "SELL", 100, -5)


def test_zero_quantity():
    with pytest.raises(ValueError):
        Order(106, "BUY", 100, 0)


def test_invalid_order_type():
    with pytest.raises(ValueError):
        Order(107, "BUY", 100, 10, "UNKNOWN")


def test_string_price():
    with pytest.raises(ValueError):
        Order(108, "BUY", "100", 10)