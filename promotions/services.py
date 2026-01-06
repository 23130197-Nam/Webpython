from abc import ABC, abstractmethod
from typing import Dict, Type, List
from django.utils import timezone
from .models import PercentageDiscount, BuyXGetYDiscount, PromotionBase, PercentageDiscountProduct
from django.core.exceptions import ObjectDoesNotExist
from decimal import Decimal
from carts.models import CartItem
from products.models import Product

class DiscountStrategy(ABC):
    @abstractmethod
    def calculate_discount(self, total_amount: Decimal, promotion_object: object, cart_items: List[CartItem] = None) -> Decimal:
        pass

class PercentageDiscountStrategy(DiscountStrategy):
    def calculate_discount(self, total_amount: Decimal, promotion_object: PercentageDiscount, cart_items: List[CartItem] = None) -> Decimal:
        rate = promotion_object.value / Decimal('100.0')
        min_amount = promotion_object.min_amount
        if total_amount >= min_amount:
            discount = total_amount * rate
            return discount
        return Decimal('0.00')

class BuyXGetYDiscountStrategy(DiscountStrategy):
    # Phương thức tính giảm giá gồm các thuộc tính:
    # - total_amount: tổng tiền đơn hàng.
    # - promotion_object: đối tượng dưới DB.
    # - order_items: danh sách các sản phẩm.
    def calculate_discount(self, total_amount: Decimal, promotion_object: BuyXGetYDiscount, cart_items: List[CartItem]) -> Decimal:
        X = promotion_object.buy_quantity
        Y = promotion_object.get_quantity
        product_sku = promotion_object.product_sku
        total_bought = 0
        product_price = Decimal('0.00')
        for item in cart_items:
            if item.product.sku == product_sku: 
                total_bought = item.quantity
                product_price = item.product.price
                break
        if total_bought < X or X == 0:
            return Decimal('0.00')
        # Tính toán số lần khuyến mãi được áp dụng
        times_applied = total_bought // X
        # Tính số lượng sản phẩm được free.
        free_quantity = times_applied * Y
        discount = free_quantity * product_price
        return min(discount, total_amount)

class DiscountFactory:
    STRATEGIES: Dict[str, Type[DiscountStrategy]] = {
        'PERCENT': PercentageDiscountStrategy,
        'BUY_X_GET_Y': BuyXGetYDiscountStrategy,
    }
    @staticmethod
    def get_strategy(discount_type: str) -> DiscountStrategy:
        normalized_type = discount_type.upper()
        if normalized_type not in DiscountFactory.STRATEGIES:
            raise ValueError(f"Unsupported discount type: {discount_type}")
        StrategyClass = DiscountFactory.STRATEGIES[normalized_type]
        return StrategyClass()

class PromotionService:
    @staticmethod
    def get_promotion_object( code: str) -> object:
        try:
            base_promo = PromotionBase.objects.get(code=code, is_active=True,valid_from__lte=timezone.now(),valid_to__gte=timezone.now())
            if base_promo.discount_type == 'PERCENT':
                return PercentageDiscount.objects.get(promotionbase_ptr_id=base_promo.pk) 
            elif base_promo.discount_type == 'BUY_X_GET_Y':
                return BuyXGetYDiscount.objects.get(promotionbase_ptr_id=base_promo.pk)
        except ObjectDoesNotExist:
            raise ValueError(f"Promotion code '{code}' not found, inactive, or expired.")
        except Exception as e:
            raise ValueError(f"Invalid promotion structure for code '{code}'. Error: {e}")
    @staticmethod
    def apply_promotion(code: str, total_amount: float, cart_items: List[CartItem]) -> dict:
        if total_amount <= 0:
            return {"discount_amount": Decimal('0.00'), "final_amount": Decimal('0.00'), "promotion": None}
        total_amount_decimal = Decimal(str(total_amount))
        promotion_object: PromotionBase = PromotionService.get_promotion_object(code)
        strategy = DiscountFactory.get_strategy(promotion_object.discount_type)
        discount_amount = strategy.calculate_discount(total_amount_decimal, promotion_object, cart_items)
        final_amount = total_amount_decimal - discount_amount
        return {
            "discount_amount": discount_amount.quantize(Decimal('0.01')),
            "final_amount": final_amount.quantize(Decimal('0.01')),
            "promotion": promotion_object 
        }
    """ Phương thức get_available_promotions phục vụ cho order"""
    @staticmethod
    def get_available_promotions(user, current_subtotal: Decimal) -> List[dict]:
        now = timezone.now()
        available_promos = []

        promos = PromotionBase.objects.filter(is_active=True,valid_from__lte=now,valid_to__gte=now)
        for p in promos:
            try:
                detail_promo = PromotionService.get_promotion_object(p.code)
                min_req = getattr(detail_promo, 'min_amount', Decimal('0.00'))
                
                if current_subtotal >= min_req:
                    available_promos.append({
                        "code": p.code,
                        "description": p.description or f"Giảm giá loại {p.discount_type}",
                        "discount_type": p.discount_type,
                        "value": getattr(detail_promo, 'value', 0),
                        "min_amount": min_req
                    })
            except:
                continue

        return available_promos
    @staticmethod
    def calculate_final_total(subtotal: Decimal, voucher_code: str, cart_items: List[CartItem]) -> Decimal:
        if not voucher_code:
            return subtotal
        try:
            result = PromotionService.apply_promotion(voucher_code, float(subtotal), cart_items)
            return result['final_amount']
        except ValueError:
            return subtotal









class ProductPromotionService:
    @staticmethod
    def get_active_promotion(product):
        now = timezone.now()
        percent = PercentageDiscountProduct.objects.filter(product=product,  is_active=True, valid_from__lte=now,  valid_to__gte=now).first()
        if percent:
            return {
                "type": "PERCENT",
                "value": percent.value,
                "min_amount": percent.min_amount,
                "promotion": percent,
            }

        buy_x = BuyXGetYDiscount.objects.filter(
            product=product,
            is_active=True,
            valid_from__lte=now,
            valid_to__gte=now
        ).first()

        if buy_x:
            return {
                "type": "BUY_X_GET_Y",
                "buy": buy_x.buy_quantity,
                "get": buy_x.get_quantity,
                "promotion": buy_x,
            }

        return None
    

def get_product_discount_price(product: Product) -> Decimal:
    now = timezone.now()

    promo = PercentageDiscountProduct.objects.filter(product=product,is_active=True, valid_from__lte=now, valid_to__gte=now).first()
    if not promo:
        return product.price

    # giảm theo %
    discount_rate = promo.value / Decimal('100')
    discounted_price = product.price * (Decimal('1') - discount_rate)
    return discounted_price.quantize(Decimal('0.01'))

