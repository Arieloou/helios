import json
from app.models.iso_models import ISOControl, ControlQuestion


# TODO: RF-15 - ISO 27002 Controls via API/MCP
# Future implementation: Integrate with external API or MCP server to fetch
# ISO 27002 control definitions dynamically.
# Example integration point:
# - Replace static ISO_27002_CONTROLS with API-fetched controls
# - Add caching layer for API responses
# - Consider using MCP protocol for standardized control updates


VULNERABILITY_CONTROL_MAP = {
    "Control de acceso": ["A.9.1", "A.9.2", "A.9.4"],
    "Criptografía": ["A.10.1"],
    "Gestión de vulnerabilidades": ["A.12.2"],
    "Seguridad de red": ["A.13.1", "A.11.1", "A.11.2"],
    "Gestión de la continuidad": ["A.12.3", "A.17.1"],
    "Monitorización": ["A.12.1"],
    "Seguridad de los recursos humanos": ["A.7.1", "A.7.2", "A.6.1"],
    "Gestión de la seguridad": ["A.5.1", "A.5.2", "A.6.2"],
    "Relaciones con proveedores": ["A.15.1"],
}


ISO_27002_CONTROLS = [
    {
        "control_id": "A.5.1",
        "domain": "Controles organizacionales",
        "title": "Políticas de seguridad de la información",
        "description": "Políticas y procedimientos de seguridad documentados y aprobados",
    },
    {
        "control_id": "A.5.2",
        "domain": "Controles organizacionales",
        "title": "Revisión de las políticas",
        "description": "Revisión periódica de las políticas de seguridad",
    },
    {
        "control_id": "A.6.1",
        "domain": "Controles organizacionales",
        "title": "Responsabilidad deSeguridad",
        "description": "Definición de responsabilidades de seguridad",
    },
    {
        "control_id": "A.6.2",
        "domain": "Controles organizacionales",
        "title": "Contactos con autoridades",
        "description": "Contactos relevantes con autoridades",
    },
    {
        "control_id": "A.7.1",
        "domain": "Seguridad de recursos humanos",
        "title": "Verificación de antecedentes",
        "description": "Verificación de antecedentes de empleados",
    },
    {
        "control_id": "A.7.2",
        "domain": "Seguridad de recursos humanos",
        "title": "Terminación de responsabilidades",
        "description": "Proceso de salida y devolución de activos",
    },
    {
        "control_id": "A.8.1",
        "domain": "Gestión de activos",
        "title": "Responsabilidad de activos",
        "description": "Inventario y clasificación de activos",
    },
    {
        "control_id": "A.8.2",
        "domain": "Gestión de activos",
        "title": "Clasificación de información",
        "description": "Clasificación según nivel de confidencialidad",
    },
    {
        "control_id": "A.8.3",
        "domain": "Gestión de activos",
        "title": "Manejo de medios",
        "description": "Gestión segura de medios removibles",
    },
    {
        "control_id": "A.9.1",
        "domain": "Control de acceso",
        "title": "Política de control de acceso",
        "description": "Política de control de acceso documentada",
    },
    {
        "control_id": "A.9.2",
        "domain": "Control de acceso",
        "title": "Gestión de acceso de usuarios",
        "description": "Proceso de alta, baja y modificación de usuarios",
    },
    {
        "control_id": "A.9.4",
        "domain": "Control de acceso",
        "title": "Gestión de contraseñas",
        "description": "Políticas de gestión de contraseñas",
    },
    {
        "control_id": "A.10.1",
        "domain": "Criptografía",
        "title": "Controles criptográficos",
        "description": "Uso de criptografía para proteger información",
    },
    {
        "control_id": "A.11.1",
        "domain": "Seguridad física y ambiental",
        "title": "Perímetro de seguridad",
        "description": "Definición de áreas seguras",
    },
    {
        "control_id": "A.11.2",
        "domain": "Seguridad física y ambiental",
        "title": "Seguridad de equipos",
        "description": "Protección de equipos y dispositivos",
    },
    {
        "control_id": "A.12.1",
        "domain": "Operaciones de seguridad",
        "title": "Responsabilidades y procedimientos",
        "description": "Procedimientos documentados de operación",
    },
    {
        "control_id": "A.12.2",
        "domain": "Operaciones de seguridad",
        "title": "Gestión de vulnerabilidades",
        "description": "Gestión de vulnerabilidades técnicas",
    },
    {
        "control_id": "A.12.3",
        "domain": "Operaciones de seguridad",
        "title": "Copias de seguridad",
        "description": "Politica y procedimientos de respaldo",
    },
    {
        "control_id": "A.13.1",
        "domain": "Seguridad de comunicaciones",
        "title": "Gestión de red",
        "description": "Seguridad de redes y comunicaciones",
    },
    {
        "control_id": "A.14.1",
        "domain": "Adquisición y desarrollo",
        "title": "Requisitos de seguridad",
        "description": "Requisitos de seguridad en desarrollo",
    },
    {
        "control_id": "A.14.2",
        "domain": "Adquisición y desarrollo",
        "title": "Desarrollo seguro",
        "description": "Metodología de desarrollo seguro",
    },
    {
        "control_id": "A.15.1",
        "domain": "Relaciones con proveedores",
        "title": "Acuerdos con proveedores",
        "description": "Acuerdos de seguridad con proveedores",
    },
    {
        "control_id": "A.16.1",
        "domain": "Gestión de incidentes",
        "title": "Gestión de incidentes",
        "description": "Procedimientos de gestión de incidentes",
    },
    {
        "control_id": "A.17.1",
        "domain": "Continuidad de negocio",
        "title": "Plan de continuidad",
        "description": "Plan de continuidad del negocio",
    },
    {
        "control_id": "A.18.1",
        "domain": "Cumplimiento",
        "title": "Cumplimiento legal",
        "description": "Cumplimiento de requisitos legales",
    },
]


QUESTIONS_BY_CONTROL = {
    "A.5.1": [
        {"question": "¿Existe una política de seguridad de la información documentada?", "options": [0, 25, 50, 75, 100]},
        {"question": "¿La política está aprobada por la dirección?", "options": [0, 25, 50, 75, 100]},
        {"question": "¿Se comunica a todos los empleados?", "options": [0, 25, 50, 75, 100]},
    ],
    "A.5.2": [
        {"question": "¿Se revisa la política periódicamente?", "options": [0, 25, 50, 75, 100]},
        {"question": "¿Se actualiza según cambios normativos?", "options": [0, 25, 50, 75, 100]},
    ],
    "A.6.1": [
        {"question": "¿Están definidas las responsabilidades de seguridad?", "options": [0, 25, 50, 75, 100]},
        {"question": "¿Existe un responsable de seguridad de la información?", "options": [0, 25, 50, 75, 100]},
    ],
    "A.7.1": [
        {"question": "¿Se verifican los antecedentes de los empleados?", "options": [0, 25, 50, 75, 100]},
        {"question": "¿Se realiza verificación de referencias?", "options": [0, 25, 50, 75, 100]},
    ],
    "A.7.2": [
        {"question": "¿Existe proceso de desvínculo?", "options": [0, 25, 50, 75, 100]},
        {"question": "¿Se revoca el acceso al terminar?", "options": [0, 25, 50, 75, 100]},
    ],
    "A.8.1": [
        {"question": "¿Existe inventario de activos?", "options": [0, 25, 50, 75, 100]},
        {"question": "¿Están identificados los propietarios?", "options": [0, 25, 50, 75, 100]},
    ],
    "A.8.2": [
        {"question": "¿Existe clasificación de información?", "options": [0, 25, 50, 75, 100]},
        {"question": "¿Se maneja información confidencial安全的?", "options": [0, 25, 50, 75, 100]},
    ],
    "A.9.1": [
        {"question": "¿Existe política de control de acceso?", "options": [0, 25, 50, 75, 100]},
        {"question": "¿Se define el acceso por roles?", "options": [0, 25, 50, 75, 100]},
    ],
    "A.9.2": [
        {"question": "¿Existe proceso de gestión de usuarios?", "options": [0, 25, 50, 75, 100]},
        {"question": "¿Se revisa el acceso periódicamente?", "options": [0, 25, 50, 75, 100]},
    ],
    "A.9.4": [
        {"question": "¿Existe política de contraseñas?", "options": [0, 25, 50, 75, 100]},
        {"question": "¿Se exige complejidad de contraseñas?", "options": [0, 25, 50, 75, 100]},
    ],
    "A.10.1": [
        {"question": "¿Se usa cifrado para datos sensibles?", "options": [0, 25, 50, 75, 100]},
        {"question": "¿Están definidas las claves criptográficas?", "options": [0, 25, 50, 75, 100]},
    ],
    "A.11.1": [
        {"question": "¿Existe definición de áreas seguras?", "options": [0, 25, 50, 75, 100]},
        {"question": "¿Hay control de acceso físico?", "options": [0, 25, 50, 75, 100]},
    ],
    "A.11.2": [
        {"question": "¿Están protegidos los equipos?", "options": [0, 25, 50, 75, 100]},
        {"question": "¿Existe política de escritorio limpio?", "options": [0, 25, 50, 75, 100]},
    ],
    "A.12.1": [
        {"question": "¿Están documentados los procedimientos?", "options": [0, 25, 50, 75, 100]},
        {"question": "¿Hay separación de funciones?", "options": [0, 25, 50, 75, 100]},
    ],
    "A.12.2": [
        {"question": "¿Se escanean vulnerabilidades?", "options": [0, 25, 50, 75, 100]},
        {"question": "¿Se aplican parches de seguridad?", "options": [0, 25, 50, 75, 100]},
    ],
    "A.12.3": [
        {"question": "¿Se realizan backups?", "options": [0, 25, 50, 75, 100]},
        {"question": "¿Se prueba el restore?", "options": [0, 25, 50, 75, 100]},
    ],
    "A.13.1": [
        {"question": "¿Está segmentada la red?", "options": [0, 25, 50, 75, 100]},
        {"question": "¿Se usa firewall?", "options": [0, 25, 50, 75, 100]},
    ],
    "A.14.1": [
        {"question": "¿Se consideran requisitos de seguridad?", "options": [0, 25, 50, 75, 100]},
        {"question": "¿Se incluyen en el diseño?", "options": [0, 25, 50, 75, 100]},
    ],
    "A.15.1": [
        {"question": "¿Hay acuerdos con proveedores?", "options": [0, 25, 50, 75, 100]},
        {"question": "¿Se incluyen cláusulas de seguridad?", "options": [0, 25, 50, 75, 100]},
    ],
    "A.16.1": [
        {"question": "¿Existe proceso de gestión de incidentes?", "options": [0, 25, 50, 75, 100]},
        {"question": "¿Se reportan los incidentes?", "options": [0, 25, 50, 75, 100]},
    ],
    "A.17.1": [
        {"question": "¿Existe plan de continuidad?", "options": [0, 25, 50, 75, 100]},
        {"question": "¿Se prueban los planes?", "options": [0, 25, 50, 75, 100]},
    ],
    "A.18.1": [
        {"question": "¿Se cumplen los requisitos legales?", "options": [0, 25, 50, 75, 100]},
        {"question": "¿Se protege la información personal?", "options": [0, 25, 50, 75, 100]},
    ],
}


_catalogs_initialized = False


def initialize_iso_catalogs():
    global _catalogs_initialized
    if _catalogs_initialized:
        return
    
    for control_data in ISO_27002_CONTROLS:
        control = ISOControl(
            control_id=control_data["control_id"],
            domain=control_data["domain"],
            title=control_data["title"],
            description=control_data["description"],
        )
        
        questions = QUESTIONS_BY_CONTROL.get(control_data["control_id"], [])
        for q in questions:
            ControlQuestion(
                control_id=control.control_id,
                question_text=q["question"],
                options=json.dumps(q["options"]),
            )
    
    _catalogs_initialized = True


def get_controls() -> list:
    initialize_iso_catalogs()
    return [c.to_dict() for c in ISOControl.get_all()]


def get_domains() -> list:
    initialize_iso_catalogs()
    return ISOControl.get_domains()


def get_controls_by_domain(domain: str) -> list:
    initialize_iso_catalogs()
    return [c.to_dict() for c in ISOControl.get_by_domain(domain)]


def get_questions_by_control(control_id: str) -> list:
    initialize_iso_catalogs()
    return [q.to_dict() for q in ControlQuestion.get_by_control(control_id)]