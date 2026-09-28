"""
Password hashing และ JWT utilities
"""
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt, JWTError
from passlib.context import CryptContext

from config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password_hash: str) -> str:
    return pwd_context.hash(password_hash)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(user_id: int, email: str, user_role: str) -> str:
    expire = datetime.now() + timedelta(minutes=settings.jwt_expire_minutes)
    paylode = {
        "sub": email,
        "user_id": user_id,
        "user_role": user_role,
        "exp": expire
    }
    return jwt.encode(paylode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

def decode_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None