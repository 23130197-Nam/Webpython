function formatMoney(n) {
  return n.toLocaleString("vi-VN") + "đ";
}

function updateCart() {
  let subtotal = 0;

  document.querySelectorAll(".cart-item").forEach(item => {
    const price = Number(item.dataset.price);
    const qty = Number(item.querySelector(".qty").innerText);
    const checked = item.querySelector(".item-check").checked;

    const total = price * qty;
    item.querySelector(".item-total").innerText = formatMoney(total);

    if (checked) subtotal += total;
  });

  document.getElementById("subtotal").innerText = formatMoney(subtotal);
  document.getElementById("total").innerText = formatMoney(subtotal);
}

document.querySelectorAll(".cart-item").forEach(item => {
  const plus = item.querySelector(".plus");
  const minus = item.querySelector(".minus");
  const qty = item.querySelector(".qty");
  const check = item.querySelector(".item-check");

  plus.onclick = () => {
    qty.innerText = Number(qty.innerText) + 1;
    updateCart();
  };

  minus.onclick = () => {
    if (Number(qty.innerText) > 1) {
      qty.innerText--;
      updateCart();
    }
  };

  check.onchange = updateCart;

  item.querySelector(".remove").onclick = () => {
    item.remove();
    updateCart();
  };
});

document.getElementById("selectAll").onchange = function () {
  document.querySelectorAll(".item-check").forEach(cb => cb.checked = this.checked);
  updateCart();
};

updateCart();
