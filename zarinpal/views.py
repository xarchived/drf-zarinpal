from django.http import HttpResponseRedirect, HttpResponse
from rest_framework.exceptions import APIException
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.views import APIView
from zeep import Client

from purchase.models import Order, Payment
from zarinpal.serializers import OrderPaymentSerializer
from zarinpal.settings import DESCRIPTION, MERCHANT, CALLBACK, FAIL_REDIRECT, SUCCESS_REDIRECT
from zarinpal.utils import calculate_total_amount

client = Client('https://www.zarinpal.com/pg/services/WebGate/wsdl')


class OrderPaymentRequestView(GenericAPIView):
    serializer_class = OrderPaymentSerializer

    def post(self, request: Request) -> HttpResponse:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order_id = serializer.validated_data['order_id']
        order = Order.objects.get(pk=order_id)
        if order is None:
            raise APIException('Order not found')

        user = order.user
        price = calculate_total_amount(order_id)

        result = client.service.PaymentRequest(
            MERCHANT,
            price,
            DESCRIPTION,
            user.email,
            f'0{user.phone}',
            CALLBACK,
        )

        payment = Payment(order=order, type_id=Payment.Type.ONLINE, identity_token=result.Authority, verify=False)
        payment.save()

        if result.Status == 100:
            return HttpResponseRedirect(redirect_to=f'https://www.zarinpal.com/pg/StartPay/{result.Authority}')
        raise APIException('Bad Request')


class PaymentVerificationView(APIView):
    # noinspection PyMethodMayBeStatic
    def get(self, request: Request) -> HttpResponse:
        status_code = request.GET.get('Status')
        authority = request.GET.get('Authority')

        if not status_code:
            return HttpResponseRedirect(redirect_to=f'{FAIL_REDIRECT}')
        if status_code == 'NOK':
            return HttpResponseRedirect(redirect_to=f'{FAIL_REDIRECT}?status_code=NOK')
        if status_code != 'OK':
            return HttpResponseRedirect(redirect_to=f'{FAIL_REDIRECT}?status_code={status_code}')

        payment = Payment.objects.get(identity_token=authority)
        order = Order.objects.get(pk=payment.order.pk)
        price = calculate_total_amount(order.pk)

        result = client.service.PaymentVerification(MERCHANT, authority, price)
        if result.Status == 100:
            payment.ref_id = result.RefID
            payment.save()
            return HttpResponseRedirect(redirect_to=f'{SUCCESS_REDIRECT}?authority={result.Authority}')
        return HttpResponseRedirect(redirect_to=f'{FAIL_REDIRECT}?error_code={result.Status}')
