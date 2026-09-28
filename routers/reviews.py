from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.deps import get_current_user
from core.exceptions import BadRequestException, ResourceNotFoundException
from database import get_db
from models.models import Review, Product, User
from schemas.schemas import ReviewCreate, ReviewOut, ApiResponse

router = APIRouter(tags=["Review"])


@router.get("/api/product/{product_id}/reviews", response_model=ApiResponse[List[ReviewOut]])
def get_by_product(product_id: int, db: Session = Depends(get_db)):
    reviews = db.query(Review).filter(Review.product_id == product_id).all()
    return ApiResponse(data=reviews)


@router.post("/api/products/{product_id}/reviews", response_model=ApiResponse[ReviewOut])
def create(product_id: int, payload: ReviewCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise ResourceNotFoundException(f"ไม่พบสินค้า id={product_id}")
        
    review = Review(
        product_id = product_id,
        user_id=current_user.user_id,
        rating=payload.rating,
        review_comment=payload.review_comment,
    )
    db.add(review)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise BadRequestException("คุณได้รีวิวสินค้านี้ไปแล้ว")
    
    db.refresh(review)
    return ApiResponse(message="เพิ่มรีวิวสินค้าสำเร็จ", data=review)


@router.delete("/api/reviews/{review_id}", response_model=ApiResponse)
def delete(review_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    review = db.query(Review).filter(Review.review_id == review_id).first()
    if not review:
        raise ResourceNotFoundException(f"ไม่พบรีวิว id={review_id}")
    if review.user_id != current_user.user_id:
        raise BadRequestException("คุณไม่มีสิทธิ์ลบรีวิวนี้")
    
    db.delete(review)
    db.commit()
    return ApiResponse(message="ลบรีวิวสำเร็จ")