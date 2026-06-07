from typing import Dict, List, Optional

from app.models.risk_models import AssetThreatMapping
from app.models.asset import Asset
from app.services.assessment_service import AssessmentService


class MageritService:
    @classmethod
    def _get_asset_v_total(cls, asset_id: str) -> Optional[int]:
        asset = Asset.get_by_id(asset_id)
        return asset.v_total if asset else None

    @classmethod
    def list_mappings(cls, assessment_id: Optional[str] = None) -> List[Dict]:
        if assessment_id:
            mappings = AssetThreatMapping.get_by_assessment(assessment_id)
        else:
            mappings = AssetThreatMapping.get_all()
        
        result = []
        for mapping in mappings:
            data = mapping.to_dict()
            
            asset = Asset.get_by_id(mapping.asset_id)
            if asset:
                data["asset_name"] = asset.name
                data["asset_v_total"] = asset.v_total
            
            result.append(data)
        return result

    @classmethod
    def list_mappings_by_asset(cls, asset_id: str) -> List[Dict]:
        mappings = AssetThreatMapping.get_by_asset(asset_id)
        return [m.to_dict() for m in mappings]

    @classmethod
    def get_mapping(cls, mapping_id: str) -> Optional[Dict]:
        mapping = AssetThreatMapping.get_by_id(mapping_id)
        if not mapping:
            return None
        
        data = mapping.to_dict()
        asset = Asset.get_by_id(mapping.asset_id)
        if asset:
            data["asset_name"] = asset.name
            data["asset_v_total"] = asset.v_total
        return data

    @classmethod
    def create_mapping(
        cls,
        asset_id: str,
        threat_id: str,
        vulnerability_id: str,
        probability: int,
        degradation: float,
        assessment_id: Optional[str] = None,
    ) -> Dict:
        asset = Asset.get_by_id(asset_id)
        if not asset:
            raise ValueError(f"Activo no encontrado: {asset_id}")
        
        if not assessment_id:
            active = AssessmentService.get_active()
            if active:
                assessment_id = active["id"]

        v_total = asset.v_total
        
        mapping = AssetThreatMapping.create(
            asset_id=asset_id,
            threat_id=threat_id,
            vulnerability_id=vulnerability_id,
            probability=probability,
            degradation=degradation,
            assessment_id=assessment_id,
            v_total=v_total,
        )
        
        return mapping.to_dict()

    @classmethod
    def update_mapping(
        cls,
        mapping_id: str,
        probability: Optional[int] = None,
        degradation: Optional[float] = None,
    ) -> Dict:
        mapping = AssetThreatMapping.get_by_id(mapping_id)
        if not mapping:
            raise ValueError(f"Mapeo no encontrado: {mapping_id}")
        
        if probability is not None and not (1 <= probability <= 5):
            raise ValueError("La probabilidad debe estar entre 1 y 5")
        
        if degradation is not None and not (0.0 <= degradation <= 1.0):
            raise ValueError("La degradación debe estar entre 0 y 1")
        
        asset = Asset.get_by_id(mapping.asset_id)
        v_total = asset.v_total if asset else None
        
        AssetThreatMapping.update_risk(
            mapping_id=mapping_id,
            probability=probability,
            degradation=degradation,
            v_total=v_total,
        )
        
        return AssetThreatMapping.get_by_id(mapping_id).to_dict()

    @classmethod
    def delete_mapping(cls, mapping_id: str) -> None:
        mapping = AssetThreatMapping.get_by_id(mapping_id)
        if not mapping:
            raise ValueError(f"Mapeo no encontrado: {mapping_id}")
        mapping.delete()

    @classmethod
    def recalculate_all(cls, assessment_id: Optional[str] = None) -> int:
        count = 0
        if assessment_id:
            mappings = AssetThreatMapping.get_by_assessment(assessment_id)
        else:
            mappings = AssetThreatMapping.get_all()
        
        for mapping in mappings:
            asset = Asset.get_by_id(mapping.asset_id)
            if asset:
                mapping.calculate_risk(asset.v_total)
                count += 1
        
        return count

    @classmethod
    def get_risk_summary(cls, assessment_id: Optional[str] = None) -> Dict:
        if assessment_id:
            mappings = AssetThreatMapping.get_by_assessment(assessment_id)
        else:
            mappings = AssetThreatMapping.get_all()
        
        if not mappings:
            return {
                "total_mappings": 0,
                "avg_risk_inherent": 0,
                "max_risk_inherent": 0,
                "min_risk_inherent": 0,
            }
        
        ri_values = [m.risk_inherent for m in mappings if m.risk_inherent is not None]
        
        return {
            "total_mappings": len(mappings),
            "avg_risk_inherent": round(sum(ri_values) / len(ri_values), 2) if ri_values else 0,
            "max_risk_inherent": max(ri_values) if ri_values else 0,
            "min_risk_inherent": min(ri_values) if ri_values else 0,
        }