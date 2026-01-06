function createProductHTML(p, isSlide = false) {
    // 1. Xác định URL đích dựa trên urls.py của bạn
    // URL chuẩn: /api/products/detaill/ID/
    const detailLink = `/api/products/detaill/${p.id}/`; 

    let imgUrl = p.thumbnail ? p.thumbnail : 'https://placehold.co/300x300?text=No+Image';
    const wrapperClass = isSlide ? 'swiper-slide' : 'col';

    return `
        <div class="${wrapperClass}">
            <div class="product-item position-relative">
                <figure>
                    <a href="${detailLink}">
                        <img src="${imgUrl}" alt="${p.name}" class="tab-image img-fluid" style="height: 200px; object-fit: contain;">
                    </a>
                </figure>
                <div class="d-flex flex-column text-center">
                    <h3 class="fs-6 fw-normal">
                        <a href="${detailLink}" class="text-decoration-none text-dark text-truncate d-block">${p.name}</a>
                    </h3>
                    </div>
            </div>
        </div>
    `;
}