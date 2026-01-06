from django.db import models
from django.db import models
from products.models import Product

class Cart(models.Model):
    id = models.CharField(max_length=100, primary_key=True) # = user_id 
    # user_id = models.CharField(max_length=100, default='guest')
    currency = models.CharField(max_length=10, default='VND')# tiền tệ có hay không 
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0) # Tổng tất cả khi giảm giá Cho Sản phẩm
    # discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart {self.id}"

    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # quantity = models.IntegerField(default=1)
    # thay đổi là số lượng thì không có số âm 
    is_select = models.BooleanField(default=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2) # tiền sản phẩm sau giảm giá
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 
    
    # trong giỏ chỉ có 1 sản phẩm ko có cái giống 
    class Meta:
        unique_together = ['cart', 'product', 'unit_price']


    def __str__(self) -> str:
        return f"{self.quantity} x {self.product.name} in Cart {self.cart.id}"
    
