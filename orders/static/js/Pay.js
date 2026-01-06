const API_ENDPOINTS = {
    checkoutData: '/api/orders/checkout-data/', 
    createOrder: '/api/orders/create/',
    applyVoucher: '/api/orders/apply/'
};

let checkoutState = {
    subtotal: 0,
    discount: 0,
    total: 0,
    selectedAddressId: null,
    selectedVoucherCode: null,
    selectedPaymentMethod: null,
    addresses: [],
    items: []
};

document.addEventListener('DOMContentLoaded', () => {
    fetchCheckoutData();
    setupEventListeners();
});

async function fetchCheckoutData() {
    console.log("fetchCheckoutData đã được gọi")
    try {
        const response = await fetch(API_ENDPOINTS.checkoutData);
        const data = await response.json();

        checkoutState.items = data.items;
        checkoutState.addresses = data.addresses;
        checkoutState.subtotal = data.subtotal;

        renderProducts(data.items);
        renderVouchers(data.promotions);
        renderAddresses(data.addresses);
        renderPaymentMethods(data.payment_methods);
        
        const defaultAddr = data.addresses.find(a => a.is_default) || data.addresses[0];
        if (defaultAddr) selectAddress(defaultAddr.id);

        updateSummaryDisplay();
    } catch (error) {
        console.error("Lỗi tải dữ liệu checkout:", error);
    }
}

function renderProducts(items) {
    console.log("renderProducts đã được gọi")
    const container = document.getElementById('order-products-container');
    container.innerHTML = items.map(item => `
        <div class="product-item" style="display: flex; gap: 15px; padding: 12px 0; border-bottom: 1px solid #f1f1f1;">
            <img src="${item.image}" alt="${item.product_name}" style="width: 70px; height: 70px; object-fit: cover; border-radius: 8px;">
            <div style="flex: 1;">
                <h4 style="margin: 0 0 5px 0; font-size: 15px;">${item.product_name}</h4>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #666;">Số lượng: ${item.quantity}</span>
                    <span style="font-weight: 600; color: #e44d26;">${formatVND(item.unit_price * item.quantity)}</span>
                </div>
            </div>
        </div>
    `).join('');
}

function renderAddresses(addresses) {
    const dropdown = document.getElementById('address-dropdown');

    dropdown.innerHTML = addresses.map(addr => `
        <div class="address-option" onclick="selectAddressAndClose(${addr.id})">
            <div style="font-weight: bold;">
                ${addr.receiver_name} | ${addr.receiver_phone}
            </div>
            <div style="font-size: 13px; color: #666;">
                ${addr.full_address}
            </div>
            ${addr.is_default ? 
                '<span style="font-size:11px;color:#2d88ff;">Mặc định</span>' 
                : ''}
        </div>
    `).join('');
}

function renderVouchers(vouchers) {
    console.log("renderVouchers đã được gọi");
    const container = document.getElementById('voucher-render-list');
    
    if (!vouchers || vouchers.length === 0) {
        container.innerHTML = '<p style="font-size: 13px; color: #999;">Không có mã giảm giá khả dụng</p>';
        return;
    }

    container.innerHTML = vouchers.map(v => `
        <div class="voucher-card" 
             onclick="applyVoucher('${v.code}')" 
             id="v-${v.code}" 
             style="border: 1px solid #ddd; padding: 12px; margin-bottom: 10px; border-radius: 8px; cursor: pointer; position: relative; transition: all 0.3s;">
            
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="font-weight: bold; color: #e44d26; font-size: 16px;">${v.code}</div>
                <div style="font-size: 11px; color: #28a745; background: #e8f5e9; padding: 2px 6px; border-radius: 4px;">Khả dụng</div>
            </div>
            
            <div style="font-size: 12px; color: #555; margin-top: 5px;">${v.description}</div>
            <div style="font-size: 11px; color: #999; margin-top: 4px;">Đơn tối thiểu: ${formatVND(v.min_amount)}</div>
        </div>
    `).join('');
}

function renderPaymentMethods(methods) {
    console.log("renderPaymentMethods đã được gọi")
    const container = document.getElementById('payment-methods-render');
    container.innerHTML = methods.map((m, index) => `
        <label class="payment-item" style="display: flex; align-items: center; padding: 12px; border: 1px solid #eee; border-radius: 8px; margin-bottom: 8px; cursor: pointer;">
            <input type="radio" name="payment-method" value="${m.code}" ${index === 0 ? 'checked' : ''}>
            <img src="${m.icon_url}" style="width: 32px; height: 32px; margin: 0 12px;">
            <span style="font-weight: 500;">${m.name}</span>
        </label>
    `).join('');
}

function selectAddress(id) {
    console.log("selectAddress đã được gọi")
    const addr = checkoutState.addresses.find(a => a.id == id);
    if (addr) {
        checkoutState.selectedAddressId = addr.id;
        document.getElementById('selected-address-display').innerHTML = `
            <div style="padding: 10px; background: #f9f9f9; border-radius: 5px; border-left: 4px solid #e44d26;">
                <div style="font-weight: bold;">${addr.receiver_name} - ${addr.receiver_phone}</div>
                <div style="font-size: 14px; color: #666;">${addr.full_address}</div>
            </div>
        `;
    }
}

function confirmAddress() {
    console.log("confirmAddress đã được gọi")
    const checked = document.querySelector('input[name="addr-choice"]:checked');
    if (checked) {
        selectAddress(checked.value);
        closeModal();
    }
}

async function applyVoucher(code) {
    console.log("Hàm applyVoucher đang chạy với code:", code);
    
    const statusMsg = document.getElementById('voucher-status-msg');
    if (statusMsg) {
        statusMsg.innerText = "Đang kiểm tra mã...";
        statusMsg.style.display = 'block';
    }

    try {
        const response = await fetch(API_ENDPOINTS.applyVoucher, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ voucher_code: code })
        });

        const result = await response.json();

        if (result.success) {
            checkoutState.selectedVoucherCode = result.voucher_code;
            checkoutState.discount = parseFloat(result.discount_amount);
        
            document.querySelectorAll('.voucher-card').forEach(el => el.style.borderColor = '#ddd');
            const activeVoucher = document.getElementById(`v-${code}`);
            if (activeVoucher) activeVoucher.style.borderColor = '#e44d26';
            updateSummaryDisplay();
            
            if (statusMsg) statusMsg.innerText = "Áp dụng mã thành công!";
        } else {
            alert(result.message);
            if (statusMsg) statusMsg.style.display = 'none';
        }
    } catch (error) {
        console.error("Lỗi applyVoucher:", error);
        alert("Không thể kết nối máy chủ để áp dụng mã.");
    }
}

function updateSummaryDisplay() {
    console.log("updateSummaryDisplay đã được gọi");

    const realSubtotal = checkoutState.items.reduce(
        (sum, item) => sum + (Number(item.unit_price) * item.quantity),
        0
    );

    checkoutState.subtotal = realSubtotal;
    checkoutState.total = Math.max(0, realSubtotal - checkoutState.discount);

    document.getElementById('summary-subtotal').innerText =
        formatVND(realSubtotal);

    document.getElementById('summary-discount').innerText =
        `-${formatVND(checkoutState.discount)}`;

    document.getElementById('summary-total').innerText =
        formatVND(checkoutState.total);
}


async function submitOrder() {
    console.log("submitOrder đã được gọi")
    const btn = document.getElementById('confirm-payment-btn');
    const paymentMethod = document.querySelector('input[name="payment-method"]:checked')?.value;
    console.log("Phương thức gửi lên server:", paymentMethod);

    if (!checkoutState.selectedAddressId) {
        alert("Vui lòng chọn địa chỉ nhận hàng!");
        return;
    }

    const payload = {
        address_id: checkoutState.selectedAddressId,
        voucher_code: checkoutState.selectedVoucherCode,
        payment_method: paymentMethod
    };

    try {
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner"></span> ĐANG XỬ LÝ...';

        const response = await fetch(API_ENDPOINTS.createOrder, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(payload)
        });

        const result = await response.json();
        // Cần coi lại.
        if (result.success) {
            checkoutState.lastOrderId = result.order_id;

            if (result.payment_url) {
                window.location.href = result.payment_url;
                return; 
            }
            showOrderSuccessModal();
        } else {
            alert("Lỗi: " + result.message);
            btn.disabled = false;
            btn.innerText = "XÁC NHẬN ĐẶT HÀNG";
        }
    } catch (error) {
        console.error("Lỗi đặt hàng:", error);
        btn.disabled = false;
    }
}

function formatVND(amount) {
    console.log("formatVND đã được gọi")
    return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(amount);
}

function getCookie(name) {
    console.log("getCookie đã được gọi")
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
function toggleAddressList() {
    document.getElementById('address-dropdown')
        .classList.toggle('hidden');
}
function selectAddressAndClose(id) {
    selectAddress(id);
    document.getElementById('address-dropdown')
        .classList.add('hidden');
}

function setupEventListeners() {
    console.log("setupEventListeners đã được gọi")
    const btnSubmit = document.getElementById('confirm-payment-btn');
    if (btnSubmit) btnSubmit.onclick = submitOrder;
}
function showOrderSuccessModal() {
    document.getElementById('order-success-overlay')
        .classList.remove('hidden');
}

function goHome() {
    window.location.href = '/';
}

function goToOrders() {
    // bạn có thể đổi URL theo route của bạn
    window.location.href = '/orders/my/';
}


window.openModal = function() { document.getElementById('addressModal').style.display = 'block'; }
window.closeModal = function() { document.getElementById('addressModal').style.display = 'none'; }