# HELIOS
Application service for the security assessment of assets using Magerit methodologies and the ISO 27002:2022 standard.

## Architectural Features
```
helios_core/
├── app/
│   ├── __init__.py               # Application Factory (Configura Flask)
│   ├── extensions.py             # Instancias de DB (SQLAlchemy) y Migraciones
│   │
│   ├── models/
│   │   ├── user.py               # Tabla de usuarios y roles (Admin, Agente, Supervisor)
│   │   ├── asset.py              # Tabla de activos de información
│   │   └── assessment.py         # Tabla de evaluaciones (Magerit / ISO 27002)
│   │
│   ├── controllers/              
│   │   ├── auth_controller.py    # Login, logout y control de acceso por roles
│   │   ├── asset_controller.py   # CRUD de activos
│   │   └── risk_controller.py    # Rutas para iniciar/ver evaluaciones de riesgo
│   │
│   ├── services/                 
│   │   ├── magerit_service.py    # Lógica de cálculo de riesgos e impacto
│   │   ├── iso27002_service.py   # Lógica de verificación de controles ISO
│   │   ├── encryption_client.py  # [Integración] Cliente HTTP para llamar a FastAPI
│   │   └── ollama_client.py      # [Integración] Cliente HTTP para enviar prompts a Ollama
│   │
│   ├── views/                    
│   │   ├── layouts/              # Plantillas base (menús, cabeceras)
│   │   ├── auth/                 # Pantallas de login
│   │   └── dashboard/            # Paneles de control según el rol del actor
│   │
│   └── static/                   
│       ├── css/
│       ├── js/                   # Scripts para interactividad en el frontend
│       └── img/
│
├── .env                          # Credenciales (URL de Postgres, llaves secretas)
├── config.py                     # Carga de variables de entorno (Dev, Prod)
├── requirements.txt              # Dependencias de Python
└── run.py                        # Script de arranque (Punto de entrada)
```
