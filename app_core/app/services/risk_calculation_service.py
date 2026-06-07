from typing import Dict, List, Optional

from app.models.asset import Asset
from app.models.risk_models import AssetThreatMapping
from app.models.iso_models import ControlMaturity


class RiskCalculationService:
    @staticmethod
    def calculate_v_total(confidentiality: int, integrity: int, availability: int) -> int:
        return max(confidentiality, integrity, availability)

    @staticmethod
    def calculate_impact(v_total: int, degradation: float) -> float:
        return v_total * degradation

    @staticmethod
    def calculate_risk_inherent(impact: float, probability: int) -> float:
        return impact * probability

    @staticmethod
    def calculate_residual_risk(risk_inherent: float, maturity: float) -> float:
        return risk_inherent * (1 - maturity)

    @staticmethod
    def get_risk_level(risk_value: float) -> str:
        if risk_value >= 17:
            return "Crítico"
        elif risk_value >= 10:
            return "Alto"
        elif risk_value >= 5:
            return "Medio"
        else:
            return "Bajo"

    @staticmethod
    def get_risk_color(risk_value: float) -> str:
        if risk_value >= 17:
            return "#f44336"
        elif risk_value >= 10:
            return "#ff9800"
        elif risk_value >= 5:
            return "#ffc107"
        else:
            return "#4caf50"

    @classmethod
    def calculate_mapping_risk(cls, mapping_id: str, v_total: int) -> Dict:
        mapping = AssetThreatMapping.get_by_id(mapping_id)
        if not mapping:
            raise ValueError(f"Mapeo no encontrado: {mapping_id}")

        impact = cls.calculate_impact(v_total, mapping.degradation)
        ri = cls.calculate_risk_inherent(impact, mapping.probability)
        rr = cls.calculate_residual_risk(ri, mapping.maturity)

        return {
            "impact": round(impact, 2),
            "risk_inherent": round(ri, 2),
            "maturity": mapping.maturity,
            "maturity_display": round(mapping.maturity * 100, 1),
            "residual_risk": round(rr, 2),
            "risk_level": cls.get_risk_level(ri),
            "residual_risk_level": cls.get_risk_level(rr),
        }

    @classmethod
    def recalculate_all_residual_risks(cls, assessment_id: Optional[str] = None) -> int:
        if assessment_id:
            mappings = AssetThreatMapping.get_by_assessment(assessment_id)
        else:
            mappings = AssetThreatMapping.get_all()

        count = 0
        for mapping in mappings:
            if mapping.risk_inherent is not None:
                mapping.calculate_residual_risk()
                count += 1

        return count

    @classmethod
    def get_risk_matrix_position(cls, impact: float, probability: int) -> Dict:
        impact_rounded = round(impact)
        impact_rounded = max(1, min(5, impact_rounded))

        return {
            "row": 6 - impact_rounded,
            "col": probability,
            "cell": f"{impact_rounded}-{probability}",
        }

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
                "avg_residual_risk": 0,
                "max_residual_risk": 0,
                "avg_maturity": 0,
            }

        ri_values = [m.risk_inherent for m in mappings if m.risk_inherent is not None]
        rr_values = [m.residual_risk for m in mappings if m.residual_risk is not None]
        m_values = [m.maturity for m in mappings]

        return {
            "total_mappings": len(mappings),
            "avg_risk_inherent": round(sum(ri_values) / len(ri_values), 2) if ri_values else 0,
            "max_risk_inherent": max(ri_values) if ri_values else 0,
            "avg_residual_risk": round(sum(rr_values) / len(rr_values), 2) if rr_values else 0,
            "max_residual_risk": max(rr_values) if rr_values else 0,
            "avg_maturity": round(sum(m_values) / len(m_values), 2) if m_values else 0,
            "avg_maturity_display": round((sum(m_values) / len(m_values) * 100), 1) if m_values else 0,
        }

    @classmethod
    def apply_maturity_to_mappings(cls, assessment_id: str, control_id: str, maturity: float) -> int:
        mappings = AssetThreatMapping.get_by_assessment(assessment_id)

        count = 0
        for mapping in mappings:
            mapping.set_maturity(maturity)
            count += 1

        return count