from datetime import datetime
from typing import Dict, List, Optional
import uuid

from .base import db, TimestampMixin


class Threat(db.Model):
    __tablename__ = "threats"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), default="")
    category = db.Column(db.String(100), default="")
    description = db.Column(db.Text, default="")

    _instances: Dict[str, "Threat"] = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.id:
            self._instances[self.id] = self

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
        }

    @classmethod
    def get_by_id(cls, id: str) -> Optional["Threat"]:
        if id in cls._instances:
            return cls._instances[id]
        return cls.query.get(id)

    @classmethod
    def get_all(cls) -> List["Threat"]:
        return cls.query.all()

    @classmethod
    def get_by_category(cls, category: str) -> List["Threat"]:
        return cls.query.filter_by(category=category).all()


class Vulnerability(db.Model):
    __tablename__ = "vulnerabilities"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), default="")
    category = db.Column(db.String(100), default="")
    description = db.Column(db.Text, default="")

    _instances: Dict[str, "Vulnerability"] = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.id:
            self._instances[self.id] = self

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
        }

    @classmethod
    def get_by_id(cls, id: str) -> Optional["Vulnerability"]:
        if id in cls._instances:
            return cls._instances[id]
        return cls.query.get(id)

    @classmethod
    def get_all(cls) -> List["Vulnerability"]:
        return cls.query.all()

    @classmethod
    def get_by_category(cls, category: str) -> List["Vulnerability"]:
        return cls.query.filter_by(category=category).all()


class AssetThreatMapping(db.Model, TimestampMixin):
    __tablename__ = "asset_threat_mappings"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    assessment_id = db.Column(db.String(36), db.ForeignKey("assessments.id"), nullable=True)
    asset_id = db.Column(db.String(36), db.ForeignKey("assets.id"), nullable=False)
    threat_id = db.Column(db.String(36), db.ForeignKey("threats.id"), nullable=False)
    vulnerability_id = db.Column(db.String(36), db.ForeignKey("vulnerabilities.id"), nullable=False)
    probability = db.Column(db.Integer, default=1)
    degradation = db.Column(db.Float, default=0.5)
    impact = db.Column(db.Float, nullable=True)
    risk_inherent = db.Column(db.Float, nullable=True)
    maturity = db.Column(db.Float, default=0.0)
    residual_risk = db.Column(db.Float, nullable=True)

    _instances: Dict[str, "AssetThreatMapping"] = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.id:
            self._instances[self.id] = self
        if self.probability:
            self.probability = max(1, min(5, self.probability))
        if self.degradation:
            self.degradation = max(0.0, min(1.0, self.degradation))
        if self.maturity:
            self.maturity = max(0.0, min(1.0, self.maturity))

    def calculate_risk(self, v_total: int) -> None:
        self.impact = v_total * self.degradation
        self.risk_inherent = self.impact * self.probability
        self.calculate_residual_risk()
        self.updated_at = datetime.now()
        db.session.commit()

    def calculate_residual_risk(self) -> None:
        if self.risk_inherent is not None:
            self.residual_risk = self.risk_inherent * (1 - self.maturity)
            self.updated_at = datetime.now()
            db.session.commit()

    def set_maturity(self, maturity: float) -> None:
        self.maturity = max(0.0, min(1.0, maturity))
        self.calculate_residual_risk()

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "assessment_id": self.assessment_id,
            "asset_id": self.asset_id,
            "threat_id": self.threat_id,
            "vulnerability_id": self.vulnerability_id,
            "probability": self.probability,
            "degradation": self.degradation,
            "impact": round(self.impact, 2) if self.impact else None,
            "risk_inherent": round(self.risk_inherent, 2) if self.risk_inherent else None,
            "maturity": round(self.maturity, 2),
            "maturity_display": round(self.maturity * 100, 1),
            "residual_risk": round(self.residual_risk, 2) if self.residual_risk else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def get_by_id(cls, id: str) -> Optional["AssetThreatMapping"]:
        if id in cls._instances:
            return cls._instances[id]
        return cls.query.get(id)

    @classmethod
    def get_all(cls) -> List["AssetThreatMapping"]:
        return cls.query.all()

    @classmethod
    def get_by_asset(cls, asset_id: str) -> List["AssetThreatMapping"]:
        return cls.query.filter_by(asset_id=asset_id).all()

    @classmethod
    def get_by_assessment(cls, assessment_id: str) -> List["AssetThreatMapping"]:
        return cls.query.filter_by(assessment_id=assessment_id).all()

    @classmethod
    def create(
        cls,
        asset_id: str,
        threat_id: str,
        vulnerability_id: str,
        probability: int,
        degradation: float,
        assessment_id: Optional[str] = None,
        v_total: Optional[int] = None,
    ) -> "AssetThreatMapping":
        mapping = cls(
            assessment_id=assessment_id,
            asset_id=asset_id,
            threat_id=threat_id,
            vulnerability_id=vulnerability_id,
            probability=probability,
            degradation=degradation,
        )
        db.session.add(mapping)
        db.session.commit()
        if v_total is not None:
            mapping.calculate_risk(v_total)
        return mapping

    @classmethod
    def update_risk(
        cls,
        mapping_id: str,
        probability: Optional[int] = None,
        degradation: Optional[float] = None,
        v_total: Optional[int] = None,
    ) -> Optional["AssetThreatMapping"]:
        mapping = cls.get_by_id(mapping_id)
        if not mapping:
            return None
        if probability is not None:
            mapping.probability = max(1, min(5, probability))
        if degradation is not None:
            mapping.degradation = max(0.0, min(1.0, degradation))
        if v_total is not None:
            mapping.calculate_risk(v_total)
        return mapping

    def delete(self) -> None:
        if self.id in self._instances:
            del self._instances[self.id]
        db.session.delete(self)
        db.session.commit()