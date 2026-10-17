from chronos.order import Order


class OrderBook:
    def __init__(self):
        self.buy_orders = []
        self.sell_orders = []

    def add_order(self, order):
        if not isinstance(order, Order):
            raise TypeError("Expected an Order object")

        # Prevent duplicate order IDs across both sides
        for existing_order in self.get_all_orders():
            if existing_order.order_id == order.order_id:
                raise ValueError(
                    f"Order ID {order.order_id} already exists"
                )

        if order.side == "BUY":
            self.buy_orders.append(order)
            self.buy_orders.sort(key=lambda item: item.price, reverse=True)

        else:
            self.sell_orders.append(order)
            self.sell_orders.sort(key=lambda item: item.price)

    def cancel_order(self, order_id):
        for orders in (self.buy_orders, self.sell_orders):
            for index, order in enumerate(orders):
                if order.order_id == order_id:
                    del orders[index]
                    return True

        return False

    def get_best_buy(self):
        if self.buy_orders:
            return self.buy_orders[0]

        return None

    def get_best_sell(self):
        if self.sell_orders:
            return self.sell_orders[0]

        return None

    def get_all_orders(self):
        return self.buy_orders + self.sell_orders

    def __repr__(self):
        return (
            f"OrderBook("
            f"buy_orders={self.buy_orders}, "
            f"sell_orders={self.sell_orders})"
        )