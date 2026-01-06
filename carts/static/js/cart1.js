/* ================= CONFIG ================= */
const API_BASE = "/api/carts/api/carts";
const USER_ID = "guest";

/* ================= STATE ================= */
let cartId = null;

/* ================= CSRF ================= */
function getCSRFToken() {
  const name = "csrftoken=";
  const cookies = document.cookie.split(";");

  for (let cookie of cookies) {
    cookie = cookie.trim();
    if (cookie.startsWith(name)) {
      return cookie.substring(name.length);
    }
  }
  return "";
}

/* ================= UTILS ================= */
function formatMoney(value) {
  return Number(value).toLocaleString("vi-VN") + "đ";
}

/* ================= LOAD CART ================= */
async function loadCart() {
  try {
    const res = await fetch(`${API_BASE}/user/${USER_ID}/`);
    if (!res.ok) {
      console.error("❌ Load cart failed");
      return;
    }

    const cart = await res.json();
    cartId = cart.id;

    renderItems(cart.items || []);
    updateSummary(cart);
  } catch (err) {
    console.error("❌ Load cart error:", err);
  }
}

/* ================= RENDER ITEMS ================= */
function renderItems(items) {
  const container = document.getElementById("cartItems");
  if (!container) return;

  container.innerHTML = "";

  if (items.length === 0) {
    container.innerHTML = "<p>Giỏ hàng trống</p>";
    return;
  }

  items.forEach(item => {
    const div = document.createElement("div");
    div.className = "cart-item";
    div.dataset.product = item.product;

    div.innerHTML = `
      <input type="checkbox" class="item-check" checked>

      <img src="${item.product_image || 'https://via.placeholder.com/80'}" alt="product">

      <span class="name">${item.product_name}</span>

      <div class="quantity">
        <button class="minus">-</button>
        <span class="qty">${item.quantity}</span>
        <button class="plus">+</button>
      </div>

      <span class="item-total">${formatMoney(item.line_total)}</span>

      <button class="remove">✕</button>
    `;

    bindItemEvents(div);
    container.appendChild(div);
  });
}

/* ================= ITEM EVENTS ================= */
function bindItemEvents(itemEl) {
  const productId = itemEl.dataset.product;
  const qtyEl = itemEl.querySelector(".qty");

  itemEl.querySelector(".plus").addEventListener("click", () => {
    updateQty(productId, Number(qtyEl.innerText) + 1);
  });

  itemEl.querySelector(".minus").addEventListener("click", () => {
    const current = Number(qtyEl.innerText);
    if (current > 1) {
      updateQty(productId, current - 1);
    }
  });

  itemEl.querySelector(".remove").addEventListener("click", () => {
    removeItem(productId);
  });
}

/* ================= API ACTIONS ================= */
async function updateQty(productId, quantity) {
  if (!cartId) return;

  await fetch(`${API_BASE}/${cartId}/update_quantity/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCSRFToken()
    },
    body: JSON.stringify({ product_id: productId, quantity })
  });

  loadCart();
}

async function removeItem(productId) {
  if (!cartId) return;

  await fetch(`${API_BASE}/${cartId}/remove_item/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCSRFToken()
    },
    body: JSON.stringify({ product_id: productId })
  });

  loadCart();
}

/* ================= SUMMARY ================= */
function updateSummary(cart) {
  document.getElementById("subtotal").innerText = formatMoney(cart.subtotal || 0);
  document.getElementById("total").innerText = formatMoney(cart.total || 0);
}

/* ================= CHECKOUT ================= */
async function checkout() {
  if (!cartId) {
    alert("Giỏ hàng trống");
    return;
  }

  console.log("🔥 Checkout clicked");

  try {
    const res = await fetch("/api/payments/create/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken()
      },
      body: JSON.stringify({
        order_id: `order_${cartId}`,
        amount: 1000000,
        currency: "USD",
        method: "BANK_TRANSFER"
      })

    });

    const data = await res.json();
    console.log("✅ Payment response:", data);

    if (!res.ok) {
      alert("Thanh toán thất bại");
      return;
    }

    alert("Thanh toán thành công (demo)");
  } catch (err) {
    console.error("❌ Checkout error:", err);
  }
}

/* ================= INIT ================= */
document.addEventListener("DOMContentLoaded", () => {
  loadCart();

  const checkoutBtn = document.getElementById("checkoutBtn");
  if (!checkoutBtn) {
    console.error("❌ checkoutBtn not found");
    return;
  }

  checkoutBtn.addEventListener("click", checkout);
  console.log("✅ Cart JS ready");
});
