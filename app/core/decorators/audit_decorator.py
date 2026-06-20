# core/audit_decorator.py
import time, functools
from app.core.context import current_user_ctx, request_id_ctx
from app.features.audit.service import save_audit_log

def audit(action: str):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.perf_counter()
            user = current_user_ctx.get()
            status, error = "SUCCESS", None
            try:
                return await func(*args, **kwargs)
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
                    duration_ms=int((time.perf_counter() - start) * 1000),
                )
        return wrapper
    return decorator