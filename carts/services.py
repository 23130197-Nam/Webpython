from .models import Cart, CartItem
from products.models import Product
from decimal import Decimal


class CartService:
    """Service layer for Cart business logic"""
    
    @staticmethod
    def create_cart(cart_id, user_id):
        """Create a new cart"""
        cart = Cart(id=cart_id, user_id=str(user_id))
        cart.save()
        return cart
    
    @staticmethod
    def get_cart(cart_id):
        """Get cart by ID"""
        try:
            return Cart.objects.get(id=cart_id)
        except Cart.DoesNotExist:
            return None
    
    @staticmethod
    def get_cart_by_user(user_id):
        """Get cart by user ID"""
        return Cart.get_cart_by_user(user_id)
    
    @staticmethod
    def add_item_to_cart(cart_id, product_id, quantity, attributes=None):
        """Add item to cart or update quantity if exists"""
        cart = Cart.objects.get(id=cart_id)
        product = Product.objects.get(id=product_id)
        
        # Check if item already exists
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={
                'quantity': quantity,
                'unit_price': product.price,
                'attributes': attributes or {}
            }
        )
        
        if not created:
            # Update quantity if item already exists
            cart_item.quantity += int(quantity)
            cart_item.save()
        
        return cart_item
    
    @staticmethod
    def remove_item_from_cart(cart_id, product_id):
        """Remove item from cart"""
        CartItem.objects.filter(cart_id=cart_id, product_id=product_id).delete()
    
    @staticmethod
    def update_item_quantity(cart_id, product_id, quantity):
        """Update item quantity"""
        if quantity <= 0:
            CartService.remove_item_from_cart(cart_id, product_id)
        else:
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            cart_item.quantity = quantity
            cart_item.save()
    
    @staticmethod
    def clear_cart(cart_id):
        """Clear all items from cart"""
        cart = Cart.objects.get(id=cart_id)
        cart.items.all().delete()
        cart.recalculate_totals()
    
    @staticmethod
    def apply_discount(cart_id, discount_amount):
        """Apply discount to cart"""
        cart = Cart.objects.get(id=cart_id)
        cart.discount = Decimal(str(discount_amount))
        cart.recalculate_totals()
        return cart
    
    @staticmethod
    def set_shipping_fee(cart_id, shipping_fee):
        """Set shipping fee for cart"""
        cart = Cart.objects.get(id=cart_id)
        cart.shipping_fee = Decimal(str(shipping_fee))
        cart.recalculate_totals()
        return cart
