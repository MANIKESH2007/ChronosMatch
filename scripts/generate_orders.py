import random
from chronos.order import Order
def generate_orders(count,seed=42):
    if not isinstance(count,int) or isinstance(count,bool) or count<0:
        raise ValueError("count must be a non-negative integer")
    rng=random.Random(seed)
    orders=[]
    for order_id in range(1,count+1):
        side = rng.choice(["BUY","SELL"])
        price = round(rng.uniform(100,200),2)
        quantity = rng.randint(1,100)
        order = Order(
            order_id=order_id,
            side=side,
            price=price,
            quantity=quantity,
            order_type="LIMIT"
        )
        orders.append(order)
    return orders

if __name__=="__main__":
    generated_orders=generate_orders(10)
    for order in generated_orders:
        print(order)