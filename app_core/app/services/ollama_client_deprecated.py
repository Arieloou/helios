import json
import requests
from typing import Dict, Optional


class OllamaClientDeprecated:
    def __init__(self, host: str = "localhost", port: int = 11434, model: str = "llama3.2"):
        self.host = host
        self.port = port
        self.model = model
        self.base_url = f"http://{host}:{port}"

    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def list_models(self) -> list:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [m["name"] for m in data.get("models", [])]
            return []
        except Exception:
            return []

    def generate(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.3,
        max_tokens: int = 500,
    ) -> Dict:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        if system:
            payload["system"] = system

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60,
            )
            if response.status_code == 200:
                return {
                    "success": True,
                    "response": response.json().get("response", ""),
                }
            else:
                return {
                    "success": False,
                    "error": f"Ollama error: {response.status_code}",
                }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "No se pudo conectar al servicio Ollama. Asegúrese de que Ollama esté ejecutándose localmente.",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def analyze_asset(self, asset_data: Dict) -> Dict:
        system_prompt = """Eres un experto en seguridad de la información y gestión de riesgos. Analiza el activo proporcionado y proporciona:
1. Observaciones de coherencia (¿tiene el activo medidas de seguridad apropiadas para su valor?)
2. Recomendaciones de controles ISO 27002 que deberían implementarse
Sé conciso y práctico en tus recomendaciones."""

        prompt = self._build_analysis_prompt(asset_data)

        result = self.generate(prompt=prompt, system=system_prompt)

        if result["success"]:
            response_text = result["response"]
            return {
                "success": True,
                "observations": self._extract_observations(response_text),
                "recommendations": self._extract_recommendations(response_text),
                "raw_response": response_text,
            }
        else:
            return result

    def _build_analysis_prompt(self, asset_data: Dict) -> str:
        return f"""Analiza el siguiente activo de información:

Nombre: {asset_data.get('name', 'N/A')}
Tipo: {asset_data.get('asset_type', 'N/A')}
Descripción: {asset_data.get('description', 'N/A')}

Valoración CID:
- Confidencialidad: {asset_data.get('confidentiality', 'N/A')}/5
- Integridad: {asset_data.get('integrity', 'N/A')}/5
- Disponibilidad: {asset_data.get('availability', 'N/A')}/5
- Valor Total (V_total): {asset_data.get('v_total', 'N/A')}

Riesgo Inherente: {asset_data.get('risk_inherent', 'N/A')}
Riesgo Residual: {asset_data.get('residual_risk', 'N/A')}
Madurez actual: {asset_data.get('maturity_display', 'N/A')}

Proporciona:
1. Observaciones de coherencia (2-3 puntos)
2. Controles ISO 27002 recomendados (3-5 controles)
"""

    def _extract_observations(self, text: str) -> list:
        lines = text.split("\n")
        observations = []
        in_observations = False

        for line in lines:
            if "observación" in line.lower() or "coherencia" in line.lower():
                in_observations = True
                continue
            if in_observations and line.strip():
                if "recomendación" in line.lower() or "control" in line.lower():
                    break
                if line.strip().startswith(("1.", "2.", "3.", "-", "•")):
                    observations.append(line.strip())

        if not observations:
            observations = [l.strip() for l in lines[:3] if l.strip() and len(l.strip()) > 20]

        return observations[:5]

    def _extract_recommendations(self, text: str) -> list:
        lines = text.split("\n")
        recommendations = []
        in_recommendations = False

        for line in lines:
            if "recomendación" in line.lower() or "control" in line.lower():
                in_recommendations = True
                continue
            if in_recommendations and line.strip():
                if line.strip().startswith(("1.", "2.", "3.", "4.", "5.", "-", "•", "A.")):
                    recommendations.append(line.strip())

        if not recommendations:
            for line in lines:
                if "A.5" in line or "A.6" in line or "A.7" in line or "A.8" in line or "A.9" in line:
                    recommendations.append(line.strip())

        return recommendations[:5]


ollama_client_deprecated = OllamaClientDeprecated()