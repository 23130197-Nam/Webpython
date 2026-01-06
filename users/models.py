from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # AbstractUser có sẵn: username, password (passwd), email.
    phone = models.CharField(max_length=20, null=True)
    def __str__(self):
        return self.username
    
#2 Class Address
class Address(models.Model):
    # Sơ đồ: User chứa List<Address>
    # Trong dtb, ta làm ngược lại: Address trỏ về User (ForeignKey)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    
    street = models.CharField(max_length=255) #đường/số nhà
    ward = models.CharField(max_length=100) #phường/xã
    province = models.CharField(max_length=100) #tỉnh/tp
    def __str__(self):
        return f"{self.street}, {self.ward}, {self.province}"
    
