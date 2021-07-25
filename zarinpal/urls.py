from django.urls import path

from zarinpal.views import OrderPaymentRequestView, PaymentVerificationView

urlpatterns = [
    path('order_payment_request/', OrderPaymentRequestView.as_view()),
    path('payment_verification/', PaymentVerificationView.as_view())
]
