from rest_framework import serializers
from .models import Cart, CartItem
from products.models import Product
from promotions.services import get_product_discount_price



class CartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="product.id", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_image = serializers.CharField(
        source="product.image",
        read_only=True,
        allow_null=True
    )
    product_price = serializers.DecimalField(
        source="product.price",
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product_id",
            "product_name",
            "product_image",
            "product_price",
            "quantity",
            "unit_price",
            "is_select",
            "total_price",
            "created_at",
            "updated_at",
        ]

    def get_line_total(self, obj):
        price = self.get_price(obj)
        return price["final"] * obj.quantity
    
    def get_total_price(self, obj):
        discounted_price = get_product_discount_price(obj.product)
        return discounted_price * obj.quantity
    
    # def get_total_price(self, obj):
    #     return obj.unit_price * obj.quantity

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = [
            "id",
            "currency",
            "subtotal",
            "created_at",
            "updated_at",
        ]


class AddCartItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1, min_value=1)

class UpdateCartItemQuantitySerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=0)

class SelectCartItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    is_select = serializers.BooleanField()

class SelectAllCartItemSerializer(serializers.Serializer):
    is_select = serializers.BooleanField(default=True)

class RemoveCartItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()

