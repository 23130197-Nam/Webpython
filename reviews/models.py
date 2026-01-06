from django.db import models
from users.models import User
from products.models import Product

class Review(models.Model):
    # Django tự động tạo id (BigAutoId) tối ưu cho Indexing
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews') # nên để như này vì nếu để product chứa list<review> thì nó k tạo dc xóa dtb
    #nếu mà nhét 1 cái list review vào product thì nó nặng máy, nên nó chậm.
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # Thêm validation cơ bản
    title = models.CharField(max_length=200) #
    content = models.TextField() 
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False) #cái này để tránh spam review, việc không đặt id k nên đặt cơ chế của Django mạnh hơn

    class Meta:
        # Index giúp tìm kiếm theo product và user nhanh hơn
        indexes = [
            models.Index(fields=['product', 'rating']),
            models.Index(fields=['user']),
        ]

    def __str__(self) -> str:
        return f"{self.rating}/5 - {self.product.name}"

#Class để train AI đeck quantam
class ReviewVote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='votes')
    is_helpful = models.BooleanField() #AI
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'review']