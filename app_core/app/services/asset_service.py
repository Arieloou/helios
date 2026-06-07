from typing import Dict, List, Optional

from app.models.asset import Asset


class AssetService:
    @classmethod
    def list_all(cls) -> List[Dict]:
        assets = Asset.get_all()
        return [a.to_dict() for a in assets]

    @classmethod
    def list_by_assessment(cls, assessment_id: str) -> List[Dict]:
        assets = Asset.get_by_assessment(assessment_id)
        return [a.to_dict() for a in assets]

    @classmethod
    def get_by_id(cls, asset_id: str) -> Optional[Dict]:
        asset = Asset.get_by_id(asset_id)
        return asset.to_dict() if asset else None

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
    ) -> Dict:
        if not name:
            raise ValueError("El nombre del activo es requerido")

        if confidentiality not in range(1, 6):
            raise ValueError("La confidencialidad debe estar entre 1 y 5")
        if integrity not in range(1, 6):
            raise ValueError("La integridad debe estar entre 1 y 5")
        if availability not in range(1, 6):
            raise ValueError("La disponibilidad debe estar entre 1 y 5")

        asset = Asset.create(
            name=name,
            asset_type=asset_type,
            description=description,
            confidentiality=confidentiality,
            integrity=integrity,
            availability=availability,
            assessment_id=assessment_id,
        )
        return asset.to_dict()

    @classmethod
    def update(
        cls,
        asset_id: str,
        name: Optional[str] = None,
        asset_type: Optional[str] = None,
        description: Optional[str] = None,
        confidentiality: Optional[int] = None,
        integrity: Optional[int] = None,
        availability: Optional[int] = None,
    ) -> Dict:
        asset = Asset.get_by_id(asset_id)
        if not asset:
            raise ValueError(f"Activo no encontrado: {asset_id}")

        if confidentiality is not None and confidentiality not in range(1, 6):
            raise ValueError("La confidencialidad debe estar entre 1 y 5")
        if integrity is not None and integrity not in range(1, 6):
            raise ValueError("La integridad debe estar entre 1 y 5")
        if availability is not None and availability not in range(1, 6):
            raise ValueError("La disponibilidad debe estar entre 1 y 5")

        asset.update(
            name=name,
            asset_type=asset_type,
            description=description,
            confidentiality=confidentiality,
            integrity=integrity,
            availability=availability,
        )
        return asset.to_dict()

    @classmethod
    def delete(cls, asset_id: str) -> None:
        asset = Asset.get_by_id(asset_id)
        if not asset:
            raise ValueError(f"Activo no encontrado: {asset_id}")
        asset.delete()

    @classmethod
    def get_v_total(cls, asset_id: str) -> Optional[int]:
        asset = Asset.get_by_id(asset_id)
        return asset.v_total if asset else None

    @classmethod
    def count_by_assessment(cls, assessment_id: str) -> int:
        return len(Asset.get_by_assessment(assessment_id))