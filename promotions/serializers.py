from rest_framework import serializers
from .models import PromotionBase, PercentageDiscount, BuyXGetYDiscount
from decimal import Decimal
from typing import List

# Sử dụng Forward Reference cho CartItem nếu nó nằm trong app khác (ví dụ: 'carts.models')

# Các Serializer để chuyển đổi từ Model sang JSON và ngược lại.
class PromotionBaseSerializer(serializers.ModelSerializer):
    discount_type_display = serializers.CharField(source='get_discount_type_display', read_only=True)
    class Meta:
        model = PromotionBase
        fields = ['id', 'discount_type', 'discount_type_display', 'code', 'description', 'is_active', 'valid_from', 'valid_to']
        read_only_fields = ['discount_type']

class PercentageDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = PercentageDiscount
        fields = PromotionBaseSerializer.Meta.fields + ['value', 'min_amount']

class BuyXGetYDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuyXGetYDiscount
        fields = PromotionBaseSerializer.Meta.fields + ['product_sku', 'buy_quantity', 'get_quantity']
#  Các Serializer cho API áp dụng khuyến mãi.
class CartItemInputSerializer(serializers.Serializer):
    product_sku = serializers.CharField(max_length=100)
    quantity = serializers.IntegerField(min_value=1)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)

class PromotionApplyInputSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    cart_items_data = CartItemInputSerializer(many=True, required=True)

class DiscountResultSerializer(serializers.Serializer):
    discount_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    final_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    promotion = PromotionBaseSerializer(read_only=True)