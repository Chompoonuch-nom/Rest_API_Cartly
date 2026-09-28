from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import traceback
from core.exceptions import BadRequestException
from core.security import hash_password, verify_password, create_access_token
from database import get_db
from models.models import User, Cart
from schemas.schemas import RegisterRequest, LoginRequest, AuthResponse, ApiResponse

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/register", response_model=ApiResponse[AuthResponse])
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    print (payload)
    try:
        if db.query(User).filter(User.email == payload.email).first():
            raise BadRequestException("Email นี้ถูกใช้งานแล้ว")
        
        user = User(
            username=payload.username,
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=payload.email,
            password_hash=hash_password(payload.password_hash),
            phone_number=payload.phone_number,
            user_role="CUSTOMER",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # สร้างตระกร้าว่างให้ผู้ใช้ใหม่ทันที
        cart = Cart(user_id=user.user_id)
        db.add(cart)
        db.commit()

        token = create_access_token(user.user_id, user.email, user.user_role)
        data = AuthResponse(
            token=token, user_id=user.user_id, username=user.username,
            first_name=user.first_name, last_name=user.last_name,
            email=user.email, user_role=user.user_role,
        )
    except Exception as e:
        print("__________________",e)
        traceback.print_exc()
    return ApiResponse(message="Sign-Up Successfully", data=data)

@router.post("/login", response_model=ApiResponse[AuthResponse])
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    if not user or not verify_password(payload.password, user.password_hash):
        raise BadRequestException("Invalid email or password")
    
    token = create_access_token(user.user_id, user.email, user.user_role)
    data = AuthResponse(
        token=token, user_id=user.user_id, username=user.username,
        first_name=user.first_name, last_name=user.last_name,
        email=user.email, user_role=user.user_role,
    )
    return ApiResponse(message="Login Successfully", data=data)