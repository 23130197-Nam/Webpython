from django.contrib import admin
from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    # list_display = ['id', 'name', 'parent_category', 'is_active', 'sort_order']
    list_display = ['id', 'name', 'is_active', 'sort_order']
    # list_filter = ['is_active', 'parent_category']
    search_fields = ['name', 'description']
    ordering = ['sort_order', 'name']
    list_editable = ['sort_order', 'is_active']
