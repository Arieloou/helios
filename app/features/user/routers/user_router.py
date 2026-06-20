# features/user/routers/user_router.py

from fastapi import APIRouter, Depends, HTTPException, Response, Request, status

# Dependency of core feature
from app.core.dependencies import require_role
from app.core.schemas import UserRole

# Dependency of assessment feature
from ..dependencies import get_user_service
from ..schemas import UserCreate, UserResponse
from ..services import UserService
from ..exceptions import *

router = APIRouter()

@router.post("/create", response_model=UserResponse)
async def create_user(
    data: UserCreate,
    
    # Inyects the user schema defined in core/schemas.py, and also validates if the user has the correct role
    current_user = Depends(require_role(UserRole.ADMIN)), 
    user_service: UserService = Depends(get_user_service)
):
    try:
        user = await user_service.create_user(data=data, current_user_id=current_user.id)
        return user
        
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))