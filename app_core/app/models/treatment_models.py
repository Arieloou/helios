from datetime import datetime
from typing import Dict, List, Optional
import uuid

from .base import db, TimestampMixin


class TreatmentPlan(db.Model, TimestampMixin):
    __tablename__ = "treatment_plans"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    assessment_id = db.Column(db.String(36), db.ForeignKey("assessments.id"), nullable=True)
    mapping_id = db.Column(db.String(36), db.ForeignKey("asset_threat_mappings.id"), nullable=False)
    strategy = db.Column(db.String(50), default="mitigate")
    status = db.Column(db.String(50), default="pending")

    _instances: Dict[str, "TreatmentPlan"] = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.id:
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
        db.session.commit()

    @classmethod
    def get_by_id(cls, id: str) -> Optional["TreatmentPlan"]:
        if id in cls._instances:
            return cls._instances[id]
        return cls.query.get(id)

    @classmethod
    def get_all(cls) -> List["TreatmentPlan"]:
        return cls.query.all()

    @classmethod
    def get_by_assessment(cls, assessment_id: str) -> List["TreatmentPlan"]:
        return cls.query.filter_by(assessment_id=assessment_id).all()

    @classmethod
    def get_by_mapping(cls, mapping_id: str) -> Optional["TreatmentPlan"]:
        return cls.query.filter_by(mapping_id=mapping_id).first()

    def delete(self) -> None:
        if self.id in self._instances:
            del self._instances[self.id]
        db.session.delete(self)
        db.session.commit()


class TreatmentTask(db.Model, TimestampMixin):
    __tablename__ = "treatment_tasks"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plan_id = db.Column(db.String(36), db.ForeignKey("treatment_plans.id"), nullable=False)
    description = db.Column(db.Text, default="")
    responsible = db.Column(db.String(255), nullable=True)
    due_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), default="pending")
    progress_percentage = db.Column(db.Integer, default=0)

    _instances: Dict[str, "TreatmentTask"] = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.id:
            self._instances[self.id] = self
        if self.progress_percentage:
            self.progress_percentage = max(0, min(100, self.progress_percentage))

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
        db.session.commit()

    @classmethod
    def get_by_id(cls, id: str) -> Optional["TreatmentTask"]:
        if id in cls._instances:
            return cls._instances[id]
        return cls.query.get(id)

    @classmethod
    def get_all(cls) -> List["TreatmentTask"]:
        return cls.query.all()

    @classmethod
    def get_by_plan(cls, plan_id: str) -> List["TreatmentTask"]:
        return cls.query.filter_by(plan_id=plan_id).all()

    def delete(self) -> None:
        if self.id in self._instances:
            del self._instances[self.id]
        db.session.delete(self)
        db.session.commit()