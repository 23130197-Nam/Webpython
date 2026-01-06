from django.db.models import Q
from .models import Product
from django.utils import timezone
from django.db.models import F, Case, When, IntegerField
from datetime import timedelta
# => Nổi bật là 10 sản phẩm giảm giá nhiều nhất 
# => Best Sales là 10 sản phẩm bán nhiều người mua nhất.
# => Mới cập bến lầ 10 sản phẩm có ngày tạo mới nnhất.
# => là 10 sản phẩm gấn hết hạn nhất.
class ProductService:
    # 1. HÀM LIST ĐA NĂNG (Phục vụ API 1)
    @staticmethod
    def list(filters: dict):
        queryset = Product.objects.filter(is_active=True)
        #  Tìm kiếm theo tên (Search)
        if filters.get('search'):
            query = filters.get('search')
            queryset = queryset.filter(name__icontains=query) #name sẽ là biến "__" là phép toán sắp nói đến  icontains k phân biệt hoa thường

        #  Lọc theo Danh mục (Category)
        if filters.get('category_id'):
            queryset = queryset.filter(category_id=filters.get('category_id'))

        # Lọc hàng bán chạy (Best Seller / Featured)
        if filters.get('featured') == 'true':
             queryset = queryset.filter(featured=True) 

        # Lọc theo khoảng giá (Price Range)
        if filters.get('min_price'):
            try:
                queryset = queryset.filter(price__gte=int(filters.get('min_price'))) #gte >=
            except ValueError:
                pass # Bỏ qua nếu giá không phải số
                
        if filters.get('max_price'):
            try:
                queryset = queryset.filter(price__lte=int(filters.get('max_price'))) #lte <=
            except ValueError:
                pass

        # --- SẮP XẾP (SORT) ---
        # Lấy limit sớm để dùng cho các logic bên dưới
        limit_param = filters.get('limit')
        try:
            limit_val = int(limit_param) if limit_param else None
        except ValueError:
            limit_val = None
            
        sort_by = filters.get('sort')   
        if sort_by == 'price_asc':
            queryset = queryset.order_by('price')       # Giá tăng dần
        elif sort_by == 'price_desc':
            queryset = queryset.order_by('-price')      # Giá giảm dần
        elif sort_by == 'near_expiry':
            now = timezone.now()
            twenty_days_later = now + timedelta(days=20)
            # B1: Lấy tất cả sản phẩm Active, còn kho, chưa hết hạn
            base_query = queryset.filter(
                expiry_date__gt=now,
                stock_qty__gt=0
            ).annotate(
                priority=Case(
                    When(expiry_date__lte=twenty_days_later, then=1),
                    default=2,
                    output_field=IntegerField(),
                )
            ).order_by('priority', 'expiry_date', '-created_at')
            # B2: Đếm xem có bao nhiêu sản phẩm dưới 20 ngày (Priority 1) trong RAM
            urgent_count = base_query.filter(priority=1).count()
            # B3: Quyết định số lượng hiển thị (Slice động)
            # Nếu nhóm khẩn cấp > 10 món: Lấy hết nhóm đó (urgent_count)
            # Nếu nhóm khẩn cấp <= 10 món: Lấy tối thiểu 20 món
            default_limit = limit_val if limit_val else 20
            final_limit = max(urgent_count, default_limit)
            return base_query[:final_limit]
        elif sort_by == 'best_selling':
            queryset = queryset.filter(stock_qty__gt=0).order_by('-sold', '-created_at')
            return queryset[:(limit_val if limit_val else 5)]


        elif sort_by == 'newest':
            queryset = queryset.order_by('-created_at') # Mới nhất
        else:
            queryset = queryset.order_by('-created_at') # Mặc định là mới nhất

        # --- GIỚI HẠN SỐ LƯỢNG (LIMIT) ---
        # Dùng cho các khối ở trang chủ (chỉ lấy 4 hoặc 8 cái)
        final_limit = limit_val if limit_val else 10
        
        return queryset[:final_limit]
    # 2. HÀM CHI TIẾT (Phục vụ API 2)
    @staticmethod
    def get_by_id(pk):
        # Lấy 1 sản phẩm theo ID. Nếu không thấy thì báo lỗi để View trả về 404.
        try:
            return Product.objects.get(id=pk, is_active=True)
        except Product.DoesNotExist:
            raise ValueError(f"Sản phẩm với ID {pk} không tồn tại hoặc đã bị ẩn.")

    # 3. HÀM LIÊN QUAN (Phục vụ API 2 - Phần gợi ý bên dưới)
    @staticmethod
    def related_products(current_id, category_id, limit=4):
        if not category_id:
            return []
        return Product.objects.filter(
            category_id=category_id,
            is_active=True
        ).exclude(id=current_id).order_by('?')[:limit] # Dấu '?' là random ngẫu nhiên
    
    #4 hàm lấy sản phẩm gần hết hạn
    @staticmethod
    def get_priority_expiry_products(limit=10):
        now = timezone.now()
        ten_days_later = now + timedelta(days=10)

        # Lấy dữ liệu
        queryset = Product.objects.filter(
            is_active=True,
            expiry_date__gt=now,           # Chặn hàng đã hỏng
            manufacturing_date__isnull=False # Đảm bảo có NSX để tính toán
        ).annotate(
            # Nhãn priority: 1 cho hàng < 10 ngày, 2 cho hàng còn lại
            priority=Case(
                When(expiry_date__lte=ten_days_later, then=1),
                default=2,
                output_field=IntegerField(),
            )
        ).order_by(
            'priority',    # Hiện hàng dưới 10 ngày lên trước
            'expiry_date',  # Ai sắp hết hạn sớm hơn đứng trước (Không random)
            '-created_at'   # Nếu cùng ngày hết hạn, ai nhập mới nhất đứng trước
        )

        return queryset[:limit]