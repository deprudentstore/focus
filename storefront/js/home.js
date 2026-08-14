(async function () {
  const newArrivalsEl = document.getElementById("newArrivals");
  const styledEditsEl = document.getElementById("styledEdits");

  try {
    const products = await apiGet("/products");
    newArrivalsEl.innerHTML = products.slice(0, 8).map(productCardHTML).join("");
    styledEditsEl.innerHTML = products.slice(0, 4).map(productCardHTML).join("");
  } catch (e) {
    newArrivalsEl.innerHTML = `<div class="status">Couldn't load products. Is the backend running?</div>`;
  }

  // Live hero banner from admin (falls back to the hardcoded default if none set)
  try {
    const banners = await apiGet("/banners");
    if (banners && banners.length) {
      const b = banners[0];
      const heroEl = document.getElementById("heroSection");
      if (b.image_url) heroEl.style.backgroundImage = `linear-gradient(0deg, rgba(20,20,20,.55), rgba(20,20,20,.25)), url('${b.image_url}')`;
      heroEl.innerHTML = `
        <div>
          <div class="eyebrow">${b.eyebrow}</div>
          <h1>${b.title}</h1>
          <p>${b.subtitle}</p>
          <a href="${b.link_url || "shop.html"}" class="btn btn-light">${b.button_text}</a>
        </div>`;
    }
  } catch (e) { /* keep default hero */ }

  // Live footer text from CMS
  try {
    const footerContent = await apiGet("/content/cms_footer_text");
    if (footerContent.value) document.getElementById("siteFooter").textContent = footerContent.value;
  } catch (e) { /* keep default footer */ }

  // Live SEO meta for this page
  try {
    const [titleContent, descContent] = await Promise.all([
      apiGet("/content/seo_home_title"),
      apiGet("/content/seo_home_description"),
    ]);
    if (titleContent.value) document.title = titleContent.value;
    if (descContent.value) {
      let metaDesc = document.querySelector('meta[name="description"]');
      if (!metaDesc) {
        metaDesc = document.createElement("meta");
        metaDesc.name = "description";
        document.head.appendChild(metaDesc);
      }
      metaDesc.content = descContent.value;
    }
  } catch (e) { /* keep default meta */ }
})();
