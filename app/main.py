from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importamos los routers de nuestros features
from app.features.assessment.routers import router as assessment_router
from app.features.asset.routers import router as asset_router
# ...

app = FastAPI(title="Mi API Feature-Based")

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluimos las rutas y les asignamos un prefijo
app.include_router(assessment_router, prefix="/api/assessment", tags=["Evaluaciones"])
# app.include_router(asset_router, prefix="/api/assets", tags=["Activos"])
# ...