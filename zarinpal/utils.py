from purchase.models import Item, Order


def calculate_total_amount(order_id: int) -> int:
    items = Item.objects.filter(order_id=order_id)
    order = Order.objects.get(pk=order_id)
    price = sum([item.price.amount for item in items])

    price = price * order.duration

    if order.duration == 31:
        price = price + 5000

    if order.duration == 62:
        price = price + 7000

    if order.duration == 93:
        price = price + 9000

    return price
