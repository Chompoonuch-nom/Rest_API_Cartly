from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.deps import get_current_user
from core.exceptions import BadRequestException, ResourceNotFoundException
from database import get_db
from models.models import Address, User
from schemas.schemas import AddressCreate, AddressOut, ApiResponse

router = APIRouter(prefix="/api/address", tags=["Address"])

def _get_owned_address(db: Session, user_id: int, address_id: int) -> Address:
    address = db.query(Address).filter(Address.address_id == address_id).first()
    if not address:
        raise ResourceNotFoundException(f"ไม่พบที่อยู่ id={address_id}")
    if address.user_id != user_id:
        raise BadRequestException("คุณไม่มีสิทธิ์เข้าถึงที่อยู่นี้")
    return address


@router.get("", response_model=ApiResponse[List[AddressOut]])
def get_my_addresses(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    addresses = db.query(Address).filter(Address.user_id == current_user.user_id).all()
    return ApiResponse(data=addresses)


@router.post("",response_model=ApiResponse[AddressOut])
def create(payload: AddressCreate, db:Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    address = Address(**payload.model_dump(), user_id=current_user.user_id)
    db.add(address)
    db.commit()
    db.refresh(address)
    return ApiResponse(message="เพิ่มที่อยู่สำเร็จ", data=address)


@router.put("/{address_id}", response_model=ApiResponse[AddressOut])
def update(address_id: int, payload: AddressCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    address = _get_owned_address(db, current_user.user_id, address_id)
    for key, value in payload.model_dump().items():
        setattr(address, key, value)
    db.commit()
    db.refresh(address)
    return ApiResponse(message="แก้ไขที่อยู่สำเร็จ", data=address)


@router.delete("/{address_id}", response_model=ApiResponse)
def delete(address_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    address = _get_owned_address(db, current_user.user_id, address_id)
    db.delete(address)
    db.commit()
    return ApiResponse(message="ลบที่อยู่สำเร็จ")