from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.request import Request

from .serializers import CartSerializer,CartItemSerializer
from .services import CartService
from users.models import User
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def cart_page(request):
    return render(request, "carts/cart.html")

class CartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart = CartService.get_cart(request.user)
        if not cart:
            cart = CartService.create_cart(request.user)

        items = CartService.get_cart_items(cart)

        data = CartSerializer(cart).data
        data["items"] = CartItemSerializer(items, many=True).data

        return Response(data, status=status.HTTP_200_OK)
    

class SelectCartItemAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        cart = CartService.get_cart(request.user)
        if not cart:
            return Response({"detail": "Cart not found"}, status=404)

        product_id = request.data.get("product_id")
        is_select = request.data.get("is_select")

        if product_id is None or is_select is None:
            return Response(
                {"detail": "product_id & is_select required"},
                status=400
            )

        CartService.set_item_select(
            cart=cart,
            product_id=product_id,
            is_select=bool(is_select)
        )

        return Response(CartSerializer(cart).data)

class SelectAllCartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        cart = CartService.get_cart(request.user)
        if not cart:
            return Response({"detail": "Cart not found"}, status=404)

        is_select = request.data.get("is_select", True)

        CartService.set_select_all(cart, bool(is_select))

        return Response(CartSerializer(cart).data)

class AddItemAPIView(APIView):

    permission_classes = [IsAuthenticated]
    # /api/cart/add/
    def post(self, request):

        cart = CartService.get_cart(request.user)
        if not cart:
            cart = CartService.create_cart(request.user)

        product_id = request.data.get('product_id')
        try:
            quantity = int(request.data.get('quantity', 1))
        except (TypeError, ValueError):
            return Response( {'detail': 'quantity must be an integer'}, status=status.HTTP_400_BAD_REQUEST)
        origin = request.data.get('origin', {})
        CartService.add_item_to_cart(cart=cart, product_id=product_id, quantity=quantity, origin=origin )

        return Response(CartSerializer(cart).data)

class UpdateItemAPIView(APIView):
    permission_classes = [IsAuthenticated]
    # /api/cart/update/
    def patch(self, request):

        cart = CartService.get_cart(request.user)
        if not cart:
            return Response({'detail': 'Cart not found'},status=status.HTTP_404_NOT_FOUND)

        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 0))

        CartService.update_item_quantity(cart=cart,product_id=product_id, quantity=quantity)

        return Response(CartSerializer(cart).data)
    
class RemoveItemAPIView(APIView):
    permission_classes = [IsAuthenticated]
    # /api/cart/remove/
    def delete(self, request):

        cart = CartService.get_cart(request.user)
        if not cart:
            return Response(
                {'detail': 'Cart not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        product_id = request.data.get('product_id')

        CartService.remove_item_from_cart(cart, product_id)

        return Response(CartSerializer(cart).data)
    

class ClearCartAPIView(APIView):
    permission_classes = [IsAuthenticated]
    # /api/cart/clear/
    def delete(self, request):

        cart = CartService.get_cart(request.user)
        if not cart:
            return Response({'detail': 'Cart not found'},status=status.HTTP_404_NOT_FOUND)

        CartService.clear_cart(cart)

        return Response(CartSerializer(cart).data)

