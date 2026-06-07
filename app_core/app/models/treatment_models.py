from datetime import datetime
from typing import Dict, List, Optional
import uuid


class TreatmentPlan:
    _instances: Dict[str, "TreatmentPlan"] = {}

    def __init__(
        self,
        id: Optional[str] = None,
        assessment_id: Optional[str] = None,
        mapping_id: str = "",
        strategy: str = "mitigate",
        status: str = "pending",
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id or str(uuid.uuid4())
        self.assessment_id = assessment_id
        self.mapping_id = mapping_id
        self.strategy = strategy
        self.status = status
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at
        self._instances[self.id] = self

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "assessment_id": self.assessment_id,
            "mapping_id": self.mapping_id,
            "strategy": self.strategy,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def update_status(self, status: str) -> None:
        valid_statuses = ["pending", "approved", "in_progress", "completed"]
        if status not in valid_statuses:
            raise ValueError(f"Estado inválido: {status}")
        self.status = status
        self.updated_at = datetime.now()

    @classmethod
    def get_by_id(cls, id: str) -> Optional["TreatmentPlan"]:
        return cls._instances.get(id)

    @classmethod
    def get_all(cls) -> List["TreatmentPlan"]:
        return list(cls._instances.values())

    @classmethod
    def get_by_assessment(cls, assessment_id: str) -> List["TreatmentPlan"]:
        return [p for p in cls._instances.values() if p.assessment_id == assessment_id]

    @classmethod
    def get_by_mapping(cls, mapping_id: str) -> Optional["TreatmentPlan"]:
        for plan in cls._instances.values():
            if plan.mapping_id == mapping_id:
                return plan
        return None

    def delete(self) -> None:
        if self.id in self._instances:
            del self._instances[self.id]


class TreatmentTask:
    _instances: Dict[str, "TreatmentTask"] = {}

    def __init__(
        self,
        id: Optional[str] = None,
        plan_id: str = "",
        description: str = "",
        responsible: Optional[str] = None,
        due_date: Optional[datetime] = None,
        status: str = "pending",
        progress_percentage: int = 0,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id or str(uuid.uuid4())
        self.plan_id = plan_id
        self.description = description
        self.responsible = responsible
        self.due_date = due_date
        self.status = status
        self.progress_percentage = max(0, min(100, progress_percentage))
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at
        self._instances[self.id] = self

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "plan_id": self.plan_id,
            "description": self.description,
            "responsible": self.responsible,
            "due_date": self.due_date.strftime("%Y-%m-%d") if self.due_date else None,
            "status": self.status,
            "progress_percentage": self.progress_percentage,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def update_progress(self, progress: int, status: Optional[str] = None) -> None:
        self.progress_percentage = max(0, min(100, progress))
        if status:
            valid_statuses = ["pending", "in_progress", "completed"]
            if status not in valid_statuses:
                raise ValueError(f"Estado inválido: {status}")
            self.status = status
        self.updated_at = datetime.now()

    @classmethod
    def get_by_id(cls, id: str) -> Optional["TreatmentTask"]:
        return cls._instances.get(id)

    @classmethod
    def get_all(cls) -> List["TreatmentTask"]:
        return list(cls._instances.values())

    @classmethod
    def get_by_plan(cls, plan_id: str) -> List["TreatmentTask"]:
        return [t for t in cls._instances.values() if t.plan_id == plan_id]

    def delete(self) -> None:
        if self.id in self._instances:
            del self._instances[self.id]