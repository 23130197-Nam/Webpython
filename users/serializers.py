from rest_framework import serializers
from .models import User, Address

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'street', 'ward', 'province']

class UserSerializer(serializers.ModelSerializer):
    #Nhúng danh sách Address vào trong User đúng như sơ đồ vẽ
    addresses = AddressSerializer(many=True, read_only=True) # app k đc ném vào sever
    password = serializers.CharField(write_only=True) #Giấu mật khẩu sever k đc ném ra 

    class Meta:
        model = User
        # Liệt kê đúng các trường trong sơ đồ
        fields = ['id', 'username', 'phone','email', 'password',  'addresses']
    
 
    