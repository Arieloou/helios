from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
import uuid

from .base import db


class AssessmentStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    CLOSED = "closed"


class Assessment(db.Model):
    __tablename__ = "assessments"

    # Encrypted fields: middleware will auto-encrypt/decrypt these
    __encrypted_fields__ = ["name", "description"]

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    period = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(20), default=AssessmentStatus.ACTIVE.value)
    created_by = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=True)
    closed_at = db.Column(db.DateTime, nullable=True)

    _instances: Dict[str, "Assessment"] = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.id:
            self._instances[self.id] = self

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "period": self.period,
            "status": self.status,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
        }

    @classmethod
    def get_by_id(cls, id: str) -> Optional["Assessment"]:
        if id in cls._instances:
            return cls._instances[id]
        return cls.query.get(id)

    @classmethod
    def get_by_name(cls, name: str) -> Optional["Assessment"]:
        return cls.query.filter_by(name=name).first()

    @classmethod
    def get_all(cls) -> List["Assessment"]:
        return cls.query.all()

    @classmethod
    def get_active(cls) -> List["Assessment"]:
        return cls.query.filter_by(status=AssessmentStatus.ACTIVE.value).all()

    @classmethod
    def create(
        cls,
        name: str,
        description: str,
        period: str,
        created_by: Optional[str] = None,
    ) -> "Assessment":
        if cls.get_by_name(name):
            raise ValueError(f"Ya existe una evaluación con el nombre '{name}'")
        assessment = cls(
            name=name,
            description=description,
            period=period,
            status=AssessmentStatus.ACTIVE.value,
            created_by=created_by,
        )
        db.session.add(assessment)
        db.session.commit()
        return assessment

    def update(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        period: Optional[str] = None,
    ) -> None:
        if name is not None and name != self.name:
            existing = self.get_by_name(name)
            if existing and existing.id != self.id:
                raise ValueError(f"Ya existe una evaluación con el nombre '{name}'")
            self.name = name
        if description is not None:
            self.description = description
        if period is not None:
            self.period = period
        self.updated_at = datetime.now()
        db.session.commit()

    def archive(self) -> None:
        self.status = AssessmentStatus.ARCHIVED.value
        self.updated_at = datetime.now()
        db.session.commit()

    def close(self) -> None:
        self.status = AssessmentStatus.CLOSED.value
        self.closed_at = datetime.now()
        self.updated_at = datetime.now()
        db.session.commit()

    def reopen(self) -> None:
        self.status = AssessmentStatus.ACTIVE.value
        self.closed_at = None
        self.updated_at = datetime.now()
        db.session.commit()

    def delete(self) -> None:
        if self.id in self._instances:
            del self._instances[self.id]
        db.session.delete(self)
        db.session.commit()