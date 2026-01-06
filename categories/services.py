from categories.models import Category

class CategoryService:
    # ========= READ (LẤY DỮ LIỆU HIỂN THỊ) =========
    @staticmethod
    def list(is_active=True):
        return Category.objects.filter(
            is_active=is_active
        ).order_by('sort_order', 'name') 
        # Sắp xếp: Ưu tiên số thứ tự (sort_order) -> Sau đó đến tên (name)

    @staticmethod
    def get_by_id(category_id):
        try:
            return Category.objects.get(id=category_id, is_active=True)
        except Category.DoesNotExist:
            raise ValueError(f"Category with ID {category_id} not found")

    # ========= ADMIN NOTE =========
    # Các chức năng Create, Update, Delete đã được lược bỏ.
    # Vui lòng sử dụng trang quản trị mặc định của Django: /admin/
    # để thêm sửa xóa danh mục.