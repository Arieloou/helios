# core/audit_decorator.py

import time, functools
from app.core.context import current_user_ctx, request_id_ctx
from app.features.audit.service import save_audit_log

from app.core.schemas import CurrentUser

def _extract_current_user(args, kwargs) -> CurrentUser | None:
    for value in (*args, *kwargs.values()):
        if isinstance(value, CurrentUser):
            return value
    return None 

def audit(action: str):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.perf_counter()
            user = _extract_current_user(args, kwargs) or current_user_ctx.get()
            status, error = "SUCCESS", None
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status, error = "FAILURE", str(e)
                raise
            finally:
                await save_audit_log(
                    action=action,
                    user_id=user.id if user else None,
                    request_id=request_id_ctx.get(),
                    status=status,
                    error=error,
                    resource_id=getattr(result, "id", None),  # útil: queda el id del Objeto creado
                    duration_ms=int((time.perf_counter() - start) * 1000),
                )
        return wrapper
    return decorator