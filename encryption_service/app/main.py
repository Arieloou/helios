"""
Punto de entrada de la aplicación FastAPI del servicio de cifrado.

Arranca el servidor gRPC en un hilo separado durante el startup
de FastAPI, y lo detiene limpiamente durante el shutdown.
También expone endpoints REST para health check y debug.
"""

import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.config import settings
from app.crypto.aes_cipher import AESCipher
from app.grpc_server.server import GRPCServer


# ---------------------------------------------------------------------------
# Inicialización de componentes
# ---------------------------------------------------------------------------

# Obtener clave de cifrado y crear cipher
key_bytes = settings.get_key_bytes()
cipher = AESCipher(key_bytes)

# Crear servidor gRPC
grpc_server = GRPCServer(port=settings.GRPC_PORT, cipher=cipher)


# ---------------------------------------------------------------------------
# Lifecycle de FastAPI (startup / shutdown)
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestiona el ciclo de vida del servidor gRPC junto con FastAPI."""
    # --- STARTUP ---
    grpc_thread = threading.Thread(
        target=_start_grpc,
        daemon=True,
        name="grpc-server-thread",
    )
    grpc_thread.start()

    print(f"[FastAPI] Servicio de cifrado iniciado")
    print(f"    ├── REST API:  http://0.0.0.0:{settings.API_PORT}")
    print(f"    └── gRPC:      localhost:{settings.GRPC_PORT}")

    yield

    # --- SHUTDOWN ---
    print("[FastAPI] Deteniendo servicio de cifrado...")
    grpc_server.stop(grace=5)


def _start_grpc():
    """Arranca el servidor gRPC (se ejecuta en un hilo separado)."""
    grpc_server.start()
    grpc_server.wait_for_termination()


# ---------------------------------------------------------------------------
# Aplicación FastAPI
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Helios Encryption Service",
    description=(
        "Servicio de cifrado/descifrado AES-256-GCM para el ecosistema Helios. "
        "El protocolo principal de comunicación es gRPC (puerto configurable). "
        "Esta API REST expone endpoints de salud y debug."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Modelos Pydantic para los endpoints REST (debug)
# ---------------------------------------------------------------------------

class EncryptRequestModel(BaseModel):
    """Modelo de solicitud de cifrado."""
    plaintext: str


class EncryptResponseModel(BaseModel):
    """Modelo de respuesta de cifrado."""
    ciphertext: str
    success: bool
    message: str


class DecryptRequestModel(BaseModel):
    """Modelo de solicitud de descifrado."""
    ciphertext: str


class DecryptResponseModel(BaseModel):
    """Modelo de respuesta de descifrado."""
    plaintext: str
    success: bool
    message: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health", tags=["Sistema"])
async def health_check():
    """
    Endpoint de salud del servicio.
    Verifica que el servicio esté corriendo y el servidor gRPC activo.
    """
    return {
        "status": "ok",
        "service": "encryption_service",
        "grpc_port": settings.GRPC_PORT,
        "encryption_algorithm": "AES-256-GCM",
    }


@app.post("/encrypt", response_model=EncryptResponseModel, tags=["Cifrado (Debug)"])
async def encrypt_endpoint(request: EncryptRequestModel):
    """
    Cifra texto plano (endpoint REST para debug/testing).
    En producción, usar el endpoint gRPC.
    """
    try:
        ciphertext = cipher.encrypt(request.plaintext)
        return EncryptResponseModel(
            ciphertext=ciphertext,
            success=True,
            message="Cifrado exitoso.",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@app.post("/decrypt", response_model=DecryptResponseModel, tags=["Cifrado (Debug)"])
async def decrypt_endpoint(request: DecryptRequestModel):
    """
    Descifra texto cifrado en Base64 (endpoint REST para debug/testing).
    En producción, usar el endpoint gRPC.
    """
    try:
        plaintext = cipher.decrypt(request.ciphertext)
        return DecryptResponseModel(
            plaintext=plaintext,
            success=True,
            message="Descifrado exitoso.",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
