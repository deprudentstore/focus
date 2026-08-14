"""
Run once after deploy to populate sample data:
    python seed.py
"""
import os
from database import SessionLocal, Base, engine
import models
from auth import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# --- Admin user ---
admin_email = os.getenv("SEED_ADMIN_EMAIL", "admin@focus.demo")
admin_password = os.getenv("SEED_ADMIN_PASSWORD", "ChangeMe123!")
if not db.query(models.AdminUser).filter(models.AdminUser.email == admin_email).first():
    db.add(models.AdminUser(email=admin_email, hashed_password=hash_password(admin_password), name="Admin User", role="owner", is_active=True))
    print(f"Created admin user: {admin_email} / {admin_password} (role: owner)")

# --- Categories ---
categories = ["Necklaces", "Earrings", "Rings", "Bracelets"]
cat_objs = {}
for name in categories:
    slug = name.lower()
    existing = db.query(models.Category).filter(models.Category.slug == slug).first()
    if not existing:
        existing = models.Category(name=name, slug=slug)
        db.add(existing)
        db.flush()
    cat_objs[name] = existing

db.commit()

# --- Products (matches the New Arrivals screenshot) ---
products = [
    dict(name="Lumen Pearl Drop Earrings", slug="lumen-pearl-drop-earrings", price=1499, compare_at_price=1999,
         badge="NEW", category="Earrings", stock=20,
         description="Freshwater pearl drops on a delicate gold-plated hook."),
    dict(name="Aurora Layered Choker", slug="aurora-layered-choker", price=2299, compare_at_price=None,
         badge="NEW", category="Necklaces", stock=15,
         description="A layered choker with fine chain detailing for an elevated everyday look."),
    dict(name="Celeste Stacking Band", slug="celeste-stacking-band", price=899, compare_at_price=None,
         badge="", category="Rings", stock=6, sizes="5,6,7,8",
         description="A slim pave band made to stack or wear alone."),
    dict(name="Lyra Tennis Bracelet", slug="lyra-tennis-bracelet", price=2199, compare_at_price=2799,
         badge="SALE", category="Bracelets", stock=10,
         description="A classic pave tennis bracelet with a secure box clasp."),
    dict(name="Thea Baguette Studs", slug="thea-baguette-studs", price=999, compare_at_price=None,
         badge="NEW", category="Earrings", stock=25,
         description="Baguette-cut stone studs for a subtle everyday sparkle."),
    dict(name="Marlowe Rope Chain", slug="marlowe-rope-chain", price=1950, compare_at_price=None,
         badge="BESTSELLER", category="Necklaces", stock=12,
         description="A timeless rope chain in warm gold tone."),
    dict(name="Orla Signet Ring", slug="orla-signet-ring", price=1099, compare_at_price=None,
         badge="BESTSELLER", category="Rings", stock=18, sizes="5,6,7,8,9",
         description="A modern signet ring with a polished face."),
    dict(name="Elara Twisted Hoops", slug="elara-twisted-hoops", price=1299, compare_at_price=None,
         badge="NEW", category="Earrings", stock=22,
         description="Twisted hoop earrings with pearl accents."),
    dict(name="Mira Locket Pendant", slug="mira-locket-pendant", price=1499, compare_at_price=None,
         badge="", category="Necklaces", stock=9,
         description="A keepsake locket pendant on a fine chain."),
    dict(name="Iris Ear Cuff", slug="iris-ear-cuff", price=799, compare_at_price=None,
         badge="NEW", category="Earrings", stock=30,
         description="A no-piercing-needed ear cuff with crystal cluster detail."),
    dict(name="Vesper Cuff Bracelet", slug="vesper-cuff-bracelet", price=1799, compare_at_price=None,
         badge="", category="Bracelets", stock=5,
         description="An open cuff bracelet with a brushed gold finish."),
]

for p in products:
    existing = db.query(models.Product).filter(models.Product.slug == p["slug"]).first()
    if existing:
        # Product already exists — just backfill sizes if it was added later
        if p.get("sizes") and not existing.sizes:
            existing.sizes = p["sizes"]
        continue
    category = cat_objs[p.pop("category")]
    db.add(models.Product(category_id=category.id, image_url="", is_active=True, **p))

db.commit()

# --- Default banner (matches "The Festive Edit" hero) ---
if not db.query(models.Banner).first():
    db.add(models.Banner(
        title="The Festive Edit",
        subtitle="Jewellery for moments worth dressing up for.",
        eyebrow="Seasonal Edit",
        image_url="",
        link_url="shop.html",
        button_text="Explore the Edit",
        is_active=True,
        sort_order=0,
    ))

# --- Default CMS / Settings / SEO content ---
default_content = {
    "cms_footer_text": "© 2026 Focus. Developed by De Prudent Store Designer.",
    "cms_about_text": "Focus is a fine jewellery label for everyday moments worth dressing up for.",
    "setting_store_name": "Focus",
    "setting_support_email": "deprudentstoredesigner@gmail.com",
    "setting_support_phone": "0916 230 6809",
    "setting_currency_symbol": "₹",
    "setting_low_stock_threshold": "10",
    "seo_home_title": "Focus — Fine Jewellery",
    "seo_home_description": "Shop necklaces, earrings, rings and bracelets at Focus.",
    "seo_shop_title": "New Arrivals — Focus",
    "seo_shop_description": "Browse the latest jewellery arrivals at Focus.",
}
for key, value in default_content.items():
    if not db.query(models.SiteContent).filter(models.SiteContent.key == key).first():
        db.add(models.SiteContent(key=key, value=value))

# --- Sample coupon ---
if not db.query(models.Coupon).filter(models.Coupon.code == "WELCOME10").first():
    db.add(models.Coupon(code="WELCOME10", discount_percent=10, is_active=True))

db.commit()
db.close()
print("Seed complete.")
