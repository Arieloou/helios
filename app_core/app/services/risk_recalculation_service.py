from typing import Dict, List, Optional

from app.models.risk_models import AssetThreatMapping
from app.models.iso_models import ControlMaturity
from app.services.risk_calculation_service import RiskCalculationService


class RiskRecalculationService:
    _subscribers: Dict[str, List] = {
        "maturity_changed": [],
        "mapping_updated": [],
        "asset_modified": [],
    }

    @classmethod
    def subscribe(cls, event_type: str, callback):
        if event_type not in cls._subscribers:
            cls._subscribers[event_type] = []
        cls._subscribers[event_type].append(callback)

    @classmethod
    def emit(cls, event_type: str, data: Dict):
        if event_type in cls._subscribers:
            for callback in cls._subscribers[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"Error en callback de evento {event_type}: {e}")

    @classmethod
    def on_maturity_changed(cls, data: Dict):
        assessment_id = data.get("assessment_id")
        control_id = data.get("control_id")
        maturity = data.get("maturity", 0.0)

        if not assessment_id:
            return

        mappings = AssetThreatMapping.get_by_assessment(assessment_id)
        count = 0

        for mapping in mappings:
            mapping.set_maturity(maturity)
            count += 1

        cls.emit("maturity_changed", {
            "assessment_id": assessment_id,
            "control_id": control_id,
            "maturity": maturity,
            "mappings_updated": count,
        })

    @classmethod
    def recalculate_for_assessment(cls, assessment_id: str) -> Dict:
        mappings = AssetThreatMapping.get_by_assessment(assessment_id)
        control_maturities = ControlMaturity.get_by_assessment(assessment_id)

        maturity_by_control = {m.control_id: m.maturity_percentage for m in control_maturities}

        count = 0
        for mapping in mappings:
            control_id = mapping.vulnerability_id[:5]
            if control_id in maturity_by_control:
                mapping.set_maturity(maturity_by_control[control_id])
            else:
                mapping.set_maturity(0.0)
            count += 1

        summary = RiskCalculationService.get_risk_summary(assessment_id)

        return {
            "assessment_id": assessment_id,
            "mappings_updated": count,
            "summary": summary,
        }

    @classmethod
    def get_mappings_with_residual_risk(cls, assessment_id: Optional[str] = None) -> List[Dict]:
        if assessment_id:
            mappings = AssetThreatMapping.get_by_assessment(assessment_id)
        else:
            mappings = AssetThreatMapping.get_all()

        result = []
        for mapping in mappings:
            data = mapping.to_dict()
            result.append(data)

        return result

    @classmethod
    def get_unacceptable_risks(cls, assessment_id: Optional[str] = None, threshold: float = 10.0) -> List[Dict]:
        mappings = cls.get_mappings_with_residual_risk(assessment_id)

        unacceptable = []
        for mapping in mappings:
            rr = mapping.get("residual_risk")
            if rr and rr >= threshold:
                unacceptable.append(mapping)

        return unacceptable

    @classmethod
    def recalculate_on_response_save(cls, assessment_id: str, control_id: str) -> Dict:
        maturity = ControlMaturity.calculate_maturity(assessment_id, control_id)

        existing = ControlMaturity.get_by_control(assessment_id, control_id)
        if existing:
            existing.maturity_percentage = maturity

        cls.on_maturity_changed({
            "assessment_id": assessment_id,
            "control_id": control_id,
            "maturity": maturity,
        })

        return {
            "control_id": control_id,
            "maturity": maturity,
            "maturity_display": round(maturity * 100, 1),
        }