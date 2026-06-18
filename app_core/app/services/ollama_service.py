from typing import Dict, List, Optional
import requests

from app.models.asset import Asset
from app.models.risk_models import AssetThreatMapping
from app.models.iso_models import ControlMaturity
from app.services.assessment_service import AssessmentService


class OllamaService:
    OLLAMA_URL = "http://localhost:11434/api/generate"
    DEFAULT_MODEL = "llama2"

    @classmethod
    def is_available(cls) -> bool:
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    @classmethod
    def compile_asset_context(cls, asset_id: str) -> Dict:
        asset = Asset.get_by_id(asset_id)
        if not asset:
            return {"error": "Activo no encontrado"}

        context = {
            "asset_name": asset.name,
            "asset_type": asset.asset_type,
            "description": asset.description,
            "confidentiality": asset.confidentiality,
            "integrity": asset.integrity,
            "availability": asset.availability,
            "v_total": asset.v_total,
            "mappings": [],
            "controls_maturity": [],
        }

        mappings = AssetThreatMapping.get_by_asset(asset_id)
        for mapping in mappings:
            mapping_data = {
                "threat_id": mapping.threat_id,
                "vulnerability_id": mapping.vulnerability_id,
                "probability": mapping.probability,
                "impact": mapping.impact,
                "risk_inherent": mapping.risk_inherent,
                "risk_residual": mapping.residual_risk,
            }
            context["mappings"].append(mapping_data)

        return context

    @classmethod
    def get_asset_recommendations(cls, asset_id: str) -> Dict:
        if not cls.is_available():
            return {
                "success": False,
                "error": "Ollama no está disponible. Asegúrese de que el servicio esté ejecutándose en localhost:11434",
            }

        context = cls.compile_asset_context(asset_id)
        if "error" in context:
            return {"success": False, "error": context["error"]}

        prompt = cls._build_recommendation_prompt(context)

        try:
            response = requests.post(
                cls.OLLAMA_URL,
                json={"model": cls.DEFAULT_MODEL, "prompt": prompt, "stream": False},
                timeout=60,
            )

            if response.status_code == 200:
                result = response.json()
                recommendations = cls._parse_recommendations(result.get("response", ""))
                return {
                    "success": True,
                    "recommendations": recommendations,
                    "asset_context": context,
                }
            else:
                return {
                    "success": False,
                    "error": f"Error de Ollama: {response.status_code}",
                }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "No se pudo conectar a Ollama",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    @classmethod
    def _build_recommendation_prompt(cls, context: Dict) -> str:
        mappings_summary = ""
        if context.get("mappings"):
            for m in context["mappings"]:
                mappings_summary += f"""
- Probabilidad: {m.get('probability')}, Impacto: {m.get('impact')}, RI: {m.get('risk_inherent')}, RR: {m.get('risk_residual')}
"""

        prompt = f"""Analiza el siguiente activo y proporciona recomendaciones de seguridad:

Nombre del Activo: {context.get('asset_name')}
Tipo: {context.get('asset_type')}
Descripción: {context.get('description')}

Valoración CID:
- Confidencialidad: {context.get('confidentiality')}/5
- Integridad: {context.get('integrity')}/5
- Disponibilidad: {context.get('availability')}/5
- Valor Total: {context.get('v_total')}

Mapeos de Riesgo:
{mappings_summary}

Basado en este contexto, proporciona:
1. Identificación de vulnerabilidades principales
2. Controles ISO 27002 recomendados ( formato: A.X.X )
3. Acciones prioritarias de tratamiento

Sé conciso y práctico.
"""
        return prompt

    @classmethod
    def _parse_recommendations(cls, response_text: str) -> List[str]:
        lines = response_text.split("\n")
        recommendations = []

        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith("-") or line.startswith("•")):
                clean_line = line.lstrip("0123456789.-•) ").strip()
                if len(clean_line) > 10:
                    recommendations.append(clean_line)

        return recommendations[:10] if recommendations else [response_text[:500]]


ollama_service = OllamaService()