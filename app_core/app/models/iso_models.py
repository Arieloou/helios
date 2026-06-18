from datetime import datetime
from typing import Dict, List, Optional
import uuid

from .base import db


class ISOControl(db.Model):
    __tablename__ = "iso_controls"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    control_id = db.Column(db.String(50), unique=True, nullable=False)
    domain = db.Column(db.String(100), default="")
    title = db.Column(db.String(255), default="")
    description = db.Column(db.Text, default="")

    _instances: Dict[str, "ISOControl"] = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.id:
            self._instances[self.id] = self

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "control_id": self.control_id,
            "domain": self.domain,
            "title": self.title,
            "description": self.description,
        }

    @classmethod
    def get_by_id(cls, id: str) -> Optional["ISOControl"]:
        if id in cls._instances:
            return cls._instances[id]
        return cls.query.get(id)

    @classmethod
    def get_by_control_id(cls, control_id: str) -> Optional["ISOControl"]:
        return cls.query.filter_by(control_id=control_id).first()

    @classmethod
    def get_all(cls) -> List["ISOControl"]:
        return cls.query.all()

    @classmethod
    def get_by_domain(cls, domain: str) -> List["ISOControl"]:
        return cls.query.filter_by(domain=domain).all()

    @classmethod
    def get_domains(cls) -> List[str]:
        domains = db.session.query(cls.domain).distinct().all()
        return sorted([d[0] for d in domains if d[0]])


class ControlQuestion(db.Model):
    __tablename__ = "control_questions"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    control_id = db.Column(db.String(50), db.ForeignKey("iso_controls.control_id"), nullable=False)
    question_text = db.Column(db.Text, default="")
    options = db.Column(db.Text, default="[]")

    _instances: Dict[str, "ControlQuestion"] = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.id:
            self._instances[self.id] = self

    def to_dict(self) -> Dict:
        import json
        return {
            "id": self.id,
            "control_id": self.control_id,
            "question_text": self.question_text,
            "options": json.loads(self.options),
        }

    @classmethod
    def get_by_id(cls, id: str) -> Optional["ControlQuestion"]:
        if id in cls._instances:
            return cls._instances[id]
        return cls.query.get(id)

    @classmethod
    def get_by_control(cls, control_id: str) -> List["ControlQuestion"]:
        return cls.query.filter_by(control_id=control_id).all()

    @classmethod
    def get_all(cls) -> List["ControlQuestion"]:
        return cls.query.all()


class ControlResponse(db.Model):
    __tablename__ = "control_responses"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    assessment_id = db.Column(db.String(36), db.ForeignKey("assessments.id"), nullable=True)
    control_id = db.Column(db.String(50), db.ForeignKey("iso_controls.control_id"), nullable=False)
    question_id = db.Column(db.String(36), db.ForeignKey("control_questions.id"), nullable=False)
    response = db.Column(db.Integer, nullable=True)
    score = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    _instances: Dict[str, "ControlResponse"] = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.id:
            self._instances[self.id] = self

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "assessment_id": self.assessment_id,
            "control_id": self.control_id,
            "question_id": self.question_id,
            "response": self.response,
            "score": self.score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def get_by_id(cls, id: str) -> Optional["ControlResponse"]:
        if id in cls._instances:
            return cls._instances[id]
        return cls.query.get(id)

    @classmethod
    def get_by_assessment(cls, assessment_id: str) -> List["ControlResponse"]:
        return cls.query.filter_by(assessment_id=assessment_id).all()

    @classmethod
    def get_by_control(cls, assessment_id: str, control_id: str) -> List["ControlResponse"]:
        return cls.query.filter_by(assessment_id=assessment_id, control_id=control_id).all()

    @classmethod
    def get_by_question(cls, assessment_id: str, question_id: str) -> Optional["ControlResponse"]:
        return cls.query.filter_by(assessment_id=assessment_id, question_id=question_id).first()


class ControlMaturity(db.Model):
    __tablename__ = "control_maturities"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    assessment_id = db.Column(db.String(36), db.ForeignKey("assessments.id"), nullable=True)
    control_id = db.Column(db.String(50), db.ForeignKey("iso_controls.control_id"), nullable=False)
    maturity_percentage = db.Column(db.Float, default=0.0)
    updated_at = db.Column(db.DateTime, nullable=True)

    _instances: Dict[str, "ControlMaturity"] = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.id:
            self._instances[self.id] = self
        if self.maturity_percentage:
            self.maturity_percentage = max(0.0, min(1.0, self.maturity_percentage))

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "assessment_id": self.assessment_id,
            "control_id": self.control_id,
            "maturity_percentage": self.maturity_percentage,
            "maturity_percentage_display": round(self.maturity_percentage * 100, 1),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def get_by_id(cls, id: str) -> Optional["ControlMaturity"]:
        if id in cls._instances:
            return cls._instances[id]
        return cls.query.get(id)

    @classmethod
    def get_by_assessment(cls, assessment_id: str) -> List["ControlMaturity"]:
        return cls.query.filter_by(assessment_id=assessment_id).all()

    @classmethod
    def get_by_control(cls, assessment_id: str, control_id: str) -> Optional["ControlMaturity"]:
        return cls.query.filter_by(assessment_id=assessment_id, control_id=control_id).first()

    @classmethod
    def calculate_maturity(cls, assessment_id: str, control_id: str) -> float:
        responses = ControlResponse.get_by_control(assessment_id, control_id)
        if not responses:
            return 0.0

        total_score = 0.0
        max_score = 0.0

        for r in responses:
            if r.score is not None:
                total_score += r.score
                max_score += 1.0

        if max_score == 0:
            return 0.0

        return total_score / max_score