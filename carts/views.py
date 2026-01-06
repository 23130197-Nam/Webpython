from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render

from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from .services import CartService

def cart_page(request):
    return render(request, "cart.html")


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    @action(detail=False, methods=["get"], url_path="user/(?P<user_id>[^/.]+)")
    def get_by_user(self, request, user_id=None):
        cart = CartService.get_cart_by_user(user_id)
        if not cart:
            return Response(
                {"error": "Cart not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def add_item(self, request, pk=None):
        cart = self.get_object()

        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))
        attributes = request.data.get("attributes", {})

        if not product_id:
            return Response(
                {"error": "product_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item = CartService.add_item_to_cart(
            cart_id=cart.id,
            product_id=product_id,
            quantity=quantity,
            attributes=attributes
        )

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def remove_item(self, request, pk=None):
        cart = self.get_object()
        product_id = request.data.get("product_id")

        if not product_id:
            return Response(
                {"error": "product_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        CartService.remove_item_from_cart(cart.id, product_id)
        return Response({"message": "Item removed"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def update_quantity(self, request, pk=None):
        cart = self.get_object()

        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity")

        if product_id is None or quantity is None:
            return Response(
                {"error": "product_id and quantity are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        CartService.update_item_quantity(cart.id, product_id, int(quantity))
        cart.refresh_from_db()

        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def clear_cart(self, request, pk=None):
        cart = self.get_object()
        CartService.clear_cart(cart.id)
        cart.refresh_from_db()

        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def apply_discount(self, request, pk=None):
        cart = self.get_object()
        discount_amount = request.data.get("discount_amount")

        if discount_amount is None:
            return Response(
                {"error": "discount_amount is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart = CartService.apply_discount(cart.id, discount_amount)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def set_shipping(self, request, pk=None):
        cart = self.get_object()
        shipping_fee = request.data.get("shipping_fee")

        if shipping_fee is None:
            return Response(
                {"error": "shipping_fee is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart = CartService.set_shipping_fee(cart.id, shipping_fee)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
