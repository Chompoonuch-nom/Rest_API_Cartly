from fastapi import APIRouter, Depends

from core.deps import get_current_user
from models.models import User
from schemas.schemas import UserOut, ApiResponse

router = APIRouter(prefix="/api/users", tags=["User"])

@router.get("/me", response_model=ApiResponse[UserOut])
def get_my_profile(current_user: User = Depends(get_current_user)):
    return ApiResponse(data=current_user)