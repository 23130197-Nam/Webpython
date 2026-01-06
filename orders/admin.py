from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    # Hiển thị các trường theo model OrderItem của bạn
    fields = ['product', 'sku', 'name', 'quantity', 'unit_price', 'get_line_total']
    readonly_fields = ['get_line_total']

    # Tính toán line_total hiển thị tạm trên admin vì model OrderItem không có trường này
    def get_line_total(self, obj):
        if obj.quantity and obj.unit_price:
            return obj.quantity * obj.unit_price
        return 0
    get_line_total.short_description = "Thành tiền"

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Khớp list_display với các trường trong Model Order
    list_display = [
        'id', 
        'user_id', 
        'subtotal', 
        'discount', 
        'shipping_fee', 
        'total', 
        'payment_status', 
        'fulfillment_status', 
        'payment_method',
        'created_at'
    ]
    
    list_filter = ['payment_status', 'fulfillment_status', 'payment_method', 'created_at']
    search_fields = ['id', 'user_id', 'payment_method']
    ordering = ['-created_at']
    
    # readonly_fields để đảm bảo các giá trị tính toán từ Service không bị sửa thủ công sai lệch
    readonly_fields = ['subtotal', 'total', 'created_at', 'updated_at']
    
    # Cho phép sửa nhanh trạng thái thanh toán và vận chuyển ngay tại danh sách
    list_editable = ['payment_status', 'fulfillment_status']
    
    inlines = [OrderItemInline]

    # Tổ chức lại giao diện chi tiết đơn hàng cho khoa học
    fieldsets = (
        ('Thông tin chung', {
            'fields': ('user_id', 'payment_method', 'created_at', 'updated_at')
        }),
        ('Địa chỉ', {
            'fields': ('shipping_address', 'billing_address')
        }),
        ('Trạng thái', {
            'fields': ('payment_status', 'fulfillment_status')
        }),
        ('Giá trị đơn hàng', {
            'fields': ('subtotal', 'discount', 'shipping_fee', 'total')
        }),
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    # Khớp list_display với các trường trong Model OrderItem
    list_display = ['id', 'order', 'product', 'sku', 'name', 'quantity', 'unit_price', 'created_at']
    search_fields = ['name', 'sku', 'order__id']
    readonly_fields = ['created_at']