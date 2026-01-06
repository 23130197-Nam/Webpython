from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.request import Request
from .services import PaymentService
from .serializers import PaymentRequestSerializer, PaymentSerializer
from django.shortcuts import render

def payment_page(request):
    return render(request, "Pay.html")

payment_service = PaymentService() 

class CreatePaymentAPIView(APIView):
    def post(self, request:Request):
        serializer = PaymentRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        validated_data = serializer.validated_data
        try:
            new_payment = payment_service.create_payment(
                method=validated_data['method'],
                order_id=validated_data['order_id'],
                amount=validated_data['amount'],
                currency=validated_data['currency']
            )
            response_data = PaymentSerializer(new_payment).data
            return Response({
                "message": "Payment initiated successfully",
                "payment": response_data
            }, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Thêm một View để xem chi tiết Payment (GET /api/payments/{id}/)
# class PaymentDetailView(generics.RetrieveAPIView):
#     queryset = Payment.objects.all()
#     serializer_class = PaymentSerializer
