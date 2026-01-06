from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'currency',
        'subtotal',
        'created_at',
        'updated_at',
    )

    search_fields = ('id',)
    ordering = ('-created_at',)

    readonly_fields = (
        'subtotal',
        'created_at',
        'updated_at',
    )

    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'cart',
        'product',
        'quantity',
        'unit_price',
        'created_at',
    )

    search_fields = ('cart__id', 'product__name')
    ordering = ('-created_at',)

    readonly_fields = (
        'created_at',
        'updated_at',
    )
