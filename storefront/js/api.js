async function apiGet(path) {
  const res = await fetch(`${API_BASE_URL}${path}`);
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

async function apiPost(path, body) {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

function formatPrice(n) {
  return "₹" + Number(n).toLocaleString("en-IN");
}

function productCardHTML(p) {
  const badgeHTML = p.badge
    ? `<span class="badge ${p.badge === "SALE" ? "sale" : ""}">${p.badge}</span>`
    : "";
  const priceHTML = p.compare_at_price
    ? `<span class="old">${formatPrice(p.compare_at_price)}</span>${formatPrice(p.price)}
       <span class="off">${Math.round(100 - (p.price / p.compare_at_price) * 100)}% off</span>`
    : formatPrice(p.price);
  const wished = typeof isWishlisted === "function" && isWishlisted(p.id);

  return `
    <a class="product-card" href="product.html?slug=${p.slug}">
      <div class="thumb" style="background-image:url('${p.image_url || placeholderImage(p.name)}')">
        ${badgeHTML}
        <div class="wish ${wished ? "active" : ""}" data-product-id="${p.id}" onclick="handleWishClick(event, ${p.id})">${wished ? "♥" : "♡"}</div>
      </div>
      <div class="name">${p.name}</div>
      <div class="price">${priceHTML}</div>
    </a>`;
}

function handleWishClick(event, productId) {
  event.preventDefault();
  event.stopPropagation();
  const nowWished = toggleWishlist(productId);
  const el = event.currentTarget;
  el.textContent = nowWished ? "♥" : "♡";
  el.classList.toggle("active", nowWished);
}

function placeholderImage(seed) {
  return `https://source.unsplash.com/400x400/?jewelry,gold&sig=${encodeURIComponent(seed)}`;
}
