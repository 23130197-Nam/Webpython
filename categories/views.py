from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from categories.serializers import CategorySerializer
from categories.services import CategoryService
from products.services import ProductService
from products.serializers import ProductListSerializer

# --- NHÓM 1: DANH SÁCH (Dùng để vẽ các hình tròn trên trang chủ) ---
class CategoryListAPIView(APIView):
    #lấy 1 cái list danh mục
    def get(self, request):
        # Vì là 1 cấp, nên list() chính là root()
        categories = CategoryService.list() 
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)
    

# --- NHÓM 2: CHI TIẾT (Lấy tên, banner) ---
class CategoryDetailAPIView(APIView):
    def get(self, request, pk):
        try:
            category = CategoryService.get_by_id(pk)
            return Response(CategorySerializer(category).data)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)


# --- NHÓM 3: SẢN PHẨM (Quan trọng nhất) ---
class CategoryProductsAPIView(APIView):

    def get(self, request, pk):
        try:
            CategoryService.get_by_id(pk) # Check tồn tại
            products = ProductService.by_category(pk)
            return Response(ProductListSerializer(products, many=True).data)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)