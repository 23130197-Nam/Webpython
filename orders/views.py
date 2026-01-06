from django.shortcuts import render
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.request import Request
from payments.services import PaymentService
from promotions.services import PromotionService
from users.services import UserService
from carts.services import CartService
from payments.models import PaymentMethod
from .models import Order
from .services import OrderService

def payment_page(request):
    return render(request, "pay.html")

class CheckOutDataView(APIView):
    def get(self, request:Request):
        user = request.user
        if not user.is_authenticated:
            return Response({"message": "Unauthorized"}, status=403)
        
        cart_data = CartService.get_checkout_items(user)
        addresses = UserService.get_user_addresses(user)
        promotions = PromotionService.get_available_promotions(user, cart_data['subtotal'])
        methods = PaymentMethod.objects.filter(is_active=True)

        return Response({
            "items": cart_data['items'],
            "subtotal": cart_data['subtotal'],
            "addresses": [
                {
                    "id": addr.id,
                    "receiver_name": addr.receiver_name,
                    "receiver_phone": addr.receiver_phone,
                    "full_address": addr.full_address,
                    "is_default": addr.is_default
                } for addr in addresses
            ],
            "promotions": promotions,
            "payment_methods": [
                {"code": m.code, "name": m.name, "icon_url": m.icon_url} for m in methods
            ]
        })

class ApplyVoucherView(APIView):
    def post(self, request: Request):
        user = request.user
        voucher_code = request.data.get('voucher_code')
        
        if not user.is_authenticated:
            return Response({"message": "Unauthorized"}, status=403)
            
        if not voucher_code:
            return Response({"success": False, "message": "Mã giảm giá không trống"}, status=400)

        try:
            cart = CartService.get_cart(user)
            if not cart:
                return Response({"success": False, "message": "Giỏ hàng trống"}, status=400)
            
            selected_items = list(CartService.get_selected_items(cart))
            if not selected_items:
                return Response({"success": False, "message": "Chưa chọn sản phẩm nào"}, status=400)

            subtotal = cart.subtotal
            
            promo_result = PromotionService.apply_promotion(
                code=voucher_code,
                total_amount=float(subtotal),
                cart_items = selected_items
            )

            return Response({
                "success": True,
                "voucher_code": voucher_code,
                "discount_amount": promo_result['discount_amount'],
                "final_total": promo_result['final_amount'],
                "description": promo_result['promotion'].description
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({"success": False, "message": str(e)}, status=400)
        except Exception as e:
            return Response({"success": False, "message": "Lỗi khi áp dụng mã giảm giá"}, status=500)


class CreateOrderView(APIView):
    def post(self, request: Request):
        user = request.user
        data = request.data
        voucher_code = data.get('voucher_code')
        
        try:
            with transaction.atomic():
                order = Order.objects.create( user_id=user.id, total=0, fulfillment_status='PENDING',payment_method=data.get('payment_method') )
                CartService.convert_cart_to_order(user=user, order_instance=order,  address_id=data.get('address_id'))
                order.refresh_from_db()
                if voucher_code:
                    promo_result = PromotionService.apply_promotion(
                        code=voucher_code, 
                        total_amount=float(order.subtotal),
                        cart_items=order.items.all()
                    )
                    order.discount = promo_result['discount_amount']
                    order.save(update_fields=['discount']) 

                OrderService.calculate_total(order)

                payment_record = PaymentService.create_payment(method=data.get('payment_method'), order_id=order.id, amount=order.total, currency="VND")
                
                payment_url = None
                if data.get('payment_method') == 'VNPAY':
                    payment_url = getattr(payment_record, 'payment_url', None)

                return Response({ "success": True, "order_id": order.id, "payment_url": payment_url
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            import traceback
            traceback.print_exc() # In lỗi chi tiết ra terminal để debug
            return Response({"success": False, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)