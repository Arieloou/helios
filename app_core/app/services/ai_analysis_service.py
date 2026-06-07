from typing import Dict, List, Optional

from app.models.asset import Asset
from app.models.risk_models import AssetThreatMapping
from app.models.iso_models import ControlMaturity
from app.services.ollama_client import ollama_client


class AIAnalysisService:
    @classmethod
    def is_available(cls) -> bool:
        return ollama_client.is_available()

    @classmethod
    def get_models(cls) -> List[str]:
        return ollama_client.list_models()

    @classmethod
    def compile_asset_data(cls, asset_id: str) -> Optional[Dict]:
        asset = Asset.get_by_id(asset_id)
        if not asset:
            return None

        mappings = AssetThreatMapping.get_by_asset(asset_id)

        maturity_data = {}
        if asset.assessment_id:
            maturities = ControlMaturity.get_by_assessment(asset.assessment_id)
            for m in maturities:
                maturity_data[m.control_id] = m.maturity_percentage

        asset_data = {
            "id": asset.id,
            "name": asset.name,
            "asset_type": asset.asset_type,
            "description": asset.description,
            "assessment_id": asset.assessment_id,
            "confidentiality": asset.confidentiality,
            "integrity": asset.integrity,
            "availability": asset.availability,
            "v_total": asset.v_total,
            "risk_inherent": None,
            "residual_risk": None,
            "maturity_display": "0%",
            "mappings_count": len(mappings),
            "maturity_data": maturity_data,
        }

        if mappings:
            avg_ri = sum(m.risk_inherent for m in mappings if m.risk_inherent) / len(mappings)
            avg_rr = sum(m.residual_risk for m in mappings if m.residual_risk) / len(mappings)
            avg_m = sum(m.maturity for m in mappings) / len(mappings)

            asset_data["risk_inherent"] = round(avg_ri, 2)
            asset_data["residual_risk"] = round(avg_rr, 2)
            asset_data["maturity_display"] = f"{round(avg_m * 100, 1)}%"

        return asset_data

    @classmethod
    def analyze_asset(cls, asset_id: str) -> Dict:
        asset_data = cls.compile_asset_data(asset_id)
        if not asset_data:
            return {
                "success": False,
                "error": "Activo no encontrado",
            }

        return ollama_client.analyze_asset(asset_data)

    @classmethod
    def analyze_asset_safe(cls, asset_id: str) -> Dict:
        if not cls.is_available():
            return {
                "success": False,
                "error": "Servicio Ollama no disponible. Asegúrese de que Ollama esté ejecutándose en localhost:11434",
                "available": False,
            }

        return cls.analyze_asset(asset_id)

    @classmethod
    def get_asset_with_analysis(cls, asset_id: str) -> Dict:
        asset = Asset.get_by_id(asset_id)
        if not asset:
            return {"error": "Activo no encontrado"}

        asset_dict = asset.to_dict()
        analysis_result = cls.analyze_asset_safe(asset_id)

        asset_dict["analysis"] = analysis_result
        asset_dict["ollama_available"] = cls.is_available()

        return asset_dict