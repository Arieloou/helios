from datetime import datetime
from typing import Dict, List, Optional
import uuid

from .base import db, TimestampMixin


class Asset(db.Model, TimestampMixin):
    __tablename__ = "assets"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    assessment_id = db.Column(db.String(36), db.ForeignKey("assessments.id"), nullable=True)
    name = db.Column(db.String(255), nullable=True)
    asset_type = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    confidentiality = db.Column(db.Integer, default=1)
    integrity = db.Column(db.Integer, default=1)
    availability = db.Column(db.Integer, default=1)

    _instances: Dict[str, "Asset"] = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.id:
            self._instances[self.id] = self

    @property
    def v_total(self) -> int:
        return max(self.confidentiality, self.integrity, self.availability)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "assessment_id": self.assessment_id,
            "name": self.name,
            "asset_type": self.asset_type,
            "description": self.description,
            "confidentiality": self.confidentiality,
            "integrity": self.integrity,
            "availability": self.availability,
            "v_total": self.v_total,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def get_by_id(cls, id: str) -> Optional["Asset"]:
        if id in cls._instances:
            return cls._instances[id]
        return cls.query.get(id)

    @classmethod
    def get_all(cls) -> List["Asset"]:
        return cls.query.all()

    @classmethod
    def get_by_assessment(cls, assessment_id: str) -> List["Asset"]:
        return cls.query.filter_by(assessment_id=assessment_id).all()

    @classmethod
    def create(
        cls,
        name: str,
        asset_type: str,
        description: str,
        confidentiality: int,
        integrity: int,
        availability: int,
        assessment_id: Optional[str] = None,
    ) -> "Asset":
        asset = cls(
            name=name,
            asset_type=asset_type,
            description=description,
            confidentiality=max(1, min(5, confidentiality)),
            integrity=max(1, min(5, integrity)),
            availability=max(1, min(5, availability)),
            assessment_id=assessment_id,
        )
        db.session.add(asset)
        db.session.commit()
        return asset

    def update(
        self,
        name: Optional[str] = None,
        asset_type: Optional[str] = None,
        description: Optional[str] = None,
        confidentiality: Optional[int] = None,
        integrity: Optional[int] = None,
        availability: Optional[int] = None,
    ) -> None:
        if name is not None:
            self.name = name
        if asset_type is not None:
            self.asset_type = asset_type
        if description is not None:
            self.description = description
        if confidentiality is not None:
            self.confidentiality = max(1, min(5, confidentiality))
        if integrity is not None:
            self.integrity = max(1, min(5, integrity))
        if availability is not None:
            self.availability = max(1, min(5, availability))
        self.updated_at = datetime.now()
        db.session.commit()

    def delete(self) -> None:
        if self.id in self._instances:
            del self._instances[self.id]
        db.session.delete(self)
        db.session.commit()