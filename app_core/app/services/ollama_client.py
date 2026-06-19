import json
import time
from typing import Dict, List, Optional

import requests


# ---------------------------------------------------------------------------
# Esquema JSON que el modelo DEBE respetar. Ollama (>= 0.5.0) restringe la
# generación para que coincida con este esquema, eliminando el parseo de texto.
# ---------------------------------------------------------------------------
ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "observaciones": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "punto": {"type": "string"},
                    "severidad": {
                        "type": "string",
                        "enum": ["baja", "media", "alta"],
                    },
                },
                "required": ["punto", "severidad"],
            },
            "minItems": 2,
            "maxItems": 4,
        },
        "controles_recomendados": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},            # p.ej. "A.8.5"
                    "nombre": {"type": "string"},         # p.ej. "Autenticación segura"
                    "justificacion": {"type": "string"},
                },
                "required": ["id", "nombre", "justificacion"],
            },
            "minItems": 3,
            "maxItems": 5,
        },
    },
    "required": ["observaciones", "controles_recomendados"],
}


class OllamaClient:
    def __init__(self, host: str = "localhost", port: int = 11434, model: str = "llama3.2"):
        self.host = host
        self.port = port
        self.model = model
        self.base_url = f"http://{host}:{port}"
    # ----------------------------- nivel bajo -----------------------------

    def _chat(
        self,
        messages: List[Dict],
        temperature: float = 0.1,
        num_predict: int = 900,
        fmt: Optional[Dict] = None,
        retries: int = 2,
    ) -> Dict:
        """Llama a /api/chat con reintentos. Los parámetros del modelo van
        DENTRO de 'options' (no en el nivel superior del payload)."""
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": num_predict,   # <-- 'num_predict', NO 'max_tokens'
            },
        }
        if fmt is not None:
            payload["format"] = fmt           # esquema JSON o la cadena "json"

        last_err = None
        for attempt in range(retries + 1):
            try:
                r = requests.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                    timeout=60,
                )
                if r.status_code == 200:
                    return {
                        "success": True,
                        "response": r.json()["message"]["content"],
                    }
                last_err = f"Ollama error {r.status_code}: {r.text[:200]}"
            except requests.exceptions.ConnectionError:
                return {
                    "success": False,
                    "error": (
                        "No se pudo conectar a Ollama. ¿Está ejecutándose en "
                        f"{self.base_url}? Inicie el servicio con 'ollama serve'."
                    ),
                }
            except requests.exceptions.Timeout:
                last_err = "Tiempo de espera agotado al consultar al modelo."
            except Exception as e:  # noqa: BLE001
                last_err = str(e)

            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))  # backoff sencillo

        return {"success": False, "error": last_err}

    def health_check(self) -> bool:
        """Verifica que Ollama responde y que el modelo está descargado."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            return response.status_code == 200
        except requests.exceptions.ConnectionError:
            return False

    # ----------------------------- nivel alto -----------------------------

    def analyze_asset(self, asset_data: Dict) -> Dict:
        system_prompt = (
            "Eres un consultor experto en seguridad de la información, gestión "
            "de riesgos e ISO/IEC 27001:2022. Analizas activos de información y "
            "recomiendas controles del Anexo A de ISO/IEC 27001:2022 "
            "(equivalente a ISO/IEC 27002:2022).\n\n"
            "Reglas estrictas:\n"
            "- Los controles SOLO pertenecen a cuatro temas: A.5 "
            "(Organizacionales), A.6 (Personas), A.7 (Físicos) y A.8 "
            "(Tecnológicos). En la versión 2022 NO existen A.9 ni superiores; "
            "nunca los inventes.\n"
            "- Usa siempre el identificador completo, p.ej. 'A.8.5 Autenticación "
            "segura'.\n"
            "- Prioriza los controles según la valoración CID y el riesgo "
            "residual del activo.\n"
            "- Sé conciso, técnico y práctico. Responde EXCLUSIVAMENTE con el "
            "JSON solicitado, sin texto adicional ni explicaciones fuera del JSON."
        )

        user_prompt = self._build_analysis_prompt(asset_data)

        result = self._chat(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,     # baja => recomendaciones más deterministas
            num_predict=900,
            fmt=ANALYSIS_SCHEMA,
        )

        if not result["success"]:
            return result

        try:
            data = json.loads(result["response"])
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "El modelo no devolvió JSON válido.",
                "raw_response": result["response"],
            }

        return {
            "success": True,
            "observations": data.get("observaciones", []),
            "recommendations": data.get("controles_recomendados", []),
            "raw_response": result["response"],
        }

    def _build_analysis_prompt(self, asset_data: Dict) -> str:
        return f"""Analiza el siguiente activo de información y devuelve el JSON solicitado.

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

Tarea:
1. Observaciones de coherencia: ¿las medidas de seguridad son proporcionales al
   valor y al riesgo del activo? Señala desajustes (sobreprotección o
   infraprotección) según la valoración CID.
2. Recomienda entre 3 y 5 controles del Anexo A de ISO 27001:2022, cada uno con
   su identificador, nombre y una justificación breve ligada a ESTE activo.
"""

    def list_models(self) -> list:
            try:
                response = requests.get(f"{self.base_url}/api/tags", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    return [m["name"] for m in data.get("models", [])]
                return []
            except Exception:
                return []

ollama_client = OllamaClient()
