# HELIOS
Application service for the security assessment of assets using Magerit methodologies and the ISO 27002:2022 standard.

## Technologies

| Layer | Technology |
|-------|------------|
| Backend (Core) | Flask 3.1+ |
| Backend (Encryption) | FastAPI 0.136+, Uvicorn |
| Database | PostgreSQL (via SQLAlchemy) |
| gRPC | gRPC, Protobuf |
| Encryption | Cryptography |
| Configuration | Pydantic Settings, Python Dotenv |
| External AI | Ollama (LLM integration) |

## Project Structure
```
helios/
├── app_core/                    # Main Flask Application
│   ├── app/
│   │   ├── __init__.py          # Application Factory
│   │   ├── extensions.py        # DB (SQLAlchemy) & Migrations
│   │   │
│   │   ├── models/
│   │   │   ├── user.py          # User & Role tables (Admin, Agent, Supervisor)
│   │   │   ├── asset.py         # Information Assets table
│   │   │   └── assessment.py    # Assessments table (Magerit / ISO 27002)
│   │   │
│   │   ├── controllers/
│   │   │   ├── auth_controller.py   # Login, logout, role-based access
│   │   │   ├── asset_controller.py  # Asset CRUD
│   │   │   └── risk_controller.py   # Risk assessment routes
│   │   │
│   │   ├── services/
│   │   │   ├── magerit_service.py    # Risk calculation & impact (Magerit)
│   │   │   ├── iso27002_service.py   # ISO 27002 control verification
│   │   │   ├── encryption_client.py  # HTTP client to Encryption Service
│   │   │   └── ollama_client.py      # HTTP client to Ollama (AI)
│   │   │
│   │   ├── views/
│   │   │   ├── layouts/            # Base templates (menus, headers)
│   │   │   ├── auth/               # Login screens
│   │   │   └── dashboard/          # Role-based dashboards
│   │   │
│   │   └── static/
│   │       ├── css/
│   │       ├── js/                 # Frontend interactivity
│   │       └── img/
│   │
│   ├── .env                       # Credentials (DB URL, secrets)
│   ├── config.py                  # Environment config (Dev, Prod)
│   ├── requirements.txt           # Python dependencies
│   └── run.py                     # Entry point
│
├── encryption_service/            # FastAPI microservice for encryption
│   ├── main.py
│   ├── requirements.txt
│   └── ...
│
├── .github/                       # GitHub workflows
├── LICENSE
└── README.md
```

