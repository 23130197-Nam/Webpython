from django.db import models

# Create your models here.
from django.db import models
from decimal import Decimal
from products.models import Product
from users.models import User


class Cart(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    user_id = models.CharField(max_length=100, default='guest')
    currency = models.CharField(max_length=10, default='USD')# đel cần
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self) -> str:
        return f"Cart {self.id} with {self.items.count()} items"

    def recalculate_totals(self):   #adsad
        """Recalculate cart totals"""
        self.subtotal = sum(item.line_total for item in self.items.all())
        self.total = self.subtotal - self.discount + self.shipping_fee
        self.save()

    @classmethod
    def get_cart_by_user(cls, user_id):
        try:
            return cls.objects.get(user_id=str(user_id))
        except cls.DoesNotExist:
            return None

    @classmethod
    def create(cls, id, user):
        cart = cls(id=str(id), user_id=str(user.id if hasattr(user, 'id') else user))
        cart.save()
        return cart


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2) #500g/1
    origin = models.JSONField(default=dict,blank=True) #nguồn góc
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 

    class Meta:
        unique_together = ['cart', 'product']

    def __str__(self) -> str:
        return f"{self.quantity} x {self.product.name} in Cart {self.cart.id}"

    @property
    def line_total(self) -> Decimal:
        if self.unit_price is None or self.quantity is None:
            return Decimal("0")
        return self.unit_price * self.quantity

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Recalculate cart totals when item changes
        self.cart.recalculate_totals()
