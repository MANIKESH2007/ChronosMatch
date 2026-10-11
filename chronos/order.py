class Order:
    def __init__(self, order_id, side, price, quantity, order_type="LIMIT"):
        # Validate order ID
        if not isinstance(order_id, int) or isinstance(order_id, bool) or order_id <= 0:
            raise ValueError("Order ID must be a positive integer")

        # Validate order side
        if side not in ("BUY", "SELL"):
            raise ValueError("Side must be BUY or SELL")

        # Validate price
        if not isinstance(price, (int, float)) or isinstance(price, bool):
            raise ValueError("Price must be a number")

        if price <= 0:
            raise ValueError("Price must be positive")

        # Validate quantity
        if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity <= 0:
            raise ValueError("Quantity must be a positive integer")

        # Validate order type
        if order_type not in ("LIMIT", "MARKET"):
            raise ValueError("Order type must be LIMIT or MARKET")

        # Store order information
        self.order_id = order_id
        self.side = side
        self.price = float(price)
        self.quantity = quantity
        self.order_type = order_type

    def __repr__(self):
        return (
            f"Order(id={self.order_id}, "
            f"side={self.side}, "
            f"price={self.price}, "
            f"quantity={self.quantity}, "
            f"type={self.order_type})"
        )