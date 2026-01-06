from django.urls import path
from orders.views import (CheckOutDataView, payment_page, CreateOrderView, ApplyVoucherView)

urlpatterns = [
    path('order/', payment_page, name='payment_page'),
    path('checkout-data/', CheckOutDataView.as_view()),
    path('create/', CreateOrderView.as_view()),
    path('apply/', ApplyVoucherView.as_view()),
]
