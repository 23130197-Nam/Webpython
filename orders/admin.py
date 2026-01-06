from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['line_total', 'created_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'subtotal', 'total', 'payment_status', 
                    'fulfillment_status', 'created_at']
    list_filter = ['payment_status', 'fulfillment_status', 'created_at']
    search_fields = ['id', 'user_id']
    ordering = ['-created_at']
    readonly_fields = ['subtotal', 'total', 'created_at', 'updated_at']
    list_editable = ['payment_status', 'fulfillment_status']
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'name', 'quantity', 'unit_price', 'line_total']
    search_fields = ['order__id', 'name', 'sku']
    ordering = ['-created_at']
    readonly_fields = ['line_total', 'created_at']
