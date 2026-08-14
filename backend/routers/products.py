from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
import models, schemas

router = APIRouter(prefix="/api", tags=["storefront"])


@router.get("/categories", response_model=List[schemas.CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).all()


@router.get("/products", response_model=List[schemas.ProductOut])
def list_products(category: Optional[str] = None, badge: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(models.Product).filter(models.Product.is_active == True)
    if category:
        q = q.join(models.Category).filter(models.Category.slug == category)
    if badge:
        q = q.filter(models.Product.badge == badge)
    return q.order_by(models.Product.created_at.desc()).all()


@router.get("/products/{slug}", response_model=schemas.ProductOut)
def get_product(slug: str, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.slug == slug).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/banners", response_model=List[schemas.BannerOut])
def list_banners(db: Session = Depends(get_db)):
    return (
        db.query(models.Banner)
        .filter(models.Banner.is_active == True)
        .order_by(models.Banner.sort_order.asc())
        .all()
    )


@router.get("/content/{key}", response_model=schemas.ContentItem)
def get_content(key: str, db: Session = Depends(get_db)):
    item = db.query(models.SiteContent).filter(models.SiteContent.key == key).first()
    if not item:
        return schemas.ContentItem(key=key, value="")
    return schemas.ContentItem(key=item.key, value=item.value)


@router.get("/content", response_model=List[schemas.ContentItem])
def list_content(prefix: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(models.SiteContent)
    if prefix:
        q = q.filter(models.SiteContent.key.startswith(prefix))
    items = q.all()
    return [schemas.ContentItem(key=i.key, value=i.value) for i in items]
