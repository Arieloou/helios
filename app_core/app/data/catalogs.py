from app.models.risk_models import Threat, Vulnerability


MAGIRIT_THREATS = [
    {"name": "Desastre natural", "category": "Físico", "description": "Incendio, inundación, terremoto, etc."},
    {"name": "Fallo de оборудования", "category": "Físico", "description": "Fallos de hardware, servidores,redes"},
    {"name": "Interrupción de servicios", "category": "Físico", "description": "Corte de energía, agua, telecomunicaciones"},
    {"name": "Acceso no autorizado", "category": "Lógico", "description": "Intrusión, acceso indebido a sistemas"},
    {"name": "Malware", "category": "Lógico", "description": "Virus, ransomware, spyware, troyanos"},
    {"name": "Ataque de red", "category": "Lógico", "description": "DDoS, inyección SQL, XSS"},
    {"name": "Ingeniería social", "category": "Lógico", "description": "Phishing, suplantación de identidad"},
    {"name": "Uso indebido", "category": "Lógico", "description": "Acceso no autorizado a datos o recursos"},
    {"name": "Robo de información", "category": "Lógico", "description": "Exfiltración de datos sensibles"},
    {"name": "Modificación no autorizada", "category": "Lógico", "description": "Alteración de datos o configuraciones"},
    {"name": "Negación de servicio", "category": "Lógico", "description": "DoS, DDoS que impide acceso"},
    {"name": "Espionaje industrial", "category": "Humano", "description": "Espionaje por competidores o estados"},
    {"name": "Empleado discontento", "category": "Humano", "description": "Sabotaje, robo,恶意行为"},
    {"name": "Error humano", "category": "Humano", "description": "Configuración incorrecta, borrado accidental"},
    {"name": "Fuga de información", "category": "Humano", "description": "Divulgación accidental de datos"},
]

ISO27001_VULNERABILITIES = [
    {"name": "Falta de control de acceso", "category": "Control de acceso", "description": "Ausencia de controles de acceso apropiados"},
    {"name": "Contraseñas débiles", "category": "Control de acceso", "description": "Políticas de contraseñas insuficientes"},
    {"name": "Sin cifrado de datos", "category": "Criptografía", "description": "Datos sensibles sin cifrar"},
    {"name": "Claves criptográficas débiles", "category": "Criptografía", "description": "Algoritmos o длины clave insuficientes"},
    {"name": "Software desactualizado", "category": "Gestión de vulnerabilidades", "description": "Parches de seguridad no aplicados"},
    {"name": "Falta de firewall", "category": "Seguridad de red", "description": "Red sin protección perimetral"},
    {"name": "Puertos abiertos", "category": "Seguridad de red", "description": "Servicios innecesarios expuestos"},
    {"name": "Sin backups", "category": "Gestión de la continuidad", "description": "No hay copias de seguridad"},
    {"name": "Falta de monitorización", "category": "Monitorización", "description": "Sin registro ni auditoría de eventos"},
    {"name": "Personal no capacitado", "category": "Seguridad de los recursos humanos", "description": "Falta de formación en seguridad"},
    {"name": "Sin política de seguridad", "category": "Gestión de la seguridad", "description": "Ausencia de normas y políticas"},
    {"name": "Falta de segmentación", "category": "Seguridad de red", "description": "Red plana sin segmentación"},
    {"name": "Contratos sin cláusulas de seguridad", "category": "Relaciones con proveedores", "description": "Acuerdos sin requisitos de seguridad"},
    {"name": "Dispositivos sin bloquear", "category": "Control de acceso", "description": "Equipos sin sesión bloqueada"},
    {"name": "Registro de eventos insuficiente", "category": "Monitorización", "description": "No se registran eventos de seguridad"},
]

_catalogs_initialized = False


def initialize_catalogs():
    global _catalogs_initialized
    if _catalogs_initialized:
        return
    
    for threat_data in MAGIRIT_THREATS:
        Threat(
            name=threat_data["name"],
            category=threat_data["category"],
            description=threat_data["description"],
        )
    
    for vuln_data in ISO27001_VULNERABILITIES:
        Vulnerability(
            name=vuln_data["name"],
            category=vuln_data["category"],
            description=vuln_data["description"],
        )
    
    _catalogs_initialized = True


def get_threats() -> list:
    initialize_catalogs()
    return [t.to_dict() for t in Threat.get_all()]


def get_threat_categories() -> list:
    initialize_catalogs()
    categories = set(t.category for t in Threat.get_all())
    return sorted(list(categories))


def get_threats_by_category(category: str) -> list:
    initialize_catalogs()
    return [t.to_dict() for t in Threat.get_by_category(category)]


def get_vulnerabilities() -> list:
    initialize_catalogs()
    return [v.to_dict() for v in Vulnerability.get_all()]


def get_vulnerability_categories() -> list:
    initialize_catalogs()
    categories = set(v.category for v in Vulnerability.get_all())
    return sorted(list(categories))


def get_vulnerabilities_by_category(category: str) -> list:
    initialize_catalogs()
    return [v.to_dict() for v in Vulnerability.get_by_category(category)]