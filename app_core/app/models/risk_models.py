from datetime import datetime
from typing import Dict, List, Optional
import uuid


class Threat:
    _instances: Dict[str, "Threat"] = {}

    def __init__(
        self,
        id: Optional[str] = None,
        name: str = "",
        category: str = "",
        description: str = "",
    ):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.category = category
        self.description = description
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
        return cls._instances.get(id)

    @classmethod
    def get_all(cls) -> List["Threat"]:
        return list(cls._instances.values())

    @classmethod
    def get_by_category(cls, category: str) -> List["Threat"]:
        return [t for t in cls._instances.values() if t.category == category]


class Vulnerability:
    _instances: Dict[str, "Vulnerability"] = {}

    def __init__(
        self,
        id: Optional[str] = None,
        name: str = "",
        category: str = "",
        description: str = "",
    ):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.category = category
        self.description = description
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
        return cls._instances.get(id)

    @classmethod
    def get_all(cls) -> List["Vulnerability"]:
        return list(cls._instances.values())

    @classmethod
    def get_by_category(cls, category: str) -> List["Vulnerability"]:
        return [v for v in cls._instances.values() if v.category == category]


class AssetThreatMapping:
    _instances: Dict[str, "AssetThreatMapping"] = {}

    def __init__(
        self,
        id: Optional[str] = None,
        assessment_id: Optional[str] = None,
        asset_id: str = "",
        threat_id: str = "",
        vulnerability_id: str = "",
        probability: int = 1,
        degradation: float = 0.5,
        impact: Optional[float] = None,
        risk_inherent: Optional[float] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id or str(uuid.uuid4())
        self.assessment_id = assessment_id
        self.asset_id = asset_id
        self.threat_id = threat_id
        self.vulnerability_id = vulnerability_id
        self.probability = max(1, min(5, probability))
        self.degradation = max(0.0, min(1.0, degradation))
        self.impact = impact
        self.risk_inherent = risk_inherent
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at
        self._instances[self.id] = self

    def calculate_risk(self, v_total: int) -> None:
        self.impact = v_total * self.degradation
        self.risk_inherent = self.impact * self.probability
        self.updated_at = datetime.now()

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
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def get_by_id(cls, id: str) -> Optional["AssetThreatMapping"]:
        return cls._instances.get(id)

    @classmethod
    def get_all(cls) -> List["AssetThreatMapping"]:
        return list(cls._instances.values())

    @classmethod
    def get_by_asset(cls, asset_id: str) -> List["AssetThreatMapping"]:
        return [m for m in cls._instances.values() if m.asset_id == asset_id]

    @classmethod
    def get_by_assessment(cls, assessment_id: str) -> List["AssetThreatMapping"]:
        return [m for m in cls._instances.values() if m.assessment_id == assessment_id]

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