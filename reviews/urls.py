from django.urls import path
from .views import ProductReviewListAPI, ProductReviewStatsAPI, ReviewVoteAPI
app_name = 'reviews'
urlpatterns = [
    # Lấy list hoặc tạo review cho sản phẩm X
    path('products/<int:product_id>/reviews/', ProductReviewListAPI.as_view(), name='product-reviews'),
    
    # Lấy thống kê sao cho sản phẩm X (API riêng để frontend gọi lazy load)
    path('products/<int:product_id>/stats/', ProductReviewStatsAPI.as_view(), name='product-review-stats'),
    
    # Vote cho review cụ thể
    path('review/<int:review_id>/vote/', ReviewVoteAPI.as_view(), name='review-vote'),
]