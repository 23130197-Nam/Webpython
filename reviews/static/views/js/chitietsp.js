// 1. Cấu hình API
const REVIEW_API = {
    BASE: '/api/reviews/',
    PRODUCT_REVIEWS: (id) => `/api/reviews/product/${id}/`,
    AVG_RATING: (id) => `/api/reviews/product/${id}/rating/`,
    DISTRIBUTION: (id) => `/api/reviews/product/${id}/distribution/`
};

// Lấy Product ID từ URL hoặc một biến toàn cục
const CURRENT_PRODUCT_ID = "PRD001"; // Tạm thời fix cứng hoặc lấy từ URL

// 2. Hàm lấy CSRF Token
function getCsrfToken() {
    return document.cookie.split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
}

// 3. Tải danh sách đánh giá
async function loadReviews() {
    try {
        const response = await fetch(REVIEW_API.PRODUCT_REVIEWS(CURRENT_PRODUCT_ID));
        const reviews = await response.json();
        
        const container = document.querySelector('.review-list');
        container.innerHTML = ''; // Xóa dữ liệu mẫu

        reviews.forEach(rev => {
            const stars = Array(5).fill(0).map((_, i) => 
                `<i class="${i < rev.rating ? 'fas' : 'far'} fa-star"></i>`
            ).join('');

            const html = `
                <div class="user-review-item" id="review-${rev.id}">
                    <div class="avatar-circle">${rev.user_name.charAt(0)}</div>
                    <div class="comment-content">
                        <h5>${rev.user_name} <span class="comment-date">- ${new Date(rev.created_at).toLocaleDateString()}</span></h5>
                        <div class="comment-stars">${stars}</div>
                        <p class="comment-text">${rev.content}</p>
                    </div>
                </div>
            `;
            container.insertAdjacentHTML('beforeend', html);
        });
    } catch (err) {
        console.error("Lỗi tải đánh giá:", err);
    }
}

// 4. Tải thống kê xếp hạng (Sao trung bình và Biểu đồ)
async function loadRatingStats() {
    try {
        // Lấy điểm trung bình
        const avgRes = await fetch(REVIEW_API.AVG_RATING(CURRENT_PRODUCT_ID));
        const avgData = await avgRes.json();
        document.querySelector('.rating-number').innerText = avgData.average_rating.toFixed(1);

        // Lấy phân phối sao
        const distRes = await fetch(REVIEW_API.DISTRIBUTION(CURRENT_PRODUCT_ID));
        const distData = await distRes.json();
        
        const bars = document.querySelectorAll('.bar-row');
        // Phân phối trả về từ API dạng {1: count, 2: count...}
        Object.keys(distData.distribution).forEach(star => {
            const count = distData.distribution[star];
            const row = bars[5 - star]; // Đảo ngược vì 5 sao nằm đầu
            if (row) {
                row.querySelector('.p-fill').style.width = `${(count / 32) * 100}%`; // Giả sử tổng 32
                row.querySelector('span:last-child').innerText = count;
            }
        });
    } catch (err) {
        console.warn("Lỗi tải thống kê:", err);
    }
}

// 5. Gửi đánh giá mới
async function postReview() {
    const content = document.querySelector('.review-textarea').value;
    const rating = document.querySelectorAll('.rating-input .selected').length;

    if (!content) return alert("Vui lòng nhập nội dung!");

    const payload = {
        id: "REV" + Date.now(), // Logic tạo ID của bạn
        product: CURRENT_PRODUCT_ID,
        user: 1, // Lấy ID user đang đăng nhập
        rating: rating,
        title: "Đánh giá sản phẩm",
        content: content
    };

    try {
        const response = await fetch(REVIEW_API.BASE, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            alert("Gửi thành công!");
            location.reload();
        } else {
            const error = await response.json();
            alert("Lỗi: " + JSON.stringify(error));
        }
    } catch (err) {
        console.error("Lỗi kết nối:", err);
    }
}

// Khởi chạy khi trang load
document.addEventListener('DOMContentLoaded', () => {
    loadReviews();
    loadRatingStats();
    
    // Gán sự kiện cho nút gửi
    document.querySelector('.btn-submit').addEventListener('click', postReview);
});