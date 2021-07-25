from rest_framework.fields import IntegerField, EmailField, CharField
from rest_framework.serializers import Serializer


# noinspection PyAbstractClass
class OrderPaymentSerializer(Serializer):
    order_id = IntegerField(
        required=True,
        min_value=1
    )
