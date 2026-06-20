# features/user/models/user.py

from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
import uuid

from core import Base, TimestampMixin

class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    failed_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    locked_until: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Model relationships
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    