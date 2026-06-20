from contextvars import ContextVar
from app.core.schemas import CurrentUser

current_user_ctx: ContextVar[CurrentUser | None] = ContextVar("current_user_ctx", default=None)
request_id_ctx: ContextVar[str | None] = ContextVar("request_id_ctx", default=None)