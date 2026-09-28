from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.deps import get_current_user, get_current_admin
from core.exceptions import BadRequestException, ResourceNotFoundException
from database import get_db
from models.models import Order, OrderItem, Payment, Cart, CartItem, Address, User
from schemas.schemas import CheckoutRequest, OrderOut, ApiResponse

router = APIRouter(prefix="/api/orders", tags=["Order"])


@router.post("/checkout", response_model=ApiResponse[OrderOut])
def checkout(payload: CheckoutRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cart = db.query(Cart).filter(Cart.user_id == current_user.user_id).first()
    if not cart or not cart.items:
        raise BadRequestException("ตระกร้าสินค้าว่างเปล่า")
    
    address = db.query(Address).filter(Address.address_id == payload.address_id).first()
    if not address:
        raise ResourceNotFoundException("ไม่พบที่อยู่จัดส่ง")
    
    order = Order(
        user_id = current_user.user_id,
        address_id = address.address_id,
        order_status = "PENDING",
        total_amount = 0,
    )
    db.add(order)
    db.flush()  # ให้ได้ order_id ก่อน commit

    total = 0
    for cart_item in cart.items:
        product = cart_item.product

        if product.stock_qty < cart_item.quantity:
            raise BadRequestException(f"สิ้นค้า '{product.product_name}' คงเหลือไม่เพียงพอ")
        subtotal = product.price * cart_item.quantity
        total += subtotal

        db.add(OrderItem(
            order_id = order.order_id,
            product_id = product.product_id,
            product_name = product.product_name,
            unit_price = product.price,
            quantity = cart_item.quantity,
            subtotal = subtotal,
        ))

        # ตัดสต้อก
        product.stock_qty -= cart_item.quantity

    order.total_amount = total

    db.add(Payment(
        order_id = order.order_id,
        payment_method = payload.payment_method,
        payment_status = "UNPAID",
        amount = total,
    ))

    #ล้างตระกร้าหลังสั่งซื้อสำเร็จ
    db.query(CartItem).filter(CartItem.cart_id == cart.cart_id).delete()

    db.commit()
    db.refresh(order)
    return ApiResponse(message="สั่งซื้อสำเร็จ", data=order)


@router.get("", response_model=ApiResponse[List[OrderOut]])
def get_my_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    orders = (
        db.query(Order)
        .filter(Order.user_id == current_user.user_id)
        .order_by(Order.created_at.desc())
        .all()
    )
    return ApiResponse(data=orders)


@router.get("/{order_id}", response_model=ApiResponse[OrderOut])
def get_by_id(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise ResourceNotFoundException(f"ไม่พบคำสั่งซื้อ id={order_id}")
    if order.user_id != current_user.user_id:
        raise BadRequestException("คุณไม่มีสิทธิ์เข้าถึงคำสั่งซื้อ")
    return ApiResponse(data=order)


@router.put("/{order_id}/cancle", response_model=ApiResponse[OrderOut])
def cancle(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise ResourceNotFoundException(f"ไม่พบคำสั่งซื้อ id={order_id}")
    if order.user_id != current_user.user_id:
        raise BadRequestException("คุณไม่มีสิทธิ์เข้าถึงคำสั่งซื้อนี้")
    if order.order_status != "PENDING":
        raise BadRequestException("ไม่สามารถยกเลิกคำสั่งซื้อที่ดำเนินการแล้วได้")
    
    order.order_status = "CANCELLED"
    db.commit()
    db.refresh(order)
    return ApiResponse(message="ยกเลิกคำสั่งซื้อสำเร็จ", data=order)


# สำหรับฝั่ง Admin ปรับสถานะคำสั่งซื้อ เช่น SHIPPED, DELIVERED
@router.put("/{order_id}/status", response_model=ApiResponse[OrderOut])
def update_status(order_id: int, status: str, db: Session = Depends(get_db), _admin = Depends(get_current_admin)):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise ResourceNotFoundException(f"ไม่พบคำสั่งซื้อ id={order_id}")
    order.order_status = status
    db.commit()
    db.refresh(order)
    return ApiResponse(message = "อัปเดตสถานะสำเร็จ", data=order)