from django.contrib.auth import authenticate
from .models import User, Address

# --- 1. USER SERVICE ---
class UserService:

    @staticmethod
    def create_user(data):
        password = data.pop('password')
        # cls.userDao.create(...) tương đương User.objects.create(...)
        # Nhưng ở đây cần hash password nên ta dùng cách thủ công một chút
        user = User(**data)
        user.set_password(password)
        user.save()
        return user

    @staticmethod
    def get_user_by_id(user_id):
        try:
            # Dùng userDao (User.objects) để tìm
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @staticmethod
    def update_user_info(user, update_data):
        # 'user' ở đây chính là thuộc tính '-user: User' trong sơ đồ
        # nhưng được truyền vào dưới dạng tham số
        if 'password' in update_data:
            new_password = update_data.pop('password')
            
            # CHỖ NÀY LÀ CẦN THIẾT: Phải gọi set_password để mã hóa!
            user.set_password(new_password)
        for key, value in update_data.items():
            setattr(user, key, value)
        user.save() # Lưu lại thay đổi (Update)
        return user
    
    @staticmethod
    def get_user_addresses( user):
        # Dùng addressDao để lọc địa chỉ
        return Address.objects.filter(user=user)

    @staticmethod
    def add_address_to_user(user, address_data):
        # Dùng addressDao để tạo mới
        return Address.objects.create(user=user, **address_data)


# --- 2. AUTHOR SERVICE ---
class AuthorService:
    # AuthorService gọi sang UserService (đúng sơ đồ)
    
    @staticmethod
    def register_user(validated_data):
        return UserService.create_user(validated_data)

    @staticmethod
    def login_user(username, password):
        return authenticate(username=username, password=password)