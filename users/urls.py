from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# --- CHÚ Ý DÒNG NÀY ---
# Phải import đúng tên class MỚI bạn vừa viết bên views.py
from .views import RegisterView, UserProfileView, UserAddressView,  getTheoDoi, getProfile, view_cart, getTrangChu, LoginView, getLogin;


urlpatterns = [
    # API Đăng ký
    path('register/', RegisterView.as_view(), name='register'),
    
    # API Đăng nhập (Lấy Token)
    path('login/', LoginView.as_view(), name='login'),
    
    # API Lấy lại Token mới
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # --- NHÓM 2: CHỨC NĂNG NGƯỜI DÙNG (USER) ---
    # 4. Xem & Sửa Profile (GET / PUT)
    # Vì UserProfileView xử lý cả 2 hàm get và put trên cùng 1 url này
    path('profile/', UserProfileView.as_view(), name='profile'),

    # 5. Quản lý địa chỉ (GET / POST)
    # Vì UserAddressView xử lý cả danh sách và tạo mới trên cùng 1 url này
    path('addresses/', UserAddressView.as_view(), name='addresses'),
    
    path('theo-doi/',getTheoDoi , name='theo_doi'),
    path('profile_t/',getProfile , name='profile_t'),
    path('carts/', view_cart, name='cart_page'),
    path('trang-chu/', getTrangChu, name='index_page'),
    path('dang-nhap/', getLogin, name='page_login'),
    path('api/users/profile/', UserProfileView.as_view()),
    path('api/users/addresses/', UserAddressView.as_view()),

]
