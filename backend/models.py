from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    slug = Column(String, unique=True, nullable=False)

    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    description = Column(Text, default="")
    price = Column(Float, nullable=False)
    compare_at_price = Column(Float, nullable=True)  # original price if on sale
    image_url = Column(String, default="")
    badge = Column(String, default="")  # NEW / SALE / BESTSELLER
    sizes = Column(String, default="")  # comma-separated, e.g. "5,6,7,8" — blank means no size variants
    stock = Column(Integer, default=0)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    category = relationship("Category", back_populates="products")


class AdminUser(Base):
    __tablename__ = "admin_users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, default="Admin User")
    role = Column(String, default="staff")  # owner / manager / staff
    is_active = Column(Boolean, default=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    admin_email = Column(String, nullable=False)
    action = Column(String, nullable=False)       # e.g. "create", "update", "delete", "login"
    entity_type = Column(String, nullable=False)  # e.g. "product", "coupon", "admin_user"
    entity_id = Column(String, nullable=True)
    details = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)


class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    customer_name = Column(String, nullable=False)
    customer_email = Column(String, nullable=False)
    shipping_address = Column(Text, default="")
    status = Column(String, default="Pending")  # Pending / Shipped / Completed / Incompleted
    total = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship("OrderItem", back_populates="order")


class Coupon(Base):
    __tablename__ = "coupons"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False)
    discount_percent = Column(Float, nullable=True)
    discount_amount = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Banner(Base):
    __tablename__ = "banners"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    subtitle = Column(String, default="")
    eyebrow = Column(String, default="")
    image_url = Column(String, default="")
    link_url = Column(String, default="")
    button_text = Column(String, default="Explore the Edit")
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class SiteContent(Base):
    """Generic key/value store — used for CMS text blocks, store Settings, and SEO meta."""
    __tablename__ = "site_content"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False)
    value = Column(Text, default="")


class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    product_name = Column(String, nullable=False)
    unit_price = Column(Float, nullable=False)
    quantity = Column(Integer, default=1)

    order = relationship("Order", back_populates="items")
