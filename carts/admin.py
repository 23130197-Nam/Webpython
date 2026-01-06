from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['line_total']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'subtotal', 'discount', 'shipping_fee', 'total', 'created_at']
    search_fields = ['id', 'user_id']
    ordering = ['-created_at']
    readonly_fields = ['subtotal', 'total', 'created_at', 'updated_at']
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'cart', 'product', 'quantity', 'unit_price', 'line_total']
    search_fields = ['cart__id', 'product__name']
    ordering = ['-created_at']
    readonly_fields = ['line_total', 'created_at', 'updated_at']
