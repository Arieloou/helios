from typing import Dict, List, Optional
import json

from app.models.iso_models import ISOControl, ControlQuestion, ControlResponse, ControlMaturity
from app.models.risk_models import AssetThreatMapping
from app.services.assessment_service import AssessmentService


class ISO27002Service:
    @classmethod
    def get_controls(cls) -> List[Dict]:
        from app.data.iso_controls import get_controls
        return get_controls()

    @classmethod
    def get_domains(cls) -> List[str]:
        from app.data.iso_controls import get_domains
        return get_domains()

    @classmethod
    def get_questions(cls, control_id: str) -> List[Dict]:
        from app.data.iso_controls import get_questions_by_control
        return get_questions_by_control(control_id)

    @classmethod
    def get_questionnaire_for_assessment(cls, assessment_id: Optional[str] = None) -> List[Dict]:
        if not assessment_id:
            active = AssessmentService.get_active()
            if active:
                assessment_id = active["id"]
        
        if not assessment_id:
            return []
        
        mappings = AssetThreatMapping.get_by_assessment(assessment_id)
        
        applicable_controls = set()
        for mapping in mappings:
            applicable_controls.add("A.5.1")
            applicable_controls.add("A.5.2")
            applicable_controls.add("A.6.1")
            applicable_controls.add("A.7.1")
            applicable_controls.add("A.7.2")
            applicable_controls.add("A.8.1")
            applicable_controls.add("A.8.2")
            applicable_controls.add("A.9.1")
            applicable_controls.add("A.9.2")
            applicable_controls.add("A.9.4")
            applicable_controls.add("A.10.1")
            applicable_controls.add("A.11.1")
            applicable_controls.add("A.11.2")
            applicable_controls.add("A.12.1")
            applicable_controls.add("A.12.2")
            applicable_controls.add("A.12.3")
        
        controls = []
        for control_id in sorted(applicable_controls):
            control = ISOControl.get_by_control_id(control_id)
            if control:
                questions = ControlQuestion.get_by_control(control_id)
                responses = ControlResponse.get_by_control(assessment_id, control_id)
                
                response_map = {r.question_id: r for r in responses}
                
                control_data = control.to_dict()
                control_data["questions"] = [q.to_dict() for q in questions]
                control_data["answered_questions"] = len(response_map)
                control_data["total_questions"] = len(questions)
                
                maturity = ControlMaturity.calculate_maturity(assessment_id, control_id)
                control_data["maturity"] = maturity
                control_data["maturity_display"] = round(maturity * 100, 1)
                
                controls.append(control_data)
        
        return controls

    @classmethod
    def save_response(
        cls,
        assessment_id: str,
        control_id: str,
        question_id: str,
        response: int,
    ) -> Dict:
        question = ControlQuestion.get_by_id(question_id)
        if not question:
            raise ValueError(f"Pregunta no encontrada: {question_id}")
        
        options = json.loads(question.options)
        if response not in options:
            raise ValueError(f"Respuesta inválida. Opciones válidas: {options}")
        
        existing = ControlResponse.get_by_question(assessment_id, question_id)
        
        if existing:
            existing.response = response
            existing.score = response / 100.0
        else:
            ControlResponse(
                assessment_id=assessment_id,
                control_id=control_id,
                question_id=question_id,
                response=response,
                score=response / 100.0,
            )
        
        maturity = ControlMaturity.calculate_maturity(assessment_id, control_id)
        
        existing_maturity = ControlMaturity.get_by_control(assessment_id, control_id)
        if existing_maturity:
            existing_maturity.maturity_percentage = maturity
        else:
            ControlMaturity(
                assessment_id=assessment_id,
                control_id=control_id,
                maturity_percentage=maturity,
            )
        
        return {"maturity": maturity, "maturity_display": round(maturity * 100, 1)}

    @classmethod
    def get_maturity_by_control(cls, assessment_id: str, control_id: str) -> Dict:
        maturity = ControlMaturity.get_by_control(assessment_id, control_id)
        if maturity:
            return maturity.to_dict()
        
        control = ISOControl.get_by_control_id(control_id)
        if not control:
            return {"maturity_percentage": 0.0, "maturity_percentage_display": 0.0}
        
        calc_maturity = ControlMaturity.calculate_maturity(assessment_id, control_id)
        return {
            "control_id": control_id,
            "maturity_percentage": calc_maturity,
            "maturity_percentage_display": round(calc_maturity * 100, 1),
        }

    @classmethod
    def get_maturity_report(cls, assessment_id: Optional[str] = None) -> Dict:
        if not assessment_id:
            active = AssessmentService.get_active()
            if active:
                assessment_id = active["id"]
        
        if not assessment_id:
            return {"controls": [], "overall_maturity": 0}
        
        controls = ISOControl.get_all()
        maturity_data = []
        total_maturity = 0.0
        
        for control in controls:
            m = cls.get_maturity_by_control(assessment_id, control.control_id)
            maturity_data.append({
                "control_id": control.control_id,
                "title": control.title,
                "domain": control.domain,
                "maturity": m["maturity_percentage"],
                "maturity_display": m["maturity_percentage_display"],
            })
            total_maturity += m["maturity_percentage"]
        
        overall = total_maturity / len(controls) if controls else 0
        
        return {
            "assessment_id": assessment_id,
            "controls": maturity_data,
            "overall_maturity": round(overall, 2),
            "overall_maturity_display": round(overall * 100, 1),
        }

    @classmethod
    def get_maturity_by_domain(cls, assessment_id: str) -> Dict:
        domains = cls.get_domains()
        result = {}
        
        for domain in domains:
            controls = ISOControl.get_by_domain(domain)
            domain_maturity = 0.0
            count = 0
            
            for control in controls:
                m = cls.get_maturity_by_control(assessment_id, control.control_id)
                domain_maturity += m["maturity_percentage"]
                count += 1
            
            avg = domain_maturity / count if count > 0 else 0
            result[domain] = {
                "maturity": avg,
                "maturity_display": round(avg * 100, 1),
                "controls_count": count,
            }
        
        return result