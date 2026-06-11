import json
import csv
from io import StringIO
from typing import Dict, List, Optional

from app.models.risk_models import AssetThreatMapping
from app.models.asset import Asset
from app.services.dashboard_service import DashboardService


class ExportService:
    @classmethod
    def export_to_json(cls, assessment_id: Optional[str] = None) -> str:
        data = DashboardService.get_dashboard_data(assessment_id)
        return json.dumps(data, indent=2, ensure_ascii=False)

    @classmethod
    def export_to_csv(cls, assessment_id: Optional[str] = None) -> str:
        if assessment_id:
            mappings = AssetThreatMapping.get_by_assessment(assessment_id)
        else:
            mappings = AssetThreatMapping.get_all()

        output = StringIO()
        writer = csv.writer(output)

        writer.writerow([
            "ID",
            "Activo",
            "V_Total",
            "Probabilidad",
            "Degradacion",
            "Impacto",
            "Riesgo_Inherente",
            "Madurez",
            "Riesgo_Residual",
            "Nivel_RI",
            "Nivel_RR",
        ])

        for mapping in mappings:
            asset = Asset.get_by_id(mapping.asset_id)
            asset_name = asset.name if asset else "Unknown"
            asset_v_total = asset.v_total if asset else 0

            from app.services.risk_calculation_service import RiskCalculationService
            ri_level = RiskCalculationService.get_risk_level(mapping.risk_inherent or 0)
            rr_level = RiskCalculationService.get_risk_level(mapping.residual_risk or 0)

            writer.writerow([
                mapping.id,
                asset_name,
                asset_v_total,
                mapping.probability,
                mapping.degradation,
                mapping.impact or "",
                mapping.risk_inherent or "",
                mapping.maturity,
                mapping.residual_risk or "",
                ri_level,
                rr_level,
            ])

        return output.getvalue()

    @classmethod
    def export_risk_journey_csv(cls, assessment_id: Optional[str] = None) -> str:
        journeys = DashboardService.get_risk_journey_data(assessment_id)

        output = StringIO()
        writer = csv.writer(output)

        writer.writerow([
            "Activo",
            "Riesgo_Inherente",
            "Riesgo_Residual",
            "Madurez_%",
            "Reduccion",
            "Reduccion_%",
            "Posicion_RI",
            "Posicion_RR",
        ])

        for journey in journeys:
            writer.writerow([
                journey["asset_name"],
                journey["risk_inherent"],
                journey["residual_risk"],
                journey["maturity_display"],
                journey["reduction"],
                journey["reduction_percent"],
                journey["ri_position"]["cell"],
                journey["rr_position"]["cell"],
            ])

        return output.getvalue()

    @classmethod
    def export_powerbi_format(cls, assessment_id: Optional[str] = None) -> str:
        if assessment_id:
            mappings = AssetThreatMapping.get_by_assessment(assessment_id)
        else:
            mappings = AssetThreatMapping.get_all()

        data = []
        for mapping in mappings:
            asset = Asset.get_by_id(mapping.asset_id)

            from app.services.risk_calculation_service import RiskCalculationService
            ri_level = RiskCalculationService.get_risk_level(mapping.risk_inherent or 0)
            rr_level = RiskCalculationService.get_risk_level(mapping.residual_risk or 0)

            data.append({
                "asset_id": mapping.asset_id,
                "asset_name": asset.name if asset else "Unknown",
                "asset_type": asset.asset_type if asset else "Unknown",
                "asset_v_total": asset.v_total if asset else 0,
                "threat_id": mapping.threat_id,
                "vulnerability_id": mapping.vulnerability_id,
                "probability": mapping.probability,
                "degradation": mapping.degradation,
                "impact": mapping.impact,
                "risk_inherent": mapping.risk_inherent,
                "risk_inherent_level": ri_level,
                "maturity": mapping.maturity,
                "maturity_percentage": round(mapping.maturity * 100, 1),
                "residual_risk": mapping.residual_risk,
                "residual_risk_level": rr_level,
                "ri_row": mapping.impact,
                "ri_col": mapping.probability,
                "rr_row": mapping.residual_risk / mapping.probability if mapping.probability > 0 else 0,
                "rr_col": mapping.probability,
            })

        return json.dumps(data, indent=2, ensure_ascii=False)

    @classmethod
    def get_export_options(cls) -> List[Dict]:
        return [
            {
                "id": "json",
                "name": "JSON Completo",
                "description": "Exporta todos los datos del dashboard en formato JSON",
                "mime_type": "application/json",
                "extension": ".json",
            },
            {
                "id": "csv",
                "name": "CSV Riesgos",
                "description": "Exporta los riesgos en formato CSV tabular",
                "mime_type": "text/csv",
                "extension": ".csv",
            },
            {
                "id": "journey_csv",
                "name": "CSV Viaje del Riesgo",
                "description": "Exporta el viaje del riesgo (RI → RR) en CSV",
                "mime_type": "text/csv",
                "extension": ".csv",
            },
            {
                "id": "powerbi",
                "name": "Power BI (JSON)",
                "description": "Formato optimizado para Power BI",
                "mime_type": "application/json",
                "extension": ".json",
            },
        ]