from django.http import HttpResponseRedirect, HttpResponse
from purchase.models import Order, Payment
from purchase.utils import order_total_price
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.request import Request
from rest_framework.views import APIView
from zeep import Client

from zarinpal.exceptions import OrderNotFoundError, PaymentError
from zarinpal.serializers import OrderPaymentSerializer
from zarinpal.settings import DESCRIPTION, MERCHANT, CALLBACK, REDIRECT_URL

client = Client('https://www.zarinpal.com/pg/services/WebGate/wsdl')


class OrderPaymentRequestView(GenericAPIView):
    serializer_class = OrderPaymentSerializer

    def get(self, request: Request) -> HttpResponse:
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        order_id = serializer.validated_data['order_id']
        order = get_object_or_404(Order, id=order_id)
        if order is None:
            raise OrderNotFoundError()

        user = order.user
        price = order_total_price(order_id)

        if price == 0:
            payment = Payment(order=order, type_id=Payment.Type.FREE, identity_token=0, ref_id=0)
            payment.save()
            return HttpResponseRedirect(redirect_to=f'{REDIRECT_URL}?ref_id=0&status=ok')

        result = client.service.PaymentRequest(
            MERCHANT,
            price,
            DESCRIPTION,
            user.email,
            f'0{user.phone}',
            CALLBACK,
        )

        payment = Payment(order=order, type_id=Payment.Type.ONLINE, identity_token=result.Authority)
        payment.save()

        if result.Status == 100:
            return HttpResponseRedirect(redirect_to=f'https://www.zarinpal.com/pg/StartPay/{result.Authority}')
        raise PaymentError(result.Status)


class PaymentVerificationView(APIView):
    # noinspection PyMethodMayBeStatic
    def get(self, request: Request) -> HttpResponse:
        status_code = request.GET.get('Status')
        authority = request.GET.get('Authority')

        if not status_code:
            return HttpResponseRedirect(redirect_to=f'{REDIRECT_URL}')
        if status_code == 'NOK':
            return HttpResponseRedirect(redirect_to=f'{REDIRECT_URL}?status=nok')
        if status_code != 'OK':
            return HttpResponseRedirect(redirect_to=f'{REDIRECT_URL}?status={status_code}')

        payment = get_object_or_404(Payment, identity_token=authority)
        price = order_total_price(order_id=payment.order_id)

        result = client.service.PaymentVerification(MERCHANT, authority, price)
        if result.Status == 100:
            payment.ref_id = result.RefID
            payment.save()
            return HttpResponseRedirect(redirect_to=f'{REDIRECT_URL}?ref_id={result.RefID}&status=ok')
        return HttpResponseRedirect(redirect_to=f'{REDIRECT_URL}?error_code={result.Status}&status=nok')
