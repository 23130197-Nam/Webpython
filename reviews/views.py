from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from products.models import Product

from .services import ReviewService, ReviewVoteService
from .serializers import ReviewSerializer, ReviewVoteSerializer

class ProductReviewListAPI(APIView):
    """
    GET: Lấy danh sách đánh giá của 1 sản phẩm (kèm bộ lọc)
    POST: Tạo đánh giá mới
    """
    # Chỉ cho phép User đã đăng nhập mới được POST, ai cũng được GET
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, product_id):
        # 1. Lấy tham số từ URL Query
        rating = request.query_params.get('rating')
        is_verified = request.query_params.get('is_verified')
        
        # 2. Gọi Service để lấy dữ liệu (đã tối ưu query)
        reviews = ReviewService.filter_reviews(
            product_id=product_id, 
            rating=rating, 
            is_verified=is_verified
        )
        
        # 3. Serialize dữ liệu ra JSON
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        
        # 1. Validate dữ liệu đầu vào (Rating, Title, Content)
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            # 2. Gọi Service để xử lý logic tạo mới
            try:
                review = ReviewService.create_review(
                    user=request.user,
                    product=product,
                    rating=serializer.validated_data['rating'],
                    title=serializer.validated_data['title'],
                    content=serializer.validated_data['content']
                )
                return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductReviewStatsAPI(APIView):
    """
    GET: Lấy thống kê sao và phân phối điểm số
    """
    def get(self, request, product_id):
        # Gọi Service tính toán Aggregation
        stats = ReviewService.get_product_stats(product_id)
        return Response(stats, status=status.HTTP_200_OK)


class ReviewVoteAPI(APIView):
    """
    POST: Vote hữu ích cho một đánh giá
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, review_id):
        serializer = ReviewVoteSerializer(data=request.data)
        if serializer.is_valid():
            ReviewVoteService.vote_review(
                user=request.user,
                review_id=review_id,
                is_helpful=serializer.validated_data['is_helpful']
            )
            return Response({"message": "Voted successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



