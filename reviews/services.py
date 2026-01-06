from django.db.models import Avg, Count, Q
from django.db import transaction
from .models import Review, ReviewVote

class ReviewService:   
    @staticmethod
    def create_review(user, product, rating, title, content):
        # Transaction đảm bảo tính toàn vẹn nếu có lỗi xảy ra
        with transaction.atomic():
            review = Review.objects.create(
                user=user,
                product=product,
                rating=rating,
                title=title,
                content=content
            )
            # 2. [QUAN TRỌNG] Gọi hàm tính toán số liệu thống kê
            # (Hàm này bạn viết bên dưới rồi, giờ tái sử dụng)
            stats = ReviewService.get_product_stats(product.id)
            # 3. Cập nhật ngược lại vào bảng Product
            # Để trang chủ load nhanh mà không cần query bảng Review
            product.rating_average = stats['average']
            product.review_count = stats['total']
            product.save(update_fields=['rating_average', 'review_count'])
            return review
    
    @staticmethod
    def get_product_stats(product_id):
        stats = Review.objects.filter(product_id=product_id).aggregate(
            average_rating=Avg('rating'),
            one_star=Count('id', filter=Q(rating=1)),
            two_star=Count('id', filter=Q(rating=2)),
            three_star=Count('id', filter=Q(rating=3)),
            four_star=Count('id', filter=Q(rating=4)),
            five_star=Count('id', filter=Q(rating=5)),
            total_reviews=Count('id')
        )
        
        # Xử lý trường hợp chưa có đánh giá nào (None -> 0)
        distribution = {
            1: stats['one_star'],
            2: stats['two_star'],
            3: stats['three_star'],
            4: stats['four_star'],
            5: stats['five_star']
        }
        
        return {
            'average': stats['average_rating'] or 0.0,
            'total': stats['total_reviews'],
            'distribution': distribution
        }
    
    @staticmethod
    def filter_reviews(product_id=None, rating=None, is_verified=None):
        queryset = Review.objects.select_related('user') # Tối ưu: Lấy luôn user để tránh N+1 query
        
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        if rating:
            queryset = queryset.filter(rating=rating)
        if is_verified is not None:
            queryset = queryset.filter(is_verified=is_verified)
            
        return queryset.order_by('-created_at')

    @staticmethod
    def verify_review(review_id):
        return Review.objects.filter(id=review_id).update(is_verified=True)


class ReviewVoteService:
    @staticmethod
    def vote_review(user, review_id, is_helpful):
        vote, created = ReviewVote.objects.update_or_create(
            user=user,
            review_id=review_id,
            defaults={'is_helpful': is_helpful}
        )
        return vote
