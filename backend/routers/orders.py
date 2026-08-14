import random, string
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
import models, schemas

router = APIRouter(prefix="/api/orders", tags=["orders"])


def generate_order_number():
    return "IM-" + "".join(random.choices(string.digits, k=4))


@router.post("/", response_model=schemas.OrderOut)
def create_order(payload: schemas.OrderCreate, db: Session = Depends(get_db)):
    # Find or create the customer record so admin "Customers" stat is accurate
    customer = db.query(models.Customer).filter(models.Customer.email == payload.customer_email).first()
    if not customer:
        customer = models.Customer(name=payload.customer_name, email=payload.customer_email)
        db.add(customer)
        db.flush()

    total = 0.0
    order_items = []
    for item in payload.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Not enough stock for {product.name}")
        line_total = product.price * item.quantity
        total += line_total
        product.stock -= item.quantity
        order_items.append(models.OrderItem(
            product_id=product.id,
            product_name=product.name,
            unit_price=product.price,
            quantity=item.quantity,
        ))

    # Apply coupon if provided and valid
    if payload.coupon_code:
        coupon = db.query(models.Coupon).filter(
            models.Coupon.code == payload.coupon_code.strip().upper(),
            models.Coupon.is_active == True,
        ).first()
        if coupon and (not coupon.expires_at or coupon.expires_at > datetime.utcnow()):
            if coupon.discount_percent:
                total -= total * (coupon.discount_percent / 100)
            elif coupon.discount_amount:
                total -= coupon.discount_amount
            total = max(total, 0)

    order = models.Order(
        order_number=generate_order_number(),
        customer_id=customer.id,
        customer_name=payload.customer_name,
        customer_email=payload.customer_email,
        shipping_address=payload.shipping_address,
        status="Pending",
        total=total,
    )
    order.items = order_items
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.get("/{order_number}", response_model=schemas.OrderOut)
def get_order(order_number: str, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.order_number == order_number).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
