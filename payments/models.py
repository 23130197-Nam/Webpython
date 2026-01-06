from django.db import models
from orders.models import Order

class Payment(models.Model):
    # orderId = models.CharField(max_length=100)
    order = models.ForeignKey(Order,on_delete=models.CASCADE,related_name='payments')
    method = models.CharField(max_length=50)
    providerReference = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)
    status = models.CharField(max_length=50, default='PENDING')
    paidAt = models.DateTimeField(null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} for Order {self.order} - {self.status}"
    
class PaymentMethod(models.Model):
    code = models.CharField(max_length=50, unique=True, help_text="Mã định danh (VD: VNPAY, MOMO, COD)")
    name = models.CharField(max_length=100, help_text="Tên hiển thị (VD: Ví VNPAY)")
    icon_url = models.CharField(max_length=255, null=True, blank=True, help_text="Link icon hoặc dùng path static")
    is_active = models.BooleanField(default=True, help_text="Bật/Tắt phương thức này")
    order_display = models.IntegerField(default=0, help_text="Thứ tự hiển thị trên web")

    class Meta:
        verbose_name = "Phương thức thanh toán"
        ordering = ['order_display']

    def __str__(self):
        return self.name