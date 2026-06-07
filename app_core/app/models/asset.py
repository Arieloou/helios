from datetime import datetime
from typing import Dict, List, Optional
import uuid


class Asset:
    _instances: Dict[str, "Asset"] = {}

    def __init__(
        self,
        id: Optional[str] = None,
        assessment_id: Optional[str] = None,
        name: Optional[str] = None,
        asset_type: Optional[str] = None,
        description: Optional[str] = None,
        confidentiality: int = 1,
        integrity: int = 1,
        availability: int = 1,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id or str(uuid.uuid4())
        self.assessment_id = assessment_id
        self.name = name
        self.asset_type = asset_type
        self.description = description
        self.confidentiality = max(1, min(5, confidentiality))
        self.integrity = max(1, min(5, integrity))
        self.availability = max(1, min(5, availability))
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at

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
        return cls._instances.get(id)

    @classmethod
    def get_all(cls) -> List["Asset"]:
        return list(cls._instances.values())

    @classmethod
    def get_by_assessment(cls, assessment_id: str) -> List["Asset"]:
        return [
            a for a in cls._instances.values()
            if a.assessment_id == assessment_id
        ]

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
        return cls(
            name=name,
            asset_type=asset_type,
            description=description,
            confidentiality=confidentiality,
            integrity=integrity,
            availability=availability,
            assessment_id=assessment_id,
        )

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

    def delete(self) -> None:
        if self.id in self._instances:
            del self._instances[self.id]