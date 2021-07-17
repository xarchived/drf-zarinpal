from rest_framework.fields import IntegerField, EmailField, CharField
from rest_framework.serializers import Serializer


# noinspection PyAbstractClass
class CreditPaymentSerializer(Serializer):
    description = CharField(
        required=False,
        max_length=50,
        allow_blank=True,
    )
    email = EmailField(
        required=False,
        min_length=3,
        max_length=320,
    )
    mobile = IntegerField(
        required=False,
        min_value=1000000000,
        max_value=9999999999,
    )
    amount = IntegerField(
        required=True,
        min_value=0,
        max_value=999999999999999999,
    )
