from django.db import models
from decimal import Decimal
from users.models import User, Address
from products.models import Product


class Order(models.Model):
    user_id = models.IntegerField()
    shipping_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, related_name='shipping_orders')
    billing_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, related_name='billing_orders')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.BooleanField(default=False)  # True if paid
    fulfillment_status = models.CharField(max_length=50, default='pending')
    # chỉnh thành khóa ngoại
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Order {self.id} for user {self.user_id}"

    def recalculate_totals(self):
        """Recalculate order totals"""
        self.subtotal = sum(item.line_total for item in self.items.all())
        self.total = self.subtotal - self.discount + self.shipping_fee
        self.save()

    def set_status(self, status):
        self.fulfillment_status = status
        self.save()

    def set_shipping_fee(self, fee):
        self.shipping_fee = fee
        self.recalculate_totals()

    def set_discount_amount(self, discount):
        self.discount = discount
        self.recalculate_totals()

    @classmethod
    def create(cls, user, shipping_address, billing_address, payment_method):
        order = cls(
            user_id=user.id,
            shipping_address=shipping_address,
            billing_address=billing_address,
            payment_method=payment_method
        )
        order.save()
        return order

    @classmethod
    def get_orders_by_user(cls, user_id):
        return cls.objects.filter(user_id=user_id)

    @classmethod
    def get(cls, id, user):
        try:
            return cls.objects.get(id=id, user_id=user.id)
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_pending_orders(cls):
        return cls.objects.filter(fulfillment_status='pending')

    @classmethod
    def get_recent_orders(cls, days=30):
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        return cls.objects.filter(created_at__gte=cutoff_date)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    sku = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.quantity} x {self.name} in Order {self.order.id}"

    @property
    def line_total(self) -> Decimal:
        return self.unit_price * self.quantity

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Recalculate order totals when item changes
        self.order.recalculate_totals()

    @classmethod
    def create(cls, order, product, quantity, unit_price):
        item = cls(
            order=order,
            product=product,
            sku=getattr(product, 'sku', str(product.id)),
            name=product.name,
            quantity=quantity,
            unit_price=unit_price
        )
        item.save()
        return item
