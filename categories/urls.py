from django.urls import path
from categories import views

urlpatterns = [
    # 1. Danh sách danh mục (Để vẽ hình tròn trang chủ)
    # URL: /api/categories/
    path('categories/', views.CategoryListAPIView.as_view(), name='category-list'),

    # 2. Chi tiết danh mục (Để lấy tên, banner khi vào trang danh mục)
    # URL: /api/categories/5/
    path('categories/<int:pk>/', views.CategoryDetailAPIView.as_view(), name='category-detail'),

    # 3. Sản phẩm trong danh mục (Để hiện list sản phẩm bên dưới)
    # URL: /api/categories/5/products/
    path('categories/<int:pk>/products/', views.CategoryProductsAPIView.as_view(), name='category-products'),
]