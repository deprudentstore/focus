from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from database import get_db
import models, schemas
from auth import verify_password, hash_password, create_access_token, get_current_admin, require_role, ROLE_LEVELS

router = APIRouter(prefix="/api/admin", tags=["admin"])


def log_action(db: Session, admin: models.AdminUser, action: str, entity_type: str, entity_id=None, details: str = ""):
    db.add(models.AuditLog(
        admin_email=admin.email,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id is not None else None,
        details=details,
    ))
    db.commit()


@router.post("/login", response_model=schemas.Token)
def login(payload: schemas.AdminLogin, db: Session = Depends(get_db)):
    admin = db.query(models.AdminUser).filter(models.AdminUser.email == payload.email).first()
    if not admin or not verify_password(payload.password, admin.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not admin.is_active:
        raise HTTPException(status_code=403, detail="This admin account has been deactivated")
    token = create_access_token({"sub": admin.email})
    log_action(db, admin, "login", "admin_user", admin.id)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.AdminUserOut)
def me(admin=Depends(get_current_admin)):
    return admin


@router.get("/dashboard", response_model=schemas.DashboardStats)
def dashboard(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    todays_sales = db.query(func.coalesce(func.sum(models.Order.total), 0.0)).filter(
        models.Order.created_at >= today_start
    ).scalar()
    orders_count = db.query(func.count(models.Order.id)).scalar()
    customers_count = db.query(func.count(models.Customer.id)).scalar()
    products_count = db.query(func.count(models.Product.id)).scalar()

    threshold_setting = db.query(models.SiteContent).filter(models.SiteContent.key == "setting_low_stock_threshold").first()
    try:
        LOW_STOCK_THRESHOLD = int(threshold_setting.value) if threshold_setting and threshold_setting.value else 10
    except ValueError:
        LOW_STOCK_THRESHOLD = 10

    low_stock_products = (
        db.query(models.Product)
        .filter(models.Product.stock <= LOW_STOCK_THRESHOLD, models.Product.is_active == True)
        .order_by(models.Product.stock.asc())
        .limit(5)
        .all()
    )

    return schemas.DashboardStats(
        todays_sales=todays_sales,
        orders_count=orders_count,
        customers_count=customers_count,
        products_count=products_count,
        low_stock=low_stock_products,
    )


# --- Products (view: any admin, write: manager+) ---

@router.get("/products", response_model=List[schemas.ProductOut])
def admin_list_products(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    return db.query(models.Product).order_by(models.Product.created_at.desc()).all()


@router.post("/products", response_model=schemas.ProductOut)
def admin_create_product(payload: schemas.ProductCreate, db: Session = Depends(get_db), admin=Depends(require_role("manager"))):
    product = models.Product(**payload.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    log_action(db, admin, "create", "product", product.id, product.name)
    return product


@router.put("/products/{product_id}", response_model=schemas.ProductOut)
def admin_update_product(product_id: int, payload: schemas.ProductUpdate, db: Session = Depends(get_db), admin=Depends(require_role("manager"))):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    log_action(db, admin, "update", "product", product.id, product.name)
    return product


@router.delete("/products/{product_id}")
def admin_delete_product(product_id: int, db: Session = Depends(get_db), admin=Depends(require_role("manager"))):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    name = product.name
    db.delete(product)
    db.commit()
    log_action(db, admin, "delete", "product", product_id, name)
    return {"detail": "Product deleted"}


# --- Orders (view + status update: any admin) ---

@router.get("/orders", response_model=List[schemas.OrderOut])
def admin_list_orders(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    return db.query(models.Order).order_by(models.Order.created_at.desc()).all()


@router.put("/orders/{order_id}/status", response_model=schemas.OrderOut)
def admin_update_order_status(order_id: int, status: str, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = status
    db.commit()
    db.refresh(order)
    log_action(db, admin, "update", "order", order.id, f"status -> {status}")
    return order


# --- Categories (view: any admin, write: manager+) ---

@router.get("/categories", response_model=List[schemas.CategoryOut])
def admin_list_categories(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    return db.query(models.Category).all()


@router.post("/categories", response_model=schemas.CategoryOut)
def admin_create_category(payload: schemas.CategoryCreate, db: Session = Depends(get_db), admin=Depends(require_role("manager"))):
    if db.query(models.Category).filter(models.Category.slug == payload.slug).first():
        raise HTTPException(status_code=400, detail="A category with that slug already exists")
    category = models.Category(**payload.dict())
    db.add(category)
    db.commit()
    db.refresh(category)
    log_action(db, admin, "create", "category", category.id, category.name)
    return category


@router.delete("/categories/{category_id}")
def admin_delete_category(category_id: int, db: Session = Depends(get_db), admin=Depends(require_role("manager"))):
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    name = category.name
    db.delete(category)
    db.commit()
    log_action(db, admin, "delete", "category", category_id, name)
    return {"detail": "Category deleted"}


# --- Customers (view: any admin) ---

@router.get("/customers", response_model=List[schemas.CustomerOut])
def admin_list_customers(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    return db.query(models.Customer).order_by(models.Customer.created_at.desc()).all()


# --- Coupons (view: any admin, write: manager+) ---

@router.get("/coupons", response_model=List[schemas.CouponOut])
def admin_list_coupons(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    return db.query(models.Coupon).order_by(models.Coupon.created_at.desc()).all()


@router.post("/coupons", response_model=schemas.CouponOut)
def admin_create_coupon(payload: schemas.CouponCreate, db: Session = Depends(get_db), admin=Depends(require_role("manager"))):
    code = payload.code.strip().upper()
    if db.query(models.Coupon).filter(models.Coupon.code == code).first():
        raise HTTPException(status_code=400, detail="A coupon with that code already exists")
    data = payload.dict()
    data["code"] = code
    coupon = models.Coupon(**data)
    db.add(coupon)
    db.commit()
    db.refresh(coupon)
    log_action(db, admin, "create", "coupon", coupon.id, coupon.code)
    return coupon


@router.delete("/coupons/{coupon_id}")
def admin_delete_coupon(coupon_id: int, db: Session = Depends(get_db), admin=Depends(require_role("manager"))):
    coupon = db.query(models.Coupon).filter(models.Coupon.id == coupon_id).first()
    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")
    code = coupon.code
    db.delete(coupon)
    db.commit()
    log_action(db, admin, "delete", "coupon", coupon_id, code)
    return {"detail": "Coupon deleted"}


# --- Banners (view: any admin, write: manager+) ---

@router.get("/banners", response_model=List[schemas.BannerOut])
def admin_list_banners(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    return db.query(models.Banner).order_by(models.Banner.sort_order.asc()).all()


@router.post("/banners", response_model=schemas.BannerOut)
def admin_create_banner(payload: schemas.BannerCreate, db: Session = Depends(get_db), admin=Depends(require_role("manager"))):
    banner = models.Banner(**payload.dict())
    db.add(banner)
    db.commit()
    db.refresh(banner)
    log_action(db, admin, "create", "banner", banner.id, banner.title)
    return banner


@router.put("/banners/{banner_id}", response_model=schemas.BannerOut)
def admin_update_banner(banner_id: int, payload: schemas.BannerCreate, db: Session = Depends(get_db), admin=Depends(require_role("manager"))):
    banner = db.query(models.Banner).filter(models.Banner.id == banner_id).first()
    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")
    for field, value in payload.dict().items():
        setattr(banner, field, value)
    db.commit()
    db.refresh(banner)
    log_action(db, admin, "update", "banner", banner.id, banner.title)
    return banner


@router.delete("/banners/{banner_id}")
def admin_delete_banner(banner_id: int, db: Session = Depends(get_db), admin=Depends(require_role("manager"))):
    banner = db.query(models.Banner).filter(models.Banner.id == banner_id).first()
    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")
    title = banner.title
    db.delete(banner)
    db.commit()
    log_action(db, admin, "delete", "banner", banner_id, title)
    return {"detail": "Banner deleted"}


# --- Site Content: CMS + SEO (manager+), Settings (owner only — store-wide config) ---

@router.get("/content", response_model=List[schemas.ContentItem])
def admin_list_content(prefix: str = "", db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    q = db.query(models.SiteContent)
    if prefix:
        q = q.filter(models.SiteContent.key.startswith(prefix))
    return [schemas.ContentItem(key=i.key, value=i.value) for i in q.all()]


@router.put("/content/{key}", response_model=schemas.ContentItem)
def admin_upsert_content(key: str, payload: schemas.ContentItem, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    required_role = "owner" if key.startswith("setting_") else "manager"
    if ROLE_LEVELS.get(admin.role, 0) < ROLE_LEVELS[required_role]:
        raise HTTPException(status_code=403, detail=f"This action requires {required_role} permissions or higher.")

    item = db.query(models.SiteContent).filter(models.SiteContent.key == key).first()
    if not item:
        item = models.SiteContent(key=key, value=payload.value)
        db.add(item)
    else:
        item.value = payload.value
    db.commit()
    log_action(db, admin, "update", "site_content", key, payload.value[:100])
    return schemas.ContentItem(key=key, value=item.value)


# --- Admin user management (owner only) ---

@router.get("/admins", response_model=List[schemas.AdminUserOut])
def admin_list_admins(db: Session = Depends(get_db), admin=Depends(require_role("owner"))):
    return db.query(models.AdminUser).order_by(models.AdminUser.id.asc()).all()


@router.post("/admins", response_model=schemas.AdminUserOut)
def admin_create_admin(payload: schemas.AdminUserCreate, db: Session = Depends(get_db), admin=Depends(require_role("owner"))):
    if payload.role not in ("owner", "manager", "staff"):
        raise HTTPException(status_code=400, detail="Role must be owner, manager, or staff")
    if db.query(models.AdminUser).filter(models.AdminUser.email == payload.email).first():
        raise HTTPException(status_code=400, detail="An admin with that email already exists")
    new_admin = models.AdminUser(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        name=payload.name,
        role=payload.role,
        is_active=True,
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    log_action(db, admin, "create", "admin_user", new_admin.id, f"{new_admin.email} ({new_admin.role})")
    return new_admin


@router.put("/admins/{admin_id}", response_model=schemas.AdminUserOut)
def admin_update_admin(admin_id: int, payload: schemas.AdminUserUpdate, db: Session = Depends(get_db), admin=Depends(require_role("owner"))):
    target = db.query(models.AdminUser).filter(models.AdminUser.id == admin_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Admin user not found")
    if payload.role is not None:
        if payload.role not in ("owner", "manager", "staff"):
            raise HTTPException(status_code=400, detail="Role must be owner, manager, or staff")
        target.role = payload.role
    if payload.is_active is not None:
        target.is_active = payload.is_active
    db.commit()
    db.refresh(target)
    log_action(db, admin, "update", "admin_user", target.id, f"role={target.role}, active={target.is_active}")
    return target


@router.delete("/admins/{admin_id}")
def admin_delete_admin(admin_id: int, db: Session = Depends(get_db), admin=Depends(require_role("owner"))):
    if admin_id == admin.id:
        raise HTTPException(status_code=400, detail="You can't delete your own account")
    target = db.query(models.AdminUser).filter(models.AdminUser.id == admin_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Admin user not found")
    email = target.email
    db.delete(target)
    db.commit()
    log_action(db, admin, "delete", "admin_user", admin_id, email)
    return {"detail": "Admin user deleted"}


# --- Audit log (manager+) ---

@router.get("/audit-log", response_model=List[schemas.AuditLogOut])
def admin_audit_log(limit: int = 100, db: Session = Depends(get_db), admin=Depends(require_role("manager"))):
    return db.query(models.AuditLog).order_by(models.AuditLog.created_at.desc()).limit(limit).all()
