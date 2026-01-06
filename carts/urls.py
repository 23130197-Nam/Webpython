from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet, CartItemViewSet, cart_page

router = DefaultRouter()
router.register(r"carts", CartViewSet, basename="cart")
router.register(r"cart-items", CartItemViewSet, basename="cart-item")
app_name = 'carts'
urlpatterns = [
    path("", cart_page, name="cart-page"),
    path("api/", include(router.urls)),
    
]
