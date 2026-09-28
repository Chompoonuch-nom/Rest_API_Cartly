"""
FastAPI dependencies - ดึง current user จาก JWT token ใน header Authorization
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from core.security import decode_access_token
from database import get_db
from models.models import User

bearer_scheme = HTTPBearer()

def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UnAUTHOIZED,
            detail="Token ไม่ถูกต้องหรือหมดอายุ"
        )
    
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ไม่พบผู้ใช้จาก token นี้"
        )
    return user


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.user_role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ต้องเป็นผู้ดูแลระบบ (ADMIN) เท่านั้น"
        )
    return current_user