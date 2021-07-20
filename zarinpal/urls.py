from django.urls import path

from zarinpal.views import CreditPaymentRequestView, PaymentVerificationView

urlpatterns = [
    path('credit_payment_request/', CreditPaymentRequestView.as_view()),
    path('payment_verification/', PaymentVerificationView.as_view())
]
