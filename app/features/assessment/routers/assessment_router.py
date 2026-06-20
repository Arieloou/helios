from fastapi import APIRouter, Depends, HTTPException
from ..schemas import AssessmentCreate, AssessmentResponse
from ..services import AssessmentService

# Dependency of core feature
from app.core.dependencies import get_current_user

# Dependency of assessment feature
from ..dependencies import get_assessment_service

router = APIRouter()

@router.post("/create", response_model=AssessmentResponse)
async def create_assessment(
    data: AssessmentCreate, # ydantic valida el JSON de React
    current_user = Depends(get_current_user),
    service: AssessmentService = Depends(get_assessment_service)
):
    try:
        assessment = await service.create(data=data, current_user_id=current_user.id)
        return assessment
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))