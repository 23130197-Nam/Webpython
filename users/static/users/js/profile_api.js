
function switchTab(element, tabId) {
    document.querySelectorAll('.menu-item').forEach(el => el.classList.remove('active'));
    element.classList.add('active');
    document.querySelectorAll('.content-box').forEach(el => el.classList.remove('active'));

    const tab = document.getElementById(tabId);
    if (tab) {
        tab.classList.add('active');
    }
}
// 1. CẤU HÌNH URL API (Đảm bảo khớp với urls.py của bạn)
const API_URL = {
    PROFILE: '/api/users/profile/',
    ADDRESS: '/api/users/addresses/'
};

// 2. HÀM LẤY CSRF TOKEN (Bắt buộc với Django)
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
const csrftoken = getCookie('csrftoken');
// --- 2. LOGIC MODAL (GIAO DIỆN) ---
function openModal() {
    const modal = document.getElementById('modal-add-address');
    if (modal) {
        modal.style.display = 'block';
    } else {
        console.error("Lỗi: Không tìm thấy ID 'modal-add-address'");
    }
}

// Hàm đóng modal
function closeModal() {
    const modal = document.getElementById('modal-add-address');
    if (modal) {
        modal.style.display = 'none';
    }
}
// (Nếu muốn xịn hơn) Bấm ra ngoài vùng trắng thì tự đóng modal
window.onclick = function (event) {
    const modal = document.getElementById('modal-add-address');
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

//  HÀM LOAD DỮ LIỆU KHI VÀO TRANG (Method: GET)
async function loadUserProfile() {
    try {
        const response = await fetch(API_URL.PROFILE, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                // Nếu dùng Session Auth thì trình duyệt tự gửi cookie, không cần Header Auth
            }
        });

        if (!response.ok) {
            throw new Error('Không thể tải thông tin user');
        }

        const data = await response.json();
        console.log("Dữ liệu User lấy về:", data);

        // Đổ dữ liệu vào HTML (DOM Manipulation)
        // Lưu ý: data.username, data.phone khớp với Serializer của bạn
        document.getElementById('input-username').value = data.username || '';
        document.getElementById('input-email').value = 'user@example.com'; // Serializer bạn chưa có email, tạm fix cứng hoặc bổ sung
        document.getElementById('input-phone').value = data.phone || '';

        // Load luôn địa chỉ nếu cần
        loadUserAddresses(data.addresses);

    } catch (error) {
        console.error('Lỗi:', error);
        alert('Có lỗi khi tải hồ sơ. Vui lòng đăng nhập lại.');
    }
}

//  HÀM CẬP NHẬT THÔNG TIN (Method: PUT)
async function updateProfile() {
    // Lấy dữ liệu từ ô input
    const updatedData = {
        username: document.getElementById('input-username').value,
        phone: document.getElementById('input-phone').value
    };

    try {
        const response = await fetch(API_URL.PROFILE, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken // QUAN TRỌNG: Gửi kèm token chống hack
            },
            body: JSON.stringify(updatedData)
        });

        if (response.ok) {
            const result = await response.json();
            alert('Cập nhật thành công!');
            const newName = document.getElementById('input-username').value;
            // Tìm thẻ hiển thị tên ở sidebar và thay đổi nội dung
            const sidebarNameLabel = document.getElementById('sidebar-username');

            // Nếu tìm thấy thì thay chữ cũ bằng chữ mới
            if (sidebarNameLabel) {
                sidebarNameLabel.innerText = updatedData.username;
            }
            console.log("Kết quả server trả về:", result);
        } else {
            const err = await response.json();
            alert('Lỗi cập nhật: ' + JSON.stringify(err));
        }
    } catch (error) {
        console.error('Lỗi:', error);
    }
}

//  HÀM HIỂN THỊ DANH SÁCH ĐỊA CHỈ (Render HTML từ JS)
function loadUserAddresses(addresses) {
    const container = document.querySelector('.address-list');
    // Giữ lại nút "Thêm mới", xóa các thẻ cũ
    const btnAdd = container.querySelector('.btn-add-addr');
    container.innerHTML = '';

    if (addresses && addresses.length > 0) {
        addresses.forEach(addr => {
            // Tạo HTML cho từng thẻ địa chỉ
            const html = `
                <div class="address-card">
                    <div class="address-row">
                        <div>
                            <span class="addr-name">Địa chỉ ${addr.id}</span>
                        </div>
                    </div>
                    <p class="addr-text">
                        ${addr.street}, ${addr.ward}, ${addr.province}
                    </p>
                    <div class="addr-actions">
                        <button class="btn-text">Cập nhật</button>
                    </div>
                </div>
            `;
            container.innerHTML += html;
        });
    } else {
        container.innerHTML += '<p>Chưa có địa chỉ nào.</p>';
    }

    // Gắn lại nút thêm
    container.appendChild(btnAdd);
}
//  Gửi Địa Chỉ Mới (POST) - [CODE QUAN TRỌNG MỚI THÊM]
async function submitNewAddress() {
    console.log("Đang gửi địa chỉ...");

    const streetInput = document.getElementById('new-street');
    const wardInput = document.getElementById('new-ward');
    const provInput = document.getElementById('new-province');


    if (!streetInput || !wardInput || !provInput) {
        alert("Lỗi HTML: Không tìm thấy ô nhập liệu!");
        return;
    }

    const payload = {
        street: streetInput.value.trim(),
        ward: wardInput.value.trim(),
        province: provInput.value.trim()
    };

    if (!payload.street || !payload.ward || !payload.province) {
        alert("Vui lòng nhập đầy đủ thông tin!");
        return;
    }

    try {
        const response = await fetch(API_URL.ADDRESS, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            alert("Thêm địa chỉ thành công!");
            closeModal();
            location.reload();
        } else {
            const errData = await response.json();
            alert("Lỗi Server: " + JSON.stringify(errData));
        }

    } catch (error) {
        console.error("Lỗi kết nối:", error);
        alert("Không thể kết nối đến Server.");
    }
}
//  Đổi Mật Khẩu (PUT)
async function changePassword() {
    console.log("Đang đổi mật khẩu...");

    const newPass = document.getElementById('new-pass').value;
    const confirmPass = document.getElementById('confirm-pass').value;

    //  Kiểm tra rỗng
    if (!newPass || !confirmPass) {
        alert("Vui lòng nhập đầy đủ mật khẩu!");
        return;
    }

    //  CHECK TRÙNG KHỚP (Đây là cái bạn đang thiếu)
    if (newPass !== confirmPass) {
        alert("Lỗi: Mật khẩu xác nhận không khớp!");
        return;
    }

    // Check độ dài (Optional)
    if (newPass.length < 6) {
        alert("Mật khẩu phải có ít nhất 6 ký tự!");
        return;
    }

    //  Gửi API
    try {
        const response = await fetch(API_URL.PROFILE, {
            method: 'PUT', // Dùng chung API Profile (hoặc API riêng tùy backend)
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({
                password: newPass // Backend Key phải khớp với Serializer
            })
        });

        if (response.ok) {
            alert("Đổi mật khẩu thành công! Vui lòng đăng nhập lại.");
            // Reset ô nhập
            document.getElementById('new-pass').value = '';
            document.getElementById('confirm-pass').value = '';
        } else {
            const err = await response.json();
            alert("Lỗi: " + JSON.stringify(err));
        }
    } catch (error) {
        console.error("Lỗi đổi pass:", error);
        alert("Có lỗi xảy ra.");
    }
}
//  TỰ ĐỘNG CHẠY KHI TRANG LOAD XONG
document.addEventListener('DOMContentLoaded', function () {
    loadUserProfile();
});



