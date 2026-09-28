from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.deps import get_current_admin
from core.exceptions import ResourceNotFoundException
from database import get_db
from models.models import Category
from schemas.schemas import CategoryCreate, CategoryOut, ApiResponse

router = APIRouter(prefix="/api/categories", tags=["Category"])


@router.get("", response_model=ApiResponse[List[CategoryOut]])
def get_all(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    return ApiResponse(data=categories)


@router.get("/{category_id}", response_model=ApiResponse[CategoryOut])
def get_by_id(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.category_id == category_id).first()
    if not category:
        raise ResourceNotFoundException(f"ไม่พบหมวดหมู่ id={category_id}")
    return ApiResponse(data=category)


@router.post("", response_model=ApiResponse[CategoryOut])
def create(payload: CategoryCreate, db: Session = Depends(get_db), _admin=Depends(get_current_admin)):
    category = Category(**payload.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return ApiResponse(message="สร้างหมวดหมู่สำเร็จ", data=category)


@router.put("/{category_id}", response_model=ApiResponse[CategoryOut])
def update(category_id: int, payload: CategoryCreate, db: Session = Depends(get_db), _admin=Depends(get_current_admin)):
    category = db.query(Category).filter(Category.category_id == category_id).first()
    if not category:
        raise ResourceNotFoundException(f"ไม่พบหมวดหมู่ id={category_id}")
    for key, value in payload.model_dump().items():
        setattr (category, key, value)
    db.commit()
    db.refresh(category)
    return ApiResponse(message="แก้ไขหมวดหมู่สำเร็จ", data=category) 


@router.delete("/{category_id}", response_model=ApiResponse)
def delete(category_id: int, db: Session = Depends(get_db), _admin=Depends(get_current_admin)):
    category = db.query(Category).filter(Category.category_id == category_id).first()
    if not category:
        raise ResourceNotFoundException(f"ไม่พบหมวดหมู่ id={category_id}")
    db.delete(category)
    db.commit()
    return ApiResponse(message="ลบหมวดหมู่สำเร็จ")