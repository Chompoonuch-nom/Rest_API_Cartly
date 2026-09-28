from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.deps import get_current_user
from core.exceptions import BadRequestException, ResourceNotFoundException
from database import get_db
from models.models import Cart, CartItem, Product, User
from schemas.schemas import CartItemCreate, CartOut, ApiResponse

router = APIRouter(prefix="/api/cart", tags=["Cart"])

def _get_cart(db: Session, user_id: int) -> Cart:
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        raise ResourceNotFoundException("ไม่พบตระกร้าของผู้ใช้นี้")
    return cart


@router.get("", response_model=ApiResponse[CartOut])
def get_my_cart(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cart = _get_cart(db, current_user.user_id)
    return ApiResponse(data=cart)


@router.post("/items", response_model=ApiResponse[CartOut])
def add_item(paylode: CartItemCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cart = _get_cart(db, current_user.user_id)
    product = db.query(Product).filter(Product.product_id == paylode.product_id).first()
    if not product:
        raise ResourceNotFoundException(f"ไม่พบสินค้า id={paylode.product_id}")
    
    if product.stock_qty < paylode.quantity:
        raise BadRequestException("สินค้าคงเหลือไม่เพียงพอ")
    
    existing = db.query(CartItem).filter(
        CartItem.cart_id == cart.cart_id, CartItem.product_id == paylode.product_id
    ).first()

    if existing:
        existing.quantity += paylode.quantity
    else:
        db.add(CartItem(cart_id=cart.cart_id, product_id=paylode.product_id, quantity=paylode.quantity))

    db.commit()
    return ApiResponse(message="เพิ่มสินค้าลงบนตระกร้าสำเร็จ", data=_get_cart(db, current_user.user_id))


@router.put("/items/{cart_item_id}", response_model=ApiResponse[CartOut])
def update_item(
    cart_item_id: int, quantity: int,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    cart = _get_cart(db, current_user.user_id)
    item = db.query(CartItem).filter(CartItem.cart_item_id == cart_item_id).first()

    if not item:
        raise ResourceNotFoundException("ไม่พบร้านการสินค้าในตระกร้า")
    if item.cart_id != cart.cart_id:
        raise BadRequestException("รายการนี้ไม่ได้อยู่ในตระกร้าของคุณ")
    
    if quantity <= 0:
        db.delete(item)
    else:
        item.quantity = quantity

    db.commit()
    return ApiResponse(data=_get_cart(db, current_user.user_id))


@router.delete("/items/{cart_item_id}", response_model=ApiResponse[CartOut])
def remove_item(cart_item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cart = _get_cart(db, current_user.user_id)
    item = db.query(CartItem).filter(CartItem.cart_item_id == cart_item_id).first()

    if not item:
        raise ResourceNotFoundException("ไม่พบรายการสินค้าในตระกร้า")
    if item.cart_id != cart.cart_id:
        raise BadRequestException("รายการนี้ไม่ได้อยู่ในตระกร้าของคุณ")
    
    db.delete(item)
    db.commit()
    return ApiResponse(data=_get_cart(db, current_user.user_id))


@router.delete("", response_model=ApiResponse)
def clear_cart(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cart = _get_cart(db, current_user.user_id)
    db.query(CartItem).filter(CartItem.cart_id == cart.cart_id).delete()
    db.commit()
    return ApiResponse(message="ล้างตระกร้าสำเร็จ")