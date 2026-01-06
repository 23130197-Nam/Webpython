from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'sku', 'category', 'price', 'stock_qty', 'is_active', 'featured']
    list_filter = ['is_active', 'featured', 'is_perishable', 'category']
    search_fields = ['name', 'sku', 'description', 'brand']
    ordering = ['-id']
    list_editable = ['is_active', 'featured', 'price']
    readonly_fields = ['id']
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('name', 'category', 'price', 'old_price', 'stock_qty', 'unit', 'sku', 'barcode', 'brand', 'sold')
        }),
        ('Hình ảnh (JSON)', {
            'fields': ('images',),
            'description': 'Nhập danh sách ảnh dạng: ["url1", "url2"]'
        }),
        ('Chi tiết sản phẩm', {
            'fields': ('description', 'ingredients', 'expiry_date', 'manufacturing_date', 'calories', 'is_perishable')
        }),
        ('Thông số kỹ thuật', {
            'fields': ('weight', 'weight_per_unit', 'dimensions', 'attributes', 'tags')
        }),
        ('Marketing & Đánh giá', {
            'fields': ('featured', 'is_active', 'rating_average', 'review_count')
        }),
    )
    
    # rating_average và review_count nên để readonly vì nó tự tính toán
    readonly_fields = ['rating_average', 'review_count']