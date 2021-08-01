from purchase.models import Item


def calculate_total_amount(order_id: int) -> int:
    items = Item.objects.filter(order_id=order_id)
    return sum([item.price.amount for item in items])
