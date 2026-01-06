# from django.urls import path
# from .views import CreatePaymentAPIView

 # urlpatterns = [path('create/', CreatePaymentAPIView.as_view(), name='create-payment'),]


from django.urls import path
from .views import CreatePaymentAPIView, payment_page

urlpatterns = [
    path('', payment_page, name='payment-page'),
    path('create/', CreatePaymentAPIView.as_view(), name='create-payment'),
]

