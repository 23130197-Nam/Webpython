  /* ================= CSRF ================= */
  function getCSRFToken() {
    const name = "csrftoken=";
    return document.cookie
      .split(";")
      .map(c => c.trim())
      .find(c => c.startsWith(name))
      ?.substring(name.length) || "";
  }

  const CSRF_TOKEN = getCSRFToken();

  /* ================= UTILS ================= */
  function formatMoney(value) {
    return Number(value || 0).toLocaleString("vi-VN") + "đ";
  }

  /* ================= STATE ================= */
  let CART_STATE = [];
  let CART_META = {};

  /* ================= LOAD CART ================= */
  async function loadCart() {
    console.log("loadCart đã chạy");
    try {
      const res = await fetch("/api/carts/cart");
      if (!res.ok) return showEmptyCart();

      const cart = await res.json();

      CART_STATE = cart.items || [];
      CART_META = cart;

      renderItems();
      updateSummary();
      syncSelectAllCheckbox();
    } catch (e) {
      console.error("Load cart error:", e);
    }
  }

  /* ================= RENDER ITEMS ================= */
  function renderItems() {
    const container = document.getElementById("cartItems");
    const emptyCart = document.getElementById("emptyCart");
    if (!container) return;

    container.innerHTML = "";

    if (CART_STATE.length === 0) {
      if (emptyCart) emptyCart.style.display = "block";
      return;
      
    }
    if (emptyCart) emptyCart.style.display = "none";

    CART_STATE.forEach(item => {
      const div = document.createElement("div");
      div.className = "cart-item";
      
      // 🎁 QUÀ TẶNG
      if (item.is_gift) {
        div.innerHTML = `
          <div class="gift-row">
            🎁 ${item.gift_message}
          </div>
        `;
        container.appendChild(div);
        return;
      }
      
      //in sản phẩm ra
    const displayUnitPrice = item.total_price / item.quantity;
    const isDiscounted = displayUnitPrice < item.product_price;


    div.innerHTML = `
      <input type="checkbox"
            class="select-item"
            ${item.is_select ? "checked" : ""}>

      <img src="${item.product_image || "/static/images/no-image.png"}">

      <span class="name">${item.product_name}</span>

      <div class="quantity">
        <button class="minus">-</button>
        <span class="qty">${item.quantity}</span>
        <button class="plus">+</button>
      </div>

        <div class="price-box">
      ${isDiscounted? ` <span class="old-price"> ${formatMoney(item.product_price)} </span>

            <span class="sale-price">
             ${formatMoney(displayUnitPrice)}
            </span>

            <span class="discount-badge">-${Math.round(100 - (displayUnitPrice / item.product_price) * 100)}%</span> `: `
            <span class="sale-price">
              ${formatMoney(item.product_price)}
            </span>
          `
      }
  </div>

      <button class="remove">✕</button> `;



      bindItemEvents(div, item);
      container.appendChild(div);
    });
  }


  /* ================= ITEM EVENTS ================= */
  function bindItemEvents(el, item) {
    console.log("bindItemEvents đã chạy");
    const productId = item.product_id;

    if (!item.is_gift) {
      el.querySelector(".plus").onclick = () =>
        updateQty(productId, item.quantity + 1);

      el.querySelector(".minus").onclick = () => {
        item.quantity > 1
          ? updateQty(productId, item.quantity - 1)
          : removeItem(productId);
      };

      el.querySelector(".remove").onclick = () =>
        removeItem(productId);

      el.querySelector(".select-item").onchange = e =>
        setItemSelect(productId, e.target.checked);
    }
  }


  /* ================= API ================= */
  async function updateQty(productId, quantity) {
    console.log("updateQty đã chạy");
    await fetch("/api/carts/cart/update/", {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": CSRF_TOKEN
      },
      body: JSON.stringify({ product_id: productId, quantity })
    });
    loadCart();
  }

  async function removeItem(productId) {
    console.log("removeItem đã chạy");
    await fetch("/api/carts/cart/remove/", {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": CSRF_TOKEN
      },
      body: JSON.stringify({ product_id: productId })
    });
    loadCart();
  }

  async function clearCart() {
    if (!confirm("Xóa toàn bộ giỏ hàng?")) return;

    await fetch("/api/carts/cart/clear/", {
      method: "DELETE",
      headers: { "X-CSRFToken": CSRF_TOKEN }
    });
    loadCart();
  }

  /* ================= SELECT ================= */
  async function setItemSelect(productId, isSelect) {
    console.log("setItemSelect đã chạy");
    await fetch("/api/carts/cart/select-item/", {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": CSRF_TOKEN
      },
      body: JSON.stringify({
        product_id: productId,
        is_select: isSelect
      })
    });
    loadCart();
  }

  async function toggleSelectAll(checked) {
    await fetch("/api/carts/cart/select-all/", {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": CSRF_TOKEN
      },
      body: JSON.stringify({ is_select: checked })
    });
    loadCart();
  }

  function syncSelectAllCheckbox() {
    const selectAll = document.getElementById("selectAll");
    if (!selectAll) return;

    const selectable = CART_STATE.filter(i => !i.is_gift);
    selectAll.checked =
      selectable.length > 0 &&
      selectable.every(i => i.is_select);
  }

  /* ================= SUMMARY ================= */
function updateSummary() {
  const selectedTotal = CART_STATE
    .filter(item => item.is_select && !item.is_gift)
    .reduce((sum, item) => sum + Number(item.total_price || 0), 0);

  document.getElementById("subtotal").innerText =
    formatMoney(selectedTotal);

  document.getElementById("total").innerText =
    formatMoney(selectedTotal);
}

  /* ================= EMPTY ================= */
  function showEmptyCart() {
    document.getElementById("emptyCart").style.display = "block";
  }

  /* ================= INIT ================= */
  document.addEventListener("DOMContentLoaded", () => {
    loadCart();
    const checkoutBtn = document.getElementById("checkoutBtn");
    if (checkoutBtn) {
        checkoutBtn.onclick = () => {
            const hasSelectedItem = CART_STATE.some(i => i.is_select && !i.is_gift);
            if (!hasSelectedItem) {
                alert("Vui lòng chọn ít nhất 1 sản phẩm để đi đến trang thanh toán.");
                return;
            }
            window.location.href = "/api/orders/order/";
        };
    }
    const clearBtn = document.getElementById("clearCartBtn");
    if (clearBtn) {
      clearBtn.onclick = () => {
        clearCart();
      };
    }
  });
