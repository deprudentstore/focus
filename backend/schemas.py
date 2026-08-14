from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class CategoryOut(BaseModel):
    id: int
    name: str
    slug: str
    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    name: str
    slug: str
    description: str = ""
    price: float
    compare_at_price: Optional[float] = None
    image_url: str = ""
    badge: str = ""
    sizes: str = ""
    stock: int = 0
    category_id: Optional[int] = None
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    compare_at_price: Optional[float] = None
    image_url: Optional[str] = None
    badge: Optional[str] = None
    stock: Optional[int] = None
    category_id: Optional[int] = None
    is_active: Optional[bool] = None


class ProductOut(ProductBase):
    id: int
    class Config:
        from_attributes = True


class CategoryCreate(BaseModel):
    name: str
    slug: str


class CustomerOut(BaseModel):
    id: int
    name: str
    email: str
    phone: str = ""
    created_at: datetime
    class Config:
        from_attributes = True


class CouponBase(BaseModel):
    code: str
    discount_percent: Optional[float] = None
    discount_amount: Optional[float] = None
    is_active: bool = True
    expires_at: Optional[datetime] = None


class CouponCreate(CouponBase):
    pass


class CouponOut(CouponBase):
    id: int
    class Config:
        from_attributes = True


class BannerBase(BaseModel):
    title: str
    subtitle: str = ""
    eyebrow: str = ""
    image_url: str = ""
    link_url: str = ""
    button_text: str = "Explore the Edit"
    is_active: bool = True
    sort_order: int = 0


class BannerCreate(BannerBase):
    pass


class BannerOut(BannerBase):
    id: int
    class Config:
        from_attributes = True


class ContentItem(BaseModel):
    key: str
    value: str


class AdminLogin(BaseModel):
    email: EmailStr
    password: str


class AdminUserOut(BaseModel):
    id: int
    email: EmailStr
    name: str
    role: str
    is_active: bool
    class Config:
        from_attributes = True


class AdminUserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str = "Admin User"
    role: str = "staff"


class AdminUserUpdate(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None


class AuditLogOut(BaseModel):
    id: int
    admin_email: str
    action: str
    entity_type: str
    entity_id: Optional[str] = None
    details: str = ""
    created_at: datetime
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class OrderItemIn(BaseModel):
    product_id: int
    quantity: int = 1


class OrderCreate(BaseModel):
    customer_name: str
    customer_email: EmailStr
    shipping_address: str = ""
    coupon_code: Optional[str] = None
    items: List[OrderItemIn]


class OrderItemOut(BaseModel):
    product_name: str
    unit_price: float
    quantity: int
    class Config:
        from_attributes = True


class OrderOut(BaseModel):
    id: int
    order_number: str
    customer_name: str
    customer_email: str
    status: str
    total: float
    created_at: datetime
    items: List[OrderItemOut] = []
    class Config:
        from_attributes = True


class LowStockItem(BaseModel):
    id: int
    name: str
    stock: int
    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    todays_sales: float
    orders_count: int
    customers_count: int
    products_count: int
    low_stock: List[LowStockItem] = []
