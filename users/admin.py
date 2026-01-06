from django.contrib import admin
from .models import User, Address
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# Đăng ký model User
@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    # 1. Sắp xếp lại các ô nhập liệu bằng fieldsets
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Thông tin cá nhân', {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        ('Quyền hạn', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Lịch sử', {'fields': ('last_login', 'date_joined')}),
    )
    
    # 2. Hiển thị cột đẹp mắt ở trang danh sách
    list_display = ('username', 'email', 'phone', 'is_staff')
    search_fields = ('username', 'email', 'phone')

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'street', 'ward', 'province')