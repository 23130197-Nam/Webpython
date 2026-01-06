from django.urls import path

from carts.views import (CartAPIView, AddItemAPIView, UpdateItemAPIView, RemoveItemAPIView, ClearCartAPIView, cart_page,SelectCartItemAPIView,SelectAllCartAPIView, )

urlpatterns = [

    path("page/", cart_page, name="cart_page"),

    path('cart/', CartAPIView.as_view()),
    path('cart/add/', AddItemAPIView.as_view()),
    path('cart/update/', UpdateItemAPIView.as_view()),
    path('cart/remove/', RemoveItemAPIView.as_view()),
    path('cart/clear/', ClearCartAPIView.as_view()),
    path("cart/select-item/", SelectCartItemAPIView.as_view()),
    path("cart/select-all/", SelectAllCartAPIView.as_view()),
    # path("api/cart/selected-items/", SelectedCartItemsAPIView.as_view()),
]
