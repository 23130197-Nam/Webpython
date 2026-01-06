from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from products.services import ProductService
from products.serializers import ProductListSerializer, ProductDetailSerializer
from reviews.services import ReviewService
from django.shortcuts import render
from reviews.serializers import ReviewSerializer
from rest_framework.request import Request
# - API 1: DANH SÁCH TỔNG HỢP (Dùng cho Trang chủ & Trang Search) ---
class ProductListAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request: Request):
        filters = {
            'search': request.query_params.get('q'),
            'category_id': request.query_params.get('category_id'),
            'min_price': request.query_params.get('min_price'),
            'max_price': request.query_params.get('max_price'),
            'sort': request.query_params.get('sort', 'newest'), 
            'featured': request.query_params.get('featured'),    
            'limit': request.query_params.get('limit')          
        }
        products = ProductService.list(filters)
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)

# --- API 2: CHI TIẾT SẢN PHẨM (Kèm sản phẩm liên quan) ---
class ProductPageDetailAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request, pk):
        try:
            product = ProductService.get_by_id(pk)
            product_data = ProductDetailSerializer(product).data

            related_products = ProductService.related_products(pk, product.category_id)
            related_data = ProductListSerializer(related_products, many=True).data

            review_stats = ReviewService.get_product_stats(pk)

            latest_reviews = ReviewService.filter_reviews(product_id=pk)[:5]
            reviews_data = ReviewSerializer(latest_reviews, many=True).data

            full_data = {
                "product": product_data,
                "related_products": related_data,
                "reviews": {
                    "stats": review_stats,
                    "latest_list": reviews_data,
                    "total_count": product.review_count if hasattr(product, 'review_count') else len(latest_reviews)
                }
            }
            return Response(full_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
        
# --- API 3: tạo dánh giá & phân trang
class ProductReviewAPIView(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
  

    def get(self, request: Request, pk):
        try:
            offset = int(request.query_params.get('offset', 0))
            limit = int(request.query_params.get('limit', 5))
            reviews = ReviewService.filter_reviews(product_id=pk)[offset : offset + limit]
            
            serializer = ReviewSerializer(reviews, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except ValueError:
            return Response({"error": "Tham số không hợp lệ"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request: Request, pk):
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            try:
                product = ProductService.get_by_id(pk)
                review = ReviewService.create_review(
                    user=request.user,
                    product=product,
                    rating=serializer.validated_data['rating'],
                    title=serializer.validated_data.get('title', ''),
                    content=serializer.validated_data.get('content', '')
                )
                return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
def view_product_detail_page(request, pk):
    return render(request, 'products/chitietsp.html', {'product_id': pk})

