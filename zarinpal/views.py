from django.http import HttpResponseRedirect, HttpResponse
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from zeep import Client

from purchase.models import Order, Payment, Price, Item
from zarinpal.serializers import OrderPaymentSerializer
from zarinpal.settings import MERCHANT, CALLBACK, FAIL_REDIRECT, SUCCESS_REDIRECT

client = Client('https://www.zarinpal.com/pg/services/WebGate/wsdl')


class OrderPaymentRequestView(GenericAPIView):
    serializer_class = OrderPaymentSerializer

    def post(self, request: Request) -> HttpResponse:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order_id = serializer.validated_data['order_id']
        order = Order.objects.get(pk=order_id)
        if order is None:
            return Response({'error_msg': 'invalid order id'}, status=status.HTTP_404_NOT_FOUND)

        items = Item.objects.filter(order_id=order_id)
        user = order.user
        amount = 0
        mobile = '0' + str(user.phone)
        email = user.email
        for item in items:
            price = Price.objects.filter(product_id=item.product.pk).first()
            amount = amount + price.amount

        result = client.service.PaymentRequest(
            MERCHANT,
            amount,
            'description',
            email,
            mobile,
            CALLBACK,
        )

        payment = Payment(order=order, type_id=Payment.Type.ONLINE, identity_token=result.Authority, verify=False)
        payment.save()

        if result.Status == 100:
            return HttpResponseRedirect(redirect_to=f'https://www.zarinpal.com/pg/StartPay/{result.Authority}')
        return Response({'error_code': result.Status}, status=status.HTTP_400_BAD_REQUEST)


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

        amount = 0
        payment = Payment.objects.get(identity_token=authority)
        order = Order.objects.get(pk=payment.order.pk)
        items = Item.objects.filter(order_id=order.pk)
        for item in items:
            price = Price.objects.filter(product_id=item.product.pk).first()
            amount = amount + price.amount

        result = client.service.PaymentVerification(MERCHANT, authority, amount)
        if result.Status == 100:
            payment.ref_id = result.RefID
            payment.save()
            return HttpResponseRedirect(redirect_to=f'{SUCCESS_REDIRECT}?authority={result.Authority}')
        return HttpResponseRedirect(redirect_to=f'{FAIL_REDIRECT}?error_code={result.Status}')
