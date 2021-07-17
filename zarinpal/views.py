from django.http import HttpResponseRedirect, HttpResponse
from redisary import Redisary
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from zeep import Client

from zarinpal.serializers import CreditPaymentSerializer
from zarinpal.settings import MERCHANT, CALLBACK, REDIS_DB

client = Client('https://www.zarinpal.com/pg/services/WebGate/wsdl')
authorities = Redisary(db=REDIS_DB)


class CreditPaymentRequestView(GenericAPIView):
    serializer_class = CreditPaymentSerializer

    def post(self, request: Request) -> HttpResponse:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = client.service.PaymentRequest(
            MERCHANT,
            serializer.validated_data['amount'],
            serializer.validated_data['description'],
            serializer.validated_data['email'],
            serializer.validated_data['mobile'],
            CALLBACK,
        )
        authorities[result.Authority] = serializer.validated_data['amount']

        if result.Status == 100:
            return HttpResponseRedirect(redirect_to=f'https://www.zarinpal.com/pg/StartPay/{result.Authority}')
        return Response({'error_code': result.Status}, status=status.HTTP_400_BAD_REQUEST)


class PaymentVerificationView(APIView):
    # noinspection PyMethodMayBeStatic
    def get(self, request: Request) -> Response:
        status_code = request.GET.get('Status')
        authority = request.GET.get('Authority')

        if not status_code:
            return Response({'detail': 'nothing provided'}, status=status.HTTP_400_BAD_REQUEST)
        if status_code == 'NOK':
            return Response({'detail': 'failed or canceled'}, status=status.HTTP_400_BAD_REQUEST)
        if status_code != 'OK':
            return Response({'detail': 'unknown status'}, status=status.HTTP_400_BAD_REQUEST)

        amount = authorities[authority]
        result = client.service.PaymentVerification(MERCHANT, authority, amount)

        if result.Status == 100:
            return Response({'ref_id': result.RefID}, status=status.HTTP_200_OK)
        if result.Status == 101:
            return Response({'detail': 'already verified'}, status=status.HTTP_409_CONFLICT)
        return Response({'error_code': result.Status}, status=status.HTTP_400_BAD_REQUEST)
