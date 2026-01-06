from django.db import models
from django.utils import timezone
from decimal import Decimal
from django.db.models.manager import Manager
from django.core.exceptions import ValidationError
from products.models import Product

# Create your models here.
class PromotionBase(models.Model):
    DISCOUNT_TYPES = [
        ('PERCENT', 'Percentage/Fixed Discount'),
        ('BUY_X_GET_Y', 'Buy X Get Y Discount'), 
    ]
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES, help_text="Loại chiến lược giảm giá sẽ áp dụng")
    code = models.CharField(max_length=50, unique=True, help_text="Mã khuyến mãi")
    description = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField()
    def __str__(self):
        return f"{self.code} ({self.discount_type})"
    def save(self, *args, **kwargs):
        if isinstance(self, PercentageDiscount):
            self.discount_type = 'PERCENT'
        elif isinstance(self, BuyXGetYDiscount):
            self.discount_type = 'BUY_X_GET_Y'
        super().save(*args, **kwargs)  
    class Meta:
        # abstract = True
        verbose_name = "Promotion Base"

# giảm giá % theo đơn hàng
class PercentageDiscount(PromotionBase):
    value = models.DecimalField(max_digits=10, decimal_places=2, help_text="Giá trị giảm giá (ví dụ: 0.10 cho 10% hoặc 50000 VND)")
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Số tiền đơn hàng tối thiểu để áp dụng")
    class Meta:
        verbose_name = "Percentage/Fixed Promotion"
        verbose_name_plural = "Percentage/Fixed Promotions"
    def clean(self):
        if self.value > 100:
            raise ValidationError("Giảm giá theo % không được vượt quá 100")
        
# giảm giá % theo sản phẩm 
class PercentageDiscountProduct(PromotionBase):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='promotions')
    value = models.DecimalField(max_digits=10, decimal_places=2, help_text="Giá trị giảm giá (ví dụ: 0.10 cho 10% hoặc 50000 VND)")
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Số tiền đơn hàng tối thiểu để áp dụng")
    class Meta:
        verbose_name = "Percentage/Fixed Promotion"
        verbose_name_plural = "Percentage/Fixed Promotions"
    def clean(self):
        if self.value > 100:
            raise ValidationError("Giảm giá theo % không được vượt quá 100")
        
#  mua 1 tặng 1 theo sản phẩm
class BuyXGetYDiscount(PromotionBase):
    # product_sku = models.CharField( max_length=100, help_text="Mã SKU của sản phẩm áp dụng cho Mua X Tặng Y")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='promotion')
    buy_quantity = models.PositiveIntegerField(help_text="Số lượng mua tối thiểu (X)")
    get_quantity = models.PositiveIntegerField(help_text="Số lượng tặng (Y)")
    class Meta:
        verbose_name = "Buy X Get Y Promotion"
        verbose_name_plural = "Buy X Get Y Promotions"
