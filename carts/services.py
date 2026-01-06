from .models import Cart, CartItem
from products.models import Product
from decimal import Decimal
from django.db import transaction 
from django.shortcuts import get_object_or_404
from django.utils import timezone
from promotions.services import get_product_discount_price
from orders.models import OrderItem, Order
from users.models import Address

class CartService:    
    # là nó thông báo đây là hàm thuộc class nhưng mà nó không lấy toàn bộ thuộc tính của class
    # tạo cart thông qua user
    @staticmethod
    def create_cart(user):
        return Cart.objects.get_or_create(id=str(user.id))[0]
    
    # lấy các sản phẩm ở cart để hiển thị giỏ hàng
    @staticmethod
    def get_cart_items(cart: Cart):
        return (CartItem.objects.filter(cart=cart).select_related('product').order_by('-created_at'))
    
    # lấy các sản phẩm được chọn đoạn này là làm pay
    @staticmethod
    def get_selected_items(cart: Cart):
        return (CartItem.objects.filter(cart=cart, is_select=True).select_related('product'))
    
    # thêm sản phẩm
    @staticmethod
    @transaction.atomic
    def add_item_to_cart(cart: Cart, product_id: int, quantity: int = 1):
        # B1: Lấy Product
        product = get_object_or_404(Product, id=product_id, is_active=True)
        # B2: check Promotion
        discounted_price = get_product_discount_price(product)     
        # B3: Check quantity.
        if quantity <= 0:
            raise ValueError("Số lượng không hợp lệ")
        # B4: Tạo CartItem
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={
                "quantity": 0,
                "is_select": True,
                "unit_price": discounted_price,
            }
        )
        # B5: cập nhật lại quantity
        item.unit_price = discounted_price
        new_quantity = item.quantity + quantity
        item.quantity = new_quantity
        item.save()
        print("PRODUCT PRICE:", product.price)
        ~print("DISCOUNTED PRICE:", discounted_price)

        # B6: Tính lại tổng
        CartService.recalculate_totals(cart)
        return item


    # chọn sản phẩm
    @staticmethod
    @transaction.atomic
    def set_item_select(cart: Cart, product_id, is_select: bool):
        item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
        item.is_select = is_select
        item.save(update_fields=['is_select', 'updated_at'])

        CartService.recalculate_totals(cart)
        return item  
    
    # chọn toàn bộ sản phẩm
    @staticmethod
    @transaction.atomic
    def set_select_all(cart: Cart, is_select: bool):
        cart.items.exclude(unit_price=0).update(is_select=is_select)
        CartService.recalculate_totals(cart)

    # tính tổng các sản phẩm được chọn
    @staticmethod
    def recalculate_totals( cart: Cart):
        subtotal = Decimal('0')

        for item in CartService.get_selected_items(cart):
            # discounted_unit_price = get_product_discount_price(item.product)
            # subtotal += discounted_unit_price * item.quantity

            subtotal += item.unit_price * item.quantity

        cart.subtotal = subtotal
        cart.save(update_fields=['subtotal', 'updated_at'])


    # lấy giỏ hàng 
    @staticmethod
    def get_cart(user):
        return Cart.objects.filter(id=str(user.id)).first()

    # xóa sản phẩm trong cart
    @staticmethod
    @transaction.atomic
    def remove_item_from_cart(cart: Cart, product_id):
        CartItem.objects.filter(cart=cart, product_id=product_id).delete()
        CartService.recalculate_totals(cart)


    # xóa toàn bộ sản phẩm
    @staticmethod
    @transaction.atomic
    def clear_cart(cart: Cart):
        cart.items.all().delete()
        cart.subtotal = Decimal('0')
        cart.save(update_fields=['subtotal', 'updated_at'])

    # cập nhật số lượng sản phẩm
    @staticmethod
    @transaction.atomic
    def update_item_quantity(cart: Cart, product_id: Product, quantity):
        if quantity <= 0:
            return CartService.remove_item_from_cart(cart, product_id)

        item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
        if item.unit_price == 0:
            return item

        if quantity > item.product.stock_qty:
            raise ValueError("Vượt quá tồn kho")

        item.quantity = quantity
        item.save(update_fields=['quantity', 'updated_at'])

        CartService.recalculate_totals(cart)
        return item
    

    """ Phương thức get_checkout_items phục vụ cho order"""
    @staticmethod
    def get_checkout_items(user):
        cart = CartService.get_cart(user)
        if not cart:
            return {"items": [], "subtotal": Decimal('0')}
            
        selected_items = CartService.get_selected_items(cart)
        
        items_data = []
        subtotal = Decimal('0')
        for item in selected_items:
            product_images = item.product.images 
            first_image = product_images[0] if product_images and len(product_images) > 0 else ""
            subtotal += item.unit_price * item.quantity
            
            items_data.append({
                "product_id": item.product.id,
                "product_name": item.product.name,
                # Cần chỉnh sửa ảnh
                "image": first_image,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
            })
            
        return {
            "items": items_data,
            "subtotal": subtotal
        }
    # Phương thức này thực hiện cho order
    @staticmethod
    @transaction.atomic
    def convert_cart_to_order(user, order_instance: Order, address_id=None):
        if address_id:
            try:
                addr_obj = Address.objects.get(id=address_id, user=user)
                order_instance.shipping_address = addr_obj
                order_instance.save(update_fields=['shipping_address'])
            except Address.DoesNotExist:
                pass

        cart = CartService.get_cart(user)
        selected_items = CartService.get_selected_items(cart)

        if not selected_items.exists():
            raise ValueError("Không có sản phẩm nào được chọn để thanh toán.")

        order_items = []
        current_subtotal = Decimal('0')
        for cart_item in selected_items:
            product = cart_item.product

            if product.stock_qty < cart_item.quantity:
                raise ValueError(f"Sản phẩm {product.name} không đủ tồn kho.")

            order_items.append(
                OrderItem(
                    order=order_instance,
                    product=product,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.unit_price  
                )
            )
            current_subtotal += cart_item.unit_price * cart_item.quantity
            product.stock_qty -= cart_item.quantity
            product.save(update_fields=['stock_qty'])

        OrderItem.objects.bulk_create(order_items)

        order_instance.subtotal = current_subtotal
        order_instance.save()

        selected_items.delete()
        CartService.recalculate_totals(cart)

        return order_items
