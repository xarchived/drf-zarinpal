from django.urls import path

from zarinpal.views import CreditPaymentRequestView, PaymentVerificationView

urlpatterns = [
    path('credit_request/', CreditPaymentRequestView.as_view()),
    path('verification/', PaymentVerificationView.as_view())
]
