from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import PercentageDiscount, BuyXGetYDiscount, PromotionBase
from .serializers import (PercentageDiscountSerializer, BuyXGetYDiscountSerializer, PromotionApplyInputSerializer, DiscountResultSerializer)
from .services import PromotionService
from carts.models import Product, Cart, CartItem 
from django.utils import timezone

class PercentageDiscountViewSet(viewsets.ModelViewSet):
    queryset = PercentageDiscount.objects.all()
    serializer_class = PercentageDiscountSerializer

class BuyXGetYDiscountViewSet(viewsets.ModelViewSet):
    queryset = BuyXGetYDiscount.objects.all()
    serializer_class = BuyXGetYDiscountSerializer
# áp đụng mã giảm giá
class ApplyPromotionAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = PromotionApplyInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        code = data['code']
        total_amount = data['total_amount']
        items_data = data['cart_items_data']
        # Khi có cart thao tác thì load dữ liệu từ DB lên không tạo mô phổng như vầy nửa.
        mock_cart_items = []
        for item_data in items_data:
            mock_product = Product(sku=item_data['product_sku'], price=item_data['price'])
            mock_item = CartItem(product=mock_product, quantity=item_data['quantity'])
            mock_cart_items.append(mock_item)

        service = PromotionService()
        try:
            result = service.apply_promotion(code=code, total_amount=float(total_amount), cart_items=mock_cart_items)
            response_serializer = DiscountResultSerializer(result)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Internal Server Error: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# thêm danh sách các giảm giá
class PromotionAvailableAPIView(APIView):
    def get(self, request):
        now = timezone.now()

        promotions = PromotionBase.objects.filter(
            is_active=True,
            valid_from__lte=now,
            valid_to__gte=now
        )

        data = []

        for promo in promotions:
            item = {
                "code": promo.code,
                "discount_type": promo.discount_type,
                "description": promo.description,
            }

            if promo.discount_type == "PERCENT":
                percent = PercentageDiscount.objects.get(
                    promotionbase_ptr_id=promo.id
                )
                item["value"] = percent.value
                item["min_amount"] = percent.min_amount

            elif promo.discount_type == "BUY_X_GET_Y":
                buyx = BuyXGetYDiscount.objects.get(
                    promotionbase_ptr_id=promo.id
                )
                item["buy"] = buyx.buy_quantity
                item["get"] = buyx.get_quantity
                item["product_sku"] = buyx.product_sku

            data.append(item)

        return Response(data)