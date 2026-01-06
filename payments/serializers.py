from rest_framework import serializers
from .models import Payment

class PaymentRequestSerializer(serializers.Serializer):
    order_id = serializers.CharField(max_length=100, help_text="Mã ID đơn hàng liên quan")
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, help_text="Số tiền giao dịch")
    currency = serializers.CharField(max_length=3, help_text="Đơn vị tiền tệ (ví dụ: VND)")
    method = serializers.CharField(max_length=50, help_text="Phương thức thanh toán (ví dụ: VNPAY, BANK_TRANSFER)")

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'