# core/context.py

from contextvars import ContextVar
from app.core.schemas import CurrentUser

request_id_ctx: ContextVar[str | None] = ContextVar("request_id_ctx", default=None)