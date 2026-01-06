from rest_framework import serializers
from products.models import Product
from categories.models import Category

# 1. SERIALIZER CHO DANH SÁCH (Trang chủ, Category, Search)
class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    thumbnail = serializers.CharField(source='images', read_only=True)
    discount_percent = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 
            'price', 'old_price', 'discount_percent', 
            'thumbnail',                            
            'rating_average', 'review_count',         
            'unit', 'featured', 'is_active',
            'category_name', 'category', 'attributes',
        ]

    def get_discount_percent(self, obj: Product):
        if obj.old_price and obj.old_price > obj.price:
            percent = int(100 - (obj.price / obj.old_price * 100))
            return f"-{percent}%"
        return None

# 2. SERIALIZER CHO CHI TIẾT (Trang Detail)
class ProductDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    discount_percent = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku',
            'price', 'old_price', 'discount_percent',
            'images',           # 
            'description',
            'rating_average', 'review_count',
            'unit', 'stock_qty',
            'ingredients', 'calories', 'expiry_date', 
            'category', 'category_name', 'is_active'
        ]
   

    def get_discount_percent(self, obj:Product):
        if obj.old_price and obj.old_price > 0 and obj.old_price > obj.price:
            percent = int(100 - (obj.price / obj.old_price * 100))
            return f"-{percent}%"
        return None


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.URLField(), 
        required=False, 
        allow_empty=True
    )

    class Meta:
        model = Product
        fields = '__all__'

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Giá không được âm")
        return value
    
    # Nếu bạn muốn Logic tạo nằm ở Service, thì View nên gọi Service.
    # Serializer chỉ nên validate dữ liệu thôi.