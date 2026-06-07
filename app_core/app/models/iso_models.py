from datetime import datetime
from typing import Dict, List, Optional
import uuid


class ISOControl:
    _instances: Dict[str, "ISOControl"] = {}

    def __init__(
        self,
        id: Optional[str] = None,
        control_id: str = "",
        domain: str = "",
        title: str = "",
        description: str = "",
    ):
        self.id = id or str(uuid.uuid4())
        self.control_id = control_id
        self.domain = domain
        self.title = title
        self.description = description
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
        return cls._instances.get(id)

    @classmethod
    def get_by_control_id(cls, control_id: str) -> Optional["ISOControl"]:
        for c in cls._instances.values():
            if c.control_id == control_id:
                return c
        return None

    @classmethod
    def get_all(cls) -> List["ISOControl"]:
        return list(cls._instances.values())

    @classmethod
    def get_by_domain(cls, domain: str) -> List["ISOControl"]:
        return [c for c in cls._instances.values() if c.domain == domain]

    @classmethod
    def get_domains(cls) -> List[str]:
        domains = set(c.domain for c in cls._instances.values())
        return sorted(list(domains))


class ControlQuestion:
    _instances: Dict[str, "ControlQuestion"] = {}

    def __init__(
        self,
        id: Optional[str] = None,
        control_id: str = "",
        question_text: str = "",
        options: str = "[]",
    ):
        self.id = id or str(uuid.uuid4())
        self.control_id = control_id
        self.question_text = question_text
        self.options = options
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
        return cls._instances.get(id)

    @classmethod
    def get_by_control(cls, control_id: str) -> List["ControlQuestion"]:
        return [q for q in cls._instances.values() if q.control_id == control_id]

    @classmethod
    def get_all(cls) -> List["ControlQuestion"]:
        return list(cls._instances.values())


class ControlResponse:
    _instances: Dict[str, "ControlResponse"] = {}

    def __init__(
        self,
        id: Optional[str] = None,
        assessment_id: Optional[str] = None,
        control_id: str = "",
        question_id: str = "",
        response: Optional[int] = None,
        score: Optional[float] = None,
        created_at: Optional[datetime] = None,
    ):
        self.id = id or str(uuid.uuid4())
        self.assessment_id = assessment_id
        self.control_id = control_id
        self.question_id = question_id
        self.response = response
        self.score = score
        self.created_at = created_at or datetime.now()
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
        return cls._instances.get(id)

    @classmethod
    def get_by_assessment(cls, assessment_id: str) -> List["ControlResponse"]:
        return [r for r in cls._instances.values() if r.assessment_id == assessment_id]

    @classmethod
    def get_by_control(cls, assessment_id: str, control_id: str) -> List["ControlResponse"]:
        return [r for r in cls._instances.values() 
                if r.assessment_id == assessment_id and r.control_id == control_id]

    @classmethod
    def get_by_question(cls, assessment_id: str, question_id: str) -> Optional["ControlResponse"]:
        for r in cls._instances.values():
            if r.assessment_id == assessment_id and r.question_id == question_id:
                return r
        return None


class ControlMaturity:
    _instances: Dict[str, "ControlMaturity"] = {}

    def __init__(
        self,
        id: Optional[str] = None,
        assessment_id: Optional[str] = None,
        control_id: str = "",
        maturity_percentage: float = 0.0,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id or str(uuid.uuid4())
        self.assessment_id = assessment_id
        self.control_id = control_id
        self.maturity_percentage = max(0.0, min(1.0, maturity_percentage))
        self.updated_at = updated_at
        self._instances[self.id] = self

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
        return cls._instances.get(id)

    @classmethod
    def get_by_assessment(cls, assessment_id: str) -> List["ControlMaturity"]:
        return [m for m in cls._instances.values() if m.assessment_id == assessment_id]

    @classmethod
    def get_by_control(cls, assessment_id: str, control_id: str) -> Optional["ControlMaturity"]:
        for m in cls._instances.values():
            if m.assessment_id == assessment_id and m.control_id == control_id:
                return m
        return None

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