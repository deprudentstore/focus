function getWishlist() {
  try {
    return JSON.parse(localStorage.getItem("focus_wishlist") || "[]");
  } catch (e) {
    return [];
  }
}

function isWishlisted(productId) {
  return getWishlist().includes(productId);
}

function toggleWishlist(productId) {
  let list = getWishlist();
  if (list.includes(productId)) {
    list = list.filter((id) => id !== productId);
  } else {
    list.push(productId);
  }
  localStorage.setItem("focus_wishlist", JSON.stringify(list));
  return list.includes(productId);
}
