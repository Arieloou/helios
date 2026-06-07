from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
import uuid


class AssessmentStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    CLOSED = "closed"


class Assessment:
    _instances: Dict[str, "Assessment"] = {}

    def __init__(
        self,
        id: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        period: Optional[str] = None,
        status: AssessmentStatus = AssessmentStatus.ACTIVE,
        created_by: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        closed_at: Optional[datetime] = None,
    ):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.period = period
        self.status = status
        self.created_by = created_by
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at
        self.closed_at = closed_at

        self._instances[self.id] = self

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "period": self.period,
            "status": self.status.value,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
        }

    @classmethod
    def get_by_id(cls, id: str) -> Optional["Assessment"]:
        return cls._instances.get(id)

    @classmethod
    def get_by_name(cls, name: str) -> Optional["Assessment"]:
        for assessment in cls._instances.values():
            if assessment.name == name:
                return assessment
        return None

    @classmethod
    def get_all(cls) -> List["Assessment"]:
        return list(cls._instances.values())

    @classmethod
    def get_active(cls) -> List["Assessment"]:
        return [a for a in cls._instances.values() if a.status == AssessmentStatus.ACTIVE]

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
        return cls(
            name=name,
            description=description,
            period=period,
            status=AssessmentStatus.ACTIVE,
            created_by=created_by,
        )

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

    def archive(self) -> None:
        self.status = AssessmentStatus.ARCHIVED
        self.updated_at = datetime.now()

    def close(self) -> None:
        self.status = AssessmentStatus.CLOSED
        self.closed_at = datetime.now()
        self.updated_at = datetime.now()

    def reopen(self) -> None:
        self.status = AssessmentStatus.ACTIVE
        self.closed_at = None
        self.updated_at = datetime.now()

    def delete(self) -> None:
        if self.id in self._instances:
            del self._instances[self.id]