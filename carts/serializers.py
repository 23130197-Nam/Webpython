from rest_framework import serializers
from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    line_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'product_name', 'quantity', 'unit_price', 
                  'attributes', 'line_total', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'line_total']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'user_id', 'currency', 'subtotal', 'discount', 'shipping_fee', 
                  'total', 'items', 'created_at', 'updated_at']
        read_only_fields = ['id', 'subtotal', 'total', 'created_at', 'updated_at']
