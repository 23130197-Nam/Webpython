from django.db import models
from categories.models import Category


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    #category_id nó cột trong product (khóa ngoại)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=0)
    old_price = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True) #từ 12k xuong 11k
    stock_qty = models.IntegerField(default=0)
    images = models.CharField(max_length=500, null=True, blank=True)
    # thuộc tính linh hoạt, cái này có khi là không cần thiết!!!!!!!
    attributes = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    # 1 đơn vị bán
    unit = models.CharField(max_length=20, default='pack')
    sold =  models.IntegerField(default=0)
    # trọng lượng của 1 đơn vị bán
    weight_per_unit = models.FloatField(default=0.0)
    expiry_date = models.DateTimeField(null=True, blank=True)#ngày hết hạn
    manufacturing_date = models.DateTimeField(null=True, blank=True)#ngày sản xuất
    calories = models.IntegerField(null=True, blank=True)
    # danh sách thành phần 
    ingredients = models.TextField(null=True, blank=True)
    # bị thừa vì đã có danh sách thành phần rồi !!!!!!!
    #allergens = models.JSONField(default=list)
    # sản phẩm có dễ hư hỏng không
    is_perishable = models.BooleanField(default=False)
    # hướng đẫn sữ dụng, cảm giác hơi thừa!!!!!!!!
    #storage_instructions = models.TextField(blank=True)
    rating_average = models.FloatField(default=0.0) # Ví dụ: 4.5
    review_count = models.IntegerField(default=0)   # Ví dụ: 120 đánh giá
    sku = models.CharField(max_length=100, unique=True, null=True, blank=True)
    # mã vạch
    barcode = models.CharField(max_length=100, null=True, blank=True)
    brand = models.CharField(max_length=100, null=True, blank=True)
    # từ khóa tìm kiếm
    tags = models.JSONField(default=list) 
    # tích hợp từ google để tìm kiếm
    #seo_title = models.CharField(max_length=200, null=True, blank=True)
    #seo_description = models.TextField(null=True, blank=True)
    # đánh dấu sản phẩm nỗi bật 
    featured = models.BooleanField(default=False)
    # trọng lượng và kích thước
    weight = models.FloatField(default=0.0)
    dimensions = models.JSONField(default=dict)
    #thêm cái ngày tạo
    created_at = models.DateTimeField(auto_now_add=True) # Tự động lấy giờ hiện tại khi tạo mới
    updated_at = models.DateTimeField(auto_now=True)     # Tự động cập nhật giờ khi sửa
    # ===== REPRESENTATION =====
    def __str__(self):
        return self.name
    