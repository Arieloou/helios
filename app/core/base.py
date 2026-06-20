from datetime import datetime
from sqlalchemy import DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Base Model structure for all models in the application
class Base(DeclarativeBase):
    pass

class TimestampMixin:
    """
    Mixin para agregar automáticamente las fechas de creación y actualización
    a cualquier modelo que lo herede.
    """
    
    # Usamos Mapped[datetime] para que Python sepa exactamente qué tipo de dato es.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=func.now(), # func.now() le dice a PostgreSQL que use su propia hora
        nullable=False
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=func.now(), 
        onupdate=func.now(), # Se actualiza automáticamente cuando modificas el registro
        nullable=False
    )