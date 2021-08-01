from rest_framework.exceptions import APIException
from django.utils.translation import gettext_lazy as _


class OrderNotFoundError(APIException):
    status_code = 404
    default_detail = _('order not found')


class PaymentError(APIException):
    status_code = 400
    default_detail = _('order not found')
