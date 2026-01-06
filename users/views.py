from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import UserSerializer, AddressSerializer
from .services import AuthorService, UserService
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken

# 1. API Đăng Ký
class RegisterView(APIView):
   permission_classes = [permissions.AllowAny] # ai cxung đky được
    # (Hứng hành động POST từ App)
   def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            # nếu đúng lọc xong lấy dữ liệu đã lọc
            clean_data = serializer.validated_data
            user_instance = AuthorService.register_user(clean_data)
            # đóng kết quả, Ta phải dùng Serializer biến nó lại thành JSON để trả khách.
            output_serializer = UserSerializer(user_instance)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# --- 2. API PROFILE (UserProfileView) ---
class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated] # Phải đăng nhập mới vào được
    # HÀM GET: Để xem thông tin của chính mình
    def get(self, request):
        current_user_id = request.user.id
        user_obj = UserService.get_user_by_id(current_user_id)
        if user_obj is None:
            return Response({"error": "Không tìm thấy user"}, status=404)
        serializer = UserSerializer(user_obj)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

    # HÀM PUT: Để sửa thông tin
    def put(self, request):
        current_user = request.user
        serializer = UserSerializer(current_user, data=request.data, partial=True) # partial=True nghĩa là: Chỉ sửa những cái gửi lên
        if serializer.is_valid():
            clean_data = serializer.validated_data
            updated_user = UserService.update_user_info(current_user, clean_data) # dữ liệu hợp lệ gọi dòng này
            
            # B5: Đóng gói kết quả mới để trả về
            output_serializer = UserSerializer(updated_user)
            return Response(output_serializer.data, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 3. API ĐỊA CHỈ (UserAddressView) 
class UserAddressView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        list_addresses = UserService.get_user_addresses(request.user)     
        # B2: Đóng gói danh sách thành JSON
        # LƯU Ý: Vì là danh sách nhiều cái, phải có many=True
        serializer = AddressSerializer(list_addresses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # HÀM POST: Thêm địa chỉ mới
    def post(self, request):
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            clean_data = serializer.validated_data
            new_address = UserService.add_address_to_user(request.user, clean_data)
    
            output_serializer = AddressSerializer(new_address)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#4 .API Đăng nhập
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        
        # 1. Xác thực user
        user = AuthorService.login_user(username, password)
        
        if user:
            # 2. Tạo bộ JWT Token (Access + Refresh)
            refresh = RefreshToken.for_user(user)
            
            return Response({
                "access_token": str(refresh.access_token), # Token dùng để gọi API
                "refresh_token": str(refresh),             # Token dùng để lấy lại access mới
                "user_id": user.pk,
                "username": user.username,
                "email": user.email,
                "role": "customer" # Ví dụ thêm role nếu cần phân quyền
            }, status=status.HTTP_200_OK)
        
        return Response({"error": "Tài khoản hoặc mật khẩu không đúng"}, status=status.HTTP_401_UNAUTHORIZED)

def getProfile(request):
    return render(request, "users/profile.html" )
def getTheoDoi(request):
    return render(request, "users/theodoidonhang.html" )
def view_cart(request):
    return render(request, 'carts/cart1.html')
def getTrangChu(request):
    return render(request, "users/index.html")
def getLogin(request):
    return render(request, "users/Login.html")

    