from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.deps import get_current_admin
from core.exceptions import ResourceNotFoundException
from database import get_db
from models.models import Product, Category, ProductImage
from schemas.schemas import ProductCreate, ProductOut, ApiResponse, PageResponse

router = APIRouter(prefix="/api/products", tags=["Product"])

@router.get("", response_model=ApiResponse[PageResponse[ProductOut]])
def get_all(
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1, le=100),
    category_id: Optional[int] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Product).filter(Product.is_active.is_(True))

    if keyword:
        query = query.filter(Product).filter(Product.product_name.ilike(f"%{keyword}%"))
    elif category_id:
        query = query.filter(Product.category_id == category_id)

    total = query.count()
    items = query.offset(page * size).limit(size).all()
    total_pages = (total + size - 1) // size if size else 0

    data = PageResponse(
        content=items, page=page, size=size,
        total_elements=total, total_pages=total_pages,
    )
    return ApiResponse(data=data)


@router.get("/{product_id}", response_model=ApiResponse[ProductOut])
def get_by_id(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise ResourceNotFoundException(f"ไม่พบสินค้า id={product_id}")
    return ApiResponse(data=product)


@router.post("", response_model=ApiResponse[ProductOut])
def create(payload: ProductCreate, db: Session = Depends(get_db), _admin=Depends(get_current_admin)):
    if payload.category_id:
        category = db.query(Category).filter(Category.category_id == payload.category_id).first()
        if not category:
            raise ResourceNotFoundException(f"ไม่พบหมวดหมู่ id={payload.category_id}")
        
        product = Product(
            product_name=payload.product_name,
            product_descp=payload.product_descp,
            price=payload.price,
            stock_qty=payload.stock_qty,
            category_id=payload.category_id,
            is_active=True,
        )
        db.add(product)
        db.flush() # ให้ได้ product_id ก่อน commit

        for img in paylode.images:
            db.add(ProductImage(product_id=product.product_id, image_url=img.image_url, is_primary=img.is_primary))

        db.commit()
        db.refresh(product)
        return ApiResponse(message="เพิ่มสินค้าสำเร็จ", data=product)
    

@router.put("/{product_id}", response_model=ApiResponse[ProductOut])
def update(product_id: int, payload: ProductCreate, db: Session = Depends(get_db), _admin=Depends(get_current_admin)):
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise ResourceNotFoundException(f"ไม่พบสินค้า id={product_id}")
    
    if payload.category_id:
        category = db.query(Category).filter(Category.category_id == payload.category_id).first()
        if not category:
            raise ResourceNotFoundException(f"ไม่พบหมวดหมู่ id={payload.category_id}")
        
        product.product_name = payload.product_name
        product.product_descp = payload.product_descp
        product.price = payload.price
        product.stock_qty = payload.stock_qty
        product.category_id = payload.category_id

        # แทนที่รูปสินค้าทั้งหมดด้วยชุดใหม่ที่ส่งมา (ถ้ามีการส่ง images มา)
        if payload.images:
            db.query(ProductImage).filter(ProductImage.product_id == product_id).delete()
            for img in payload.images:
                db.add(ProductImage(product_id=product_id, image_url=img.image_url, is_primary=img.is_primary))
        
        db.commit()
        db.refresh(product)
        return ApiResponse(message="แก้ไขสำเร็จ", data=product)
    

@router.delete("/{product_id}", response_model=ApiResponse)
def delete(product_id: int, db: Session = Depends(get_db), _admin=Depends(get_current_admin)):
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise ResourceNotFoundException(f"ไม่พบสินค้า id={product_id}")
    product.is_active = False  # soft delete
    db.commit()
    return ApiResponse(message="ลบสินค้าสำเร็จ")


# ----Product Image
@router.post("/{product_id}/images", response_model=ApiResponse[ProductOut])
def add_image(product_id: int, image_url: str, is_primary: bool = False,
              db: Session = Depends(get_db), _admin=Depends(get_current_admin)):
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise ResourceNotFoundException(f"ไม่พบสินค้า id={product_id}")
    
    if is_primary:
        db.query(ProductImage).filter(ProductImage.product_id == product_id).update({"is_primary": False})

    db.add(ProductImage(product_id=product_id, image_url=image_url, is_primary=is_primary))
    db.commit()
    db.refresh(product)
    return ApiResponse(message="เพิ่มรูปสินค้าสำเร็จ", data=product)


@router.delete("/{product_id}/images/{product_img_id}", response_model=ApiResponse)
def delete_image(product_id: int, product_img_id: int, db: Session = Depends(get_db), _admin=Depends(get_current_admin)):
    image = db.query(ProductImage).filter(
        ProductImage.product_img_id == product_img_id, ProductImage.product_id == product_id
    ).first()
    if not image:
        raise ResourceNotFoundException("ไม่พบรูปภาพนี้")
    db.delete(image)
    db.commit()
    return ApiResponse(message="ลบรูปสินค้าสำเร็จ")