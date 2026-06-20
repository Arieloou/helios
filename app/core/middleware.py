# core/middleware.py
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.security import decode_access_token
from app.core.schemas import CurrentUser
from app.core.context import current_user_ctx, request_id_ctx

class AuditContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id_ctx.set(str(uuid.uuid4()))

        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                payload = decode_access_token(auth_header.split(" ", 1)[1])
                current_user_ctx.set(CurrentUser(
                    id=payload.get("sub"),
                    email=payload.get("email", ""),
                    roles=payload.get("roles", []),
                ))
            except Exception:
                current_user_ctx.set(None)

        return await call_next(request)