# features/assessment/routers/assessment_router.py

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
    data: AssessmentCreate, # pydantic valida el JSON de React
    current_user = Depends(get_current_user),
    assessment_service: AssessmentService = Depends(get_assessment_service)
):
    try:
        assessment = await assessment_service.create_assessment(assessment=data, current_user_id=current_user.id)
        return assessment        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))