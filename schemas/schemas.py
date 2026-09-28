"""
Pydantic schemas - ใช้สำหรับ validate request body และกำหนดรูปแบบ response
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Generic, TypeVar

from pydantic import BaseModel, EmailStr, Field, ConfigDict

T = TypeVar("T")

# Common
class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "OK"
    data: Optional[T] = None

class PageResponse(BaseModel, Generic[T]):
    content: List[T]
    page: int
    size: int
    total_elements: int
    total_pages: int

# Auth / User
class RegisterRequest(BaseModel):
    username: str = Field(min_length=1)
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    email: EmailStr
    password_hash: str = Field(min_length=6)
    phone_number: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    token: str
    user_id: int
    username: str
    first_name: str
    last_name: str
    email: str
    user_role:str

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    username: str
    first_name: str
    last_name: str
    email: str
    phone_number: Optional[str] = None
    avatar_url: Optional[str] = None
    user_role: str
    created_at: datetime

# Category
class CategoryCreate(BaseModel):
    category_name: str
    category_descp: Optional[str] = None
    icon_url: Optional[str] = None

class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category_id: int
    category_name: str
    category_descp: Optional[str] = None
    icon_url: Optional[str] = None

# Product
class ProductImageCreate(BaseModel):
    image_url: str
    is_primary: bool = False

class ProductImageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_img_id: int
    image_url: str
    is_primary: bool

class ProductCreate(BaseModel):
    product_name: str
    product_descp: Optional[str] = None
    price: Decimal 
    stock_qty: int = Field(ge=0)
    category_id: Optional[int] = None
    images: List[ProductImageCreate] = []

class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    product_name: str
    product_descp: Optional[str] = None
    price: Decimal
    stock_qty: int
    is_active: bool
    category_id: Optional[int] = None
    images: List[ProductImageOut] = []

# Address
class AddressCreate(BaseModel):
    label_type: Optional[str] = None
    recipient_name: str
    phone_number: str
    address_line: str
    sub_district: str
    district: str
    province: str
    postal_code: str
    is_default: bool = False

class AddressOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    address_id: int
    label_type: Optional[str] = None
    recipient_name: str
    phone_number: str
    address_line: str
    sub_district: str
    district: str
    province: str
    postal_code: str
    is_default: bool

# Cart
class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)

class CartItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    cart_item_id: int
    product: ProductOut
    quantity: int

class CartOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    cart_id: int
    items: List[CartItemOut] = []

# Order
class CheckoutRequest(BaseModel):
    address_id: int
    payment_method: str   # COD, CREDIT_CARD, PROMTPAY, TRUEMONEY

class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_item_id: int
    product_id: int
    product_name: str
    unit_price: Decimal
    quantity: int
    subtotal: Decimal

class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_id: int
    order_status: str
    total_amount: Decimal
    created_at: datetime
    items: List[OrderItemOut] = []

# Review
class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    review_comment: Optional[str] = None

class ReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    review_id: int
    user_id: int
    rating: int
    review_comment: Optional[str] = None
    created_at: datetime