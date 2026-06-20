# features/assessment/routers.py
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
    data: AssessmentCreate, # 1. Pydantic valida el JSON de React
    current_user = Depends(get_current_user), # 2. FastAPI extrae el usuario actual
    service: AssessmentService = Depends(get_assessment_service) # 3. Inyectamos el servicio
):
    try:
        # 4. Le pasamos todo al servicio
        # Asumiendo que tu current_user tiene un atributo .id o .username
        assessment = await service.create(data=data, current_user_id=current_user.id)
        return assessment
        
    except ValueError as e:
        # Si el servicio lanza un error (ej. nombre duplicado), devolvemos un 400
        raise HTTPException(status_code=400, detail=str(e))