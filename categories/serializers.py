from rest_framework import serializers
from .models import Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        # Chỉ lấy những trường Frontend thực sự cần dùng
        fields = ['id', 'name', 'description', 'image','icon','sort_order','is_active' ]
        # Không cần 'subcategories' vì mô hình phẳng
        # Không cần 'parent_category' vì không có cha