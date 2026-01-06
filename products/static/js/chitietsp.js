// 1. QUẢN LÝ TRẠNG THÁI TRONG RAM
let currentOffset = 5; 
let totalReviewCount = 0;
let currentRating = 0;

// 2. BẢO MẬT CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


document.addEventListener("DOMContentLoaded", function () {
    if (typeof productId === 'undefined' || !productId || productId === "None") {
        console.error("LỖI: productId không hợp lệ.");
        return;
    }

    initProductPage(productId);
    setupStarRating();
    setupReviewSubmit(productId);
});

// HÀM ĐIỀU PHỐI CHÍNH (GỌI API GỘP)
async function initProductPage(id) {
    const apiUrl = `/api/products/detail/${id}/`;
    const reviewContainer = document.querySelector('.review-list');
    if (reviewContainer) reviewContainer.innerHTML = '<p class="text-center">Đang nạp đánh giá mới...</p>';
    try {
        const response = await fetch(apiUrl);
        if (!response.ok) throw new Error("Lỗi mạng");
        
        const data = await response.json();

        // Đổ dữ liệu vào các vùng nhớ và render
        renderMainProductInfo(data.product);
        renderRelatedProducts(data.related_products);
        renderStatsUI(data.reviews.stats);
       
        
        // Render 5 cái đầu
        const reviewContainer = document.querySelector('.review-list');
        renderReviewsList(data.reviews.latest_list, reviewContainer);
       

        totalReviewCount = data.reviews.total_count;
        currentOffset = data.reviews.latest_list.length;
        checkLoadMoreVisibility(id);

    } catch (error) {
        console.error("Lỗi:", error);
        document.getElementById('main-product-target').innerHTML = `<p class="text-danger">Lỗi nạp dữ liệu</p>`;
    }
}

// chi tiết sp
function renderMainProductInfo(product) {
    const container = document.getElementById('main-product-target');
    if (!container) return;
    const mainImgUrl = product.images || 'https://via.placeholder.com/500x500?text=No+Image';
    
    const priceFormatted = formatCurrency(product.price);
    const oldPriceHtml = product.old_price > product.price ? `<span class="old-price">${formatCurrency(product.old_price)}</span>` : '';
    const discountBadge = product.discount_percent ? `<span class="discount-badge">${product.discount_percent}</span>` : '';

    container.innerHTML = `
    <div class="product-detail-box">
        <div class="product-images">
            <div class="main-img-wrapper"><img src="${mainImgUrl}" id="mainImg" class="main-img" alt="${product.name}"></div>
            <div class="thumb-list">
                <div class="thumb-item active" onclick="changeImage(this, '${mainImgUrl}')"><img src="${mainImgUrl}"></div>
            </div>
        </div>
        <div class="product-content">
            <span class="category-tag text-uppercase">${product.category_name || 'Thực phẩm'}</span>
            <h1 class="product-name">${product.name}</h1>
            <div class="review-row">${renderStars(product.rating_average || 0)} <span class="review-count">(${product.review_count} đánh giá)</span></div>
            <div class="price-row">
                <span class="current-price">${priceFormatted}</span>
                ${oldPriceHtml} ${discountBadge}
            </div>
            <p class="short-desc">${product.description || 'Chưa có mô tả.'}</p>
            <ul class="specs-list">
                <li><strong>Hạn sử dụng:</strong> ${product.expiry_date || 'Xem bao bì'}</li>
                <li><strong>Bảo quản:</strong> Ngăn mát tủ lạnh</li>
            </ul>
            <div class="action-row">
                <div class="qty-control">
                    <button class="qty-btn" onclick="updateQty(-1)">-</button>
                    <input type="text" value="1" class="qty-input" id="qtyInput">
                    <button class="qty-btn" onclick="updateQty(1)">+</button>
                </div>
                <button class="btn-add" onclick="addToCart(${product.id})"><i class="fas fa-shopping-cart"></i> Thêm vào giỏ</button>
                <a href="#"><button class="btn-buy-now"><i class="fas fa-check"></i> Mua ngay</button></a>
            </div>
        </div>
    </div>`;
}

// sản phẩm liên quan
function renderRelatedProducts(products) {
    const container = document.getElementById('related-products-container');
    if (!container || !products) return;

    container.innerHTML = products.map(item => `
        <div class="product-item">
            <figure><a href="/api/products/detaill/${item.id}/"><img src="${item.thumbnail || 'https://via.placeholder.com/300x300'}" class="tab-image"></a></figure>
            <div class="product-details">
                <h3 class="product-title"><a href="/api/products/detaill/${item.id}/">${item.name}</a></h3>
                <div class="rating">${renderStars(item.rating_average || 0)} <span>(${item.review_count})</span></div>
                <div class="price-box">
                    <span class="new-price">${formatCurrency(item.price)}</span>
                </div>
                <div class="button-area">
                    <div class="row-btn">
                        <input type="number" value="1" class="qty-input-mini" min="1">
                        <button class="btn-cart-mini" onclick="addToCart(${item.id})"><i class="fas fa-shopping-cart"></i> Thêm</button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

// 7. XỬ LÝ ĐÁNH GIÁ (LIST & STATS)
function renderStatsUI(stats) {
    document.getElementById('avg-rating').innerText = (stats.average || 0).toFixed(1);
    document.getElementById('total-reviews-count').innerText = `${stats.total || 0} đánh giá`;
    for (let i = 1; i <= 5; i++) {
        const count = stats.distribution[i] || 0;
        const percent = stats.total > 0 ? (count / stats.total) * 100 : 0;
        const bar = document.getElementById(`bar-${i}`);
        if (bar) {
            bar.style.width = `${percent}%`;
            bar.parentElement.nextElementSibling.innerText = count;
        }
    }
}

function renderReviewsList(reviews, container) {
    if (!container) return;
    container.innerHTML = reviews.length ? '' : '<p class="text-center">Chưa có đánh giá nào.</p>';
    reviews.forEach(r => container.insertAdjacentHTML('beforeend', createReviewItemHTML(r)));
}

function createReviewItemHTML(data) {
    const avatar = (data.user_name || 'K').charAt(0).toUpperCase();
    const date = data.created_at ? new Date(data.created_at).toLocaleDateString('vi-VN') : 'Vừa xong';
    return `
        <div class="user-review-item">
            <div class="avatar-circle">${avatar}</div>
            <div class="comment-content">
                <h5>${data.user_name || 'Khách hàng'} <span class="comment-date">- ${date}</span></h5>
                <div class="comment-stars">${renderStars(data.rating)}</div>
                <p class="comment-text">${data.content}</p>
            </div>
        </div>`;
}

// 8. XỬ LÝ XEM THÊM
function checkLoadMoreVisibility(id) {
    let btn = document.getElementById('btn-load-more');
    if (!btn && totalReviewCount > 5) {
        const list = document.querySelector('.review-list');
        list.insertAdjacentHTML('afterend', '<div class="text-center mt-4"><button id="btn-load-more" class="btn btn-primary">Xem thêm</button></div>');
        btn = document.getElementById('btn-load-more');
    }
    if (btn) {
        btn.style.display = totalReviewCount > currentOffset ? 'inline-block' : 'none';
        btn.onclick = () => loadNextReviews(id);
    }
}

async function loadNextReviews(id) {
    const btn = document.getElementById('btn-load-more');
    btn.disabled = true;
    try {
        const res = await fetch(`/api/products/detail/${id}/reviews/?offset=${currentOffset}&limit=5`);
        const data = await res.json();
        if (data.length) {
            const container = document.querySelector('.review-list');
            data.forEach(r => container.insertAdjacentHTML('beforeend', createReviewItemHTML(r)));
            currentOffset += data.length;
        }
        checkLoadMoreVisibility(id);
    } finally { btn.disabled = false; }
}

// 9. CHỌN SAO & GỬI POST
function setupStarRating() {
    const stars = document.querySelectorAll('#star-container i');
    stars.forEach(star => {
        star.style.cursor = 'pointer';
        star.onclick = function() {
            currentRating = parseInt(this.getAttribute('data-value'));
            stars.forEach(s => s.className = parseInt(s.getAttribute('data-value')) <= currentRating ? 'fas fa-star' : 'far fa-star');
            document.getElementById('rating-text').innerText = `(${currentRating} sao)`;
        };
    });
}

async function setupReviewSubmit(id) {
    const btn = document.getElementById('btn-submit-review');
    if (!btn) return;

    btn.onclick = async function() {
        // Kiểm tra nhanh trong RAM trình duyệt xem có CSRF Token không
        if (!getCookie('csrftoken')) {
            alert("Bạn cần đăng nhập để đánh giá sản phẩm này!");
            return;
        }

        const content = document.getElementById('review-content').value.trim();
        if (currentRating === 0 || content.length < 10) return alert("Nhập đủ thông tin.");

        btn.disabled = true;
        const url = `/api/products/detail/${id}/reviews/`;
        try {
            const res = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                // GỬI THÊM TRƯỜNG TITLE ĐỂ KHỚP VỚI SERIALIZER
                body: JSON.stringify({ 
                    rating: currentRating, 
                    content: content,
                    title: content.substring(0, 50) // Lấy 50 ký tự đầu làm tiêu đề
                })
            });

            if (res.status === 403) {
                alert("Lỗi: Bạn phải đăng nhập mới có thể đánh giá!");
            } else if (res.ok) {
                alert("Đánh giá thành công!");
                location.reload();
            }
        } catch (e) {
            alert("Lỗi kết nối.");
        } finally {
            btn.disabled = false;
        }
    };
}

// 10. HELPERS (FORMAT, QTY, STARS)
function formatCurrency(amount) { return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(amount || 0); }
function renderStars(rating) {
    let s = '';
    for (let i = 1; i <= 5; i++) {
        if (rating >= i) s += '<i class="fas fa-star"></i>';
        else if (rating >= i - 0.5) s += '<i class="fas fa-star-half-alt"></i>';
        else s += '<i class="far fa-star"></i>';
    }
    return s;
}
function changeImage(el, src) { document.getElementById('mainImg').src = src; document.querySelectorAll('.thumb-item').forEach(i => i.classList.remove('active')); el.classList.add('active'); }
function updateQty(val) { let i = document.getElementById('qtyInput'); let n = (parseInt(i.value) || 1) + val; if (n >= 1) i.value = n; }
function addToCart(id) { alert("Đã thêm sản phẩm " + id + " vào giỏ!"); }