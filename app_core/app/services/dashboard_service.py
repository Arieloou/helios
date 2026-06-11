from typing import Dict, List, Optional
from collections import defaultdict

from app.models.risk_models import AssetThreatMapping
from app.models.asset import Asset
from app.services.risk_calculation_service import RiskCalculationService


class DashboardService:
    @classmethod
    def get_executive_summary(cls, assessment_id: Optional[str] = None) -> Dict:
        if assessment_id:
            mappings = AssetThreatMapping.get_by_assessment(assessment_id)
        else:
            mappings = AssetThreatMapping.get_all()

        if not mappings:
            return {
                "total_risks": 0,
                "ri_critical": 0,
                "ri_high": 0,
                "ri_medium": 0,
                "ri_low": 0,
                "rr_critical": 0,
                "rr_high": 0,
                "rr_medium": 0,
                "rr_low": 0,
                "avg_maturity": 0,
                "risks_reduced": 0,
                "reduction_percentage": 0,
            }

        ri_critical = ri_high = ri_medium = ri_low = 0
        rr_critical = rr_high = rr_medium = rr_low = 0
        maturity_sum = 0

        for mapping in mappings:
            if mapping.risk_inherent is not None:
                level = RiskCalculationService.get_risk_level(mapping.risk_inherent)
                if level == "Crítico":
                    ri_critical += 1
                elif level == "Alto":
                    ri_high += 1
                elif level == "Medio":
                    ri_medium += 1
                else:
                    ri_low += 1

            if mapping.residual_risk is not None:
                level = RiskCalculationService.get_risk_level(mapping.residual_risk)
                if level == "Crítico":
                    rr_critical += 1
                elif level == "Alto":
                    rr_high += 1
                elif level == "Medio":
                    rr_medium += 1
                else:
                    rr_low += 1

            maturity_sum += mapping.maturity

        avg_maturity = maturity_sum / len(mappings) if mappings else 0

        total_ri = sum(m.risk_inherent for m in mappings if m.risk_inherent is not None)
        total_rr = sum(m.residual_risk for m in mappings if m.residual_risk is not None)
        risks_reduced = total_ri - total_rr
        reduction_percentage = (risks_reduced / total_ri * 100) if total_ri > 0 else 0

        return {
            "total_risks": len(mappings),
            "ri_critical": ri_critical,
            "ri_high": ri_high,
            "ri_medium": ri_medium,
            "ri_low": ri_low,
            "rr_critical": rr_critical,
            "rr_high": rr_high,
            "rr_medium": rr_medium,
            "rr_low": rr_low,
            "avg_maturity": round(avg_maturity * 100, 1),
            "risks_reduced": round(risks_reduced, 2),
            "reduction_percentage": round(reduction_percentage, 1),
        }

    @classmethod
    def get_risk_matrix_data(cls, assessment_id: Optional[str] = None) -> Dict:
        if assessment_id:
            mappings = AssetThreatMapping.get_by_assessment(assessment_id)
        else:
            mappings = AssetThreatMapping.get_all()

        matrix = defaultdict(lambda: {"ri_count": 0, "rr_count": 0, "risks": []})

        for mapping in mappings:
            if mapping.impact is None or mapping.risk_inherent is None:
                continue

            impact_rounded = max(1, min(5, round(mapping.impact)))
            probability = mapping.probability

            ri_cell = f"{impact_rounded}-{probability}"
            matrix[ri_cell]["ri_count"] += 1
            matrix[ri_cell]["risks"].append({
                "id": mapping.id,
                "type": "inherent",
                "asset_id": mapping.asset_id,
                "impact": mapping.impact,
                "probability": probability,
                "risk_value": mapping.risk_inherent,
            })

            if mapping.residual_risk is not None:
                rr_impact = mapping.residual_risk / mapping.probability if mapping.probability > 0 else 0
                rr_impact_rounded = max(1, min(5, round(rr_impact)))
                rr_cell = f"{rr_impact_rounded}-{probability}"
                if rr_cell != ri_cell:
                    matrix[rr_cell]["rr_count"] += 1
                    matrix[ri_cell]["risks"].append({
                        "id": mapping.id,
                        "type": "residual",
                        "asset_id": mapping.asset_id,
                        "impact": rr_impact,
                        "probability": probability,
                        "risk_value": mapping.residual_risk,
                    })

        matrix_cells = {}
        for cell_key, cell_data in matrix.items():
            parts = cell_key.split("-")
            impact_level = int(parts[0])
            prob_level = int(parts[1])
            risk_value = impact_level * prob_level

            matrix_cells[cell_key] = {
                "impact_level": impact_level,
                "prob_level": prob_level,
                "ri_count": cell_data["ri_count"],
                "rr_count": cell_data["rr_count"],
                "risk_value": risk_value,
                "risk_level": RiskCalculationService.get_risk_level(risk_value),
                "risks": cell_data["risks"],
            }

        return {
            "matrix": matrix_cells,
            "total_cells": len(matrix_cells),
        }

    @classmethod
    def get_risk_journey_data(cls, assessment_id: Optional[str] = None) -> List[Dict]:
        if assessment_id:
            mappings = AssetThreatMapping.get_by_assessment(assessment_id)
        else:
            mappings = AssetThreatMapping.get_all()

        journeys = []
        for mapping in mappings:
            if mapping.risk_inherent is None or mapping.residual_risk is None:
                continue

            asset = Asset.get_by_id(mapping.asset_id)
            asset_name = asset.name if asset else "Unknown"

            ri_impact = mapping.impact or 0
            ri_prob = mapping.probability

            rr_impact = mapping.residual_risk / ri_prob if ri_prob > 0 else 0
            rr_prob = mapping.probability

            ri_pos = cls._get_matrix_position(ri_impact, ri_prob)
            rr_pos = cls._get_matrix_position(rr_impact, rr_prob)

            journeys.append({
                "id": mapping.id,
                "asset_name": asset_name,
                "risk_inherent": mapping.risk_inherent,
                "residual_risk": mapping.residual_risk,
                "maturity": mapping.maturity,
                "maturity_display": round(mapping.maturity * 100, 1),
                "ri_position": ri_pos,
                "rr_position": rr_pos,
                "reduction": round(mapping.risk_inherent - mapping.residual_risk, 2),
                "reduction_percent": round((mapping.risk_inherent - mapping.residual_risk) / mapping.risk_inherent * 100, 1) if mapping.risk_inherent > 0 else 0,
            })

        journeys.sort(key=lambda x: x["reduction"], reverse=True)
        return journeys

    @classmethod
    def _get_matrix_position(cls, impact: float, probability: int) -> Dict:
        impact_rounded = max(1, min(5, round(impact)))
        return {
            "row": 6 - impact_rounded,
            "col": probability,
            "cell": f"{impact_rounded}-{probability}",
            "impact": impact_rounded,
            "probability": probability,
        }

    @classmethod
    def get_dashboard_data(cls, assessment_id: Optional[str] = None) -> Dict:
        return {
            "summary": cls.get_executive_summary(assessment_id),
            "matrix": cls.get_risk_matrix_data(assessment_id),
            "journey": cls.get_risk_journey_data(assessment_id),
        }