from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'product',
            'sku',
            'name',
            'quantity',
            'unit_price',
            'line_total',
            'created_at',
        ]
        read_only_fields = fields

    def get_line_total(self, obj):
        return obj.line_total

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'shipping_address',
            'billing_address',

            'subtotal',
            'discount',
            'shipping_fee',
            'total',

            'payment_method',
            'payment_status',
            'fulfillment_status',

            'items',

            'created_at',
            'updated_at',
        ]
        read_only_fields = fields

class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.IntegerField()
    shipping_address_id = serializers.IntegerField()
    billing_address_id = serializers.IntegerField()
    payment_method = serializers.CharField(max_length=50)

class UpdateOrderStatusSerializer(serializers.Serializer):
    fulfillment_status = serializers.ChoiceField(
        choices=[
            'PENDING',
            'PROCESSING',
            'SHIPPED',
            'DELIVERED',
            'CANCELLED',
        ]
    )

class ApplyDiscountSerializer(serializers.Serializer):
    discount = serializers.DecimalField(max_digits=12, decimal_places=2)

class SetShippingFeeSerializer(serializers.Serializer):
    shipping_fee = serializers.DecimalField(max_digits=12, decimal_places=2)
