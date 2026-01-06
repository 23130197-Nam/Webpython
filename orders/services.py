from .models import Order, OrderItem
from users.models import User, Address
from products.models import Product
from carts.models import Cart
from decimal import Decimal


class OrderService:
    @staticmethod
    def calculate_total(order: Order):
        order.total = order.subtotal - order.discount + order.shipping_fee
        order.save(update_fields=['total'])
        return order.total

    @staticmethod
    def set_fulfillment_status(order: Order, status: str):
        order.fulfillment_status = status
        order.save(update_fields=['fulfillment_status'])

    @staticmethod
    def set_shipping_fee(order: Order, fee):
        order.shipping_fee = Decimal(fee)
        OrderService.calculate_total(order)

    @staticmethod
    def set_discount_amount(order: Order, discount):
        order.discount = Decimal(discount)
        OrderService.calculate_total(order)


    @staticmethod
    def create_order(user_id, shipping_address_id, billing_address_id, payment_method):
        user = User.objects.get(id=user_id)
        shipping_address = Address.objects.get(id=shipping_address_id)
        billing_address = Address.objects.get(id=billing_address_id)
        
        order = Order.create(user, shipping_address, billing_address, payment_method)
        return order
    
    @staticmethod
    def create_order_from_cart(cart_id, shipping_address_id, billing_address_id, payment_method):
        cart = Cart.objects.get(id=cart_id)
        user = User.objects.get(id=cart.user_id)
        shipping_address = Address.objects.get(id=shipping_address_id)
        billing_address = Address.objects.get(id=billing_address_id)
        
        order = Order.create(user, shipping_address, billing_address, payment_method)
        
        for cart_item in cart.items.all():
            OrderItem.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price
            )
        
        order.subtotal = cart.subtotal
        order.discount = cart.discount
        order.shipping_fee = cart.shipping_fee
        order.total = cart.total
        order.save()
        
        return order
    
    @staticmethod
    def add_item_to_order(order_id, product_id, quantity):
        order = Order.objects.get(id=order_id)
        product = Product.objects.get(id=product_id)
        
        OrderItem.create(
            order=order,
            product=product,
            quantity=quantity,
            unit_price=product.price
        )
        return order
    
    @staticmethod
    def get_order(order_id, user_id):
        try:
            return Order.get_orders_by_user(user_id)
            return Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return None
    
    @staticmethod
    def get_orders_by_user(user_id):
        return Order.get_orders_by_user(user_id)
    
    @staticmethod
    def get_pending_orders():
        return Order.get_pending_orders()
    
    @staticmethod
    def get_recent_orders(days=30):
        return Order.get_recent_orders(days)
    
    @staticmethod
    def update_order_status(order_id, status):
        order = Order.objects.get(id=order_id)
        order.set_status(status)
        return order
    
    @staticmethod
    def mark_as_paid(order_id):
        order = Order.objects.get(id=order_id)
        order.payment_status = True
        order.save()
        return order
    
    @staticmethod
    def apply_discount(order_id, discount_amount):
        order = Order.objects.get(id=order_id)
        order.set_discount_amount(Decimal(str(discount_amount)))
        return order
    
    @staticmethod
    def set_shipping_fee(order_id, shipping_fee):
        order = Order.objects.get(id=order_id)
        order.set_shipping_fee(Decimal(str(shipping_fee)))
        return order
