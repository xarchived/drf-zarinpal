from purchase.models import Order


def calculate_total_amount(order_id: int) -> int:
    order = Order.objects.get(pk=order_id)

    return sum([item.price.amount for item in order.items.all()])
