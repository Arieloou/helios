from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importamos los routers de nuestros features
from app.features.assessment.routers import router as assessment_router
from app.features.user.routers import router as user_router
from app.features.auth.routers import router as auth_router
from app.features.asset.routers import router as asset_router

# Importamos los manejadores de excepciones
from app.features.auth.exceptions_handler import EXCEPTION_HANDLERS as auth_handlers

app = FastAPI(title="Helios Backend")

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluimos las rutas y les asignamos un prefijo
app.include_router(assessment_router, prefix="/api/assessment", tags=["Evaluaciones"])
app.include_router(user_router, prefix="/api/user", tags=["Usuarios"])
app.include_router(auth_router, prefix="/api/auth", tags=["Autenticación"])
# app.include_router(asset_router, prefix="/api/assets", tags=["Activos"])
# ...

# Registro de manejadores de excepciones
ALL_EXCEPTION_HANDLERS = {**auth_handlers}
for exc_class, handler in ALL_EXCEPTION_HANDLERS.items():
    app.add_exception_handler(exc_class, handler)