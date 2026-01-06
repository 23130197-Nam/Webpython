# from django.urls import path
# from .views import (ProductListAPIView, ProductDetailAPIView, ProductReviewAPIView, view_product_detail_page
# )

# app_name = 'products'  # Đặt tên app để dễ gọi ngược (reverse)

# urlpatterns = [
#     # 1. API Danh sách & Bộ lọc
#     # URL: /api/products/
#     # URL: /api/products/?q=thit&min_price=50000
#     path('', ProductListAPIView.as_view(), name='product-list'),

#     # 2. API Chi tiết sản phẩm
#     # URL: /api/products/5/
#     path('<int:pk>/', ProductDetailAPIView.as_view(), name='product-detail'),

#     # 3. API Xem & Viết đánh giá
#     # URL: /api/products/5/reviews/
#     path('<int:pk>/reviews/', ProductReviewAPIView.as_view(), name='product-reviews'),
#     # THÊM DÒNG NÀY: Đường dẫn dành riêng cho việc hiển thị HTML
#     path('view/<int:pk>/', view_product_detail_page, name='chi_tiet_page'),
# ]
from django.urls import path
from . import views


app_name = 'products'

urlpatterns = [
    # 1. API lấy danh sách (Dùng cho Trang chủ, Search)
    # URL thực tế: /products/api/list/
    path('list/', views.ProductListAPIView.as_view(), name='api-product-list'),

    # 2. API chi tiết sản phẩm
    # URL thực tế: /products/api/detail/1/
    path('detail/<int:pk>/', views.ProductPageDetailAPIView.as_view(), name='api-product-detail'),

    # 3. API Review (Get list & Post new)
    # URL thực tế: /products/api/detail/1/reviews/
    path('detail/<int:pk>/reviews/', views.ProductReviewAPIView.as_view(), name='api-product-reviews'),

    # 4. View Render HTML (Trang chi tiết truyền thống - nếu còn dùng)
    path('detaill/<int:pk>/', views.view_product_detail_page, name='page-product-detail'),
    
]