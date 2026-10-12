from chronos.order_book import OrderBook


class MatchingEngine:
    def __init__(self):
        self.order_book = OrderBook()
        self.trades = []

    def add_order(self, order):
        self.order_book.add_order(order)
        self.match_orders()

    def match_orders(self):
        while True:
            buy_order = self.order_book.get_best_buy()
            sell_order = self.order_book.get_best_sell()

            # Stop if either side has no orders
            if buy_order is None or sell_order is None:
                break

            # Stop if the prices do not match
            if buy_order.price < sell_order.price:
                break

            # Determine the quantity to trade
            trade_quantity = min(
                buy_order.quantity,
                sell_order.quantity
            )

            # Record the executed trade
            trade = {
                "buy_order_id": buy_order.order_id,
                "sell_order_id": sell_order.order_id,
                "price": sell_order.price,
                "quantity": trade_quantity
            }

            self.trades.append(trade)

            # Update the remaining quantities
            buy_order.quantity -= trade_quantity
            sell_order.quantity -= trade_quantity

            # Remove completely filled orders
            if buy_order.quantity == 0:
                self.order_book.cancel_order(buy_order.order_id)

            if sell_order.quantity == 0:
                self.order_book.cancel_order(sell_order.order_id)