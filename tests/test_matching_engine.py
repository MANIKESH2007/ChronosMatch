from chronos.order import Order
from chronos.matching_engine import MatchingEngine


def test_matching_orders():
    engine = MatchingEngine()

    buy_order = Order(1, "BUY", 105, 10)
    sell_order = Order(2, "SELL", 103, 6)

    engine.add_order(buy_order)
    engine.add_order(sell_order)

    assert len(engine.trades) == 1

    trade = engine.trades[0]

    assert trade["buy_order_id"] == 1
    assert trade["sell_order_id"] == 2
    assert trade["price"] == 103
    assert trade["quantity"] == 6

    assert buy_order.quantity == 4
    assert len(engine.order_book.buy_orders) == 1
    assert len(engine.order_book.sell_orders) == 0


def test_orders_do_not_match():
    engine = MatchingEngine()

    buy_order = Order(1, "BUY", 100, 5)
    sell_order = Order(2, "SELL", 105, 5)

    engine.add_order(buy_order)
    engine.add_order(sell_order)

    assert len(engine.trades) == 0
    assert len(engine.order_book.buy_orders) == 1
    assert len(engine.order_book.sell_orders) == 1

def test_exact_quantity_match():
    engine = MatchingEngine()

    buy_order = Order(1, "BUY", 105, 5)
    sell_order = Order(2, "SELL", 100, 5)

    engine.add_order(buy_order)
    engine.add_order(sell_order)

    assert len(engine.trades) == 1
    assert engine.trades[0]["quantity"] == 5

    assert len(engine.order_book.buy_orders) == 0
    assert len(engine.order_book.sell_orders) == 0


def test_buy_order_fully_filled():
    engine = MatchingEngine()

    buy_order = Order(1, "BUY", 105, 4)
    sell_order = Order(2, "SELL", 100, 10)

    engine.add_order(buy_order)
    engine.add_order(sell_order)

    assert len(engine.trades) == 1
    assert buy_order.quantity == 0
    assert sell_order.quantity == 6

    assert len(engine.order_book.buy_orders) == 0
    assert len(engine.order_book.sell_orders) == 1


def test_multiple_trades():
    engine = MatchingEngine()

    buy_order = Order(1, "BUY", 105, 5)
    sell_order1 = Order(2, "SELL", 100, 2)
    sell_order2 = Order(3, "SELL", 102, 3)

    engine.add_order(buy_order)
    engine.add_order(sell_order1)
    engine.add_order(sell_order2)

    assert len(engine.trades) == 2
    assert engine.trades[0]["quantity"] == 2
    assert engine.trades[1]["quantity"] == 3

    assert len(engine.order_book.buy_orders) == 0
    assert len(engine.order_book.sell_orders) == 0


def test_equal_prices_match(): 
    engine = MatchingEngine() 
    buy_order = Order(1, "BUY", 100, 5)
    sell_order = Order(2, "SELL", 100, 5)
    engine.add_order(buy_order) 
    engine.add_order(sell_order) 
    assert len(engine.trades) == 1 
    assert engine.trades[0]["price"] == 100 
    assert engine.trades[0]["quantity"] == 5 
    assert len(engine.order_book.buy_orders) == 0 
    assert len(engine.order_book.sell_orders) == 0



def test_sell_order_fully_filled(): 
    engine = MatchingEngine() 
    buy_order = Order(1, "BUY", 105, 10) 
    sell_order = Order(2, "SELL", 100, 4) 
    engine.add_order(buy_order) 
    engine.add_order(sell_order) 
    assert len(engine.trades) == 1 
    assert engine.trades[0]["quantity"] == 4 
    assert buy_order.quantity == 6 
    assert sell_order.quantity == 0 
    assert len(engine.order_book.buy_orders) == 1 
    assert len(engine.order_book.sell_orders) == 0



def test_sell_price_priority(): 
    engine = MatchingEngine() 
    sell_order1 = Order(1, "SELL", 105, 3) 
    sell_order2 = Order(2, "SELL", 100, 4) 
    buy_order = Order(3, "BUY", 110, 5) 
    engine.add_order(sell_order1) 
    engine.add_order(sell_order2) 
    engine.add_order(buy_order) 
    assert len(engine.trades) == 2 
    assert engine.trades[0]["sell_order_id"] == 2 
    assert engine.trades[0]["price"] == 100 
    assert engine.trades[0]["quantity"] == 4 
    assert engine.trades[1]["sell_order_id"] == 1 
    assert engine.trades[1]["price"] == 105 
    assert engine.trades[1]["quantity"] == 1 
    assert len(engine.order_book.buy_orders) == 0 
    assert len(engine.order_book.sell_orders) == 1 
    assert sell_order1.quantity == 2




def test_buy_price_priority():
    engine = MatchingEngine()

    buy_order1 = Order(1, "BUY", 100, 3)
    buy_order2 = Order(2, "BUY", 105, 4)
    sell_order = Order(3, "SELL", 95, 5)

    engine.add_order(buy_order1)
    engine.add_order(buy_order2)
    engine.add_order(sell_order)

    assert len(engine.trades) == 2

    assert engine.trades[0]["buy_order_id"] == 2
    assert engine.trades[0]["price"] == 95
    assert engine.trades[0]["quantity"] == 4

    assert engine.trades[1]["buy_order_id"] == 1
    assert engine.trades[1]["price"] == 95
    assert engine.trades[1]["quantity"] == 1

    assert buy_order1.quantity == 2
    assert buy_order2.quantity == 0
    assert sell_order.quantity == 0

    assert len(engine.order_book.buy_orders) == 1
    assert len(engine.order_book.sell_orders) == 0
