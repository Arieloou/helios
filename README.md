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

## Getting Started

### Prerequisites

- **Python 3.12+**
- **PostgreSQL 16+** (local installation or Docker container)
- **Ollama** (optional, for AI features)

### 1. Set Up the Virtual Environment

```bash
cd helios/app_core
python -m venv .venv
```

### 2. Install Dependencies

```powershell
# Windows (PowerShell)
& ".venv\Scripts\python.exe" -m pip install -r requirements.txt
```

```bash
# Linux / macOS
.venv/bin/python -m pip install -r requirements.txt
```

### 3. Configure Environment Variables

Edit the `.env` file in `app_core/` with your PostgreSQL credentials:

```env
SECRET_KEY=cambiar-esta-clave-en-produccion
FLASK_PORT=5000
FLASK_DEBUG=true
ENCRYPTION_SERVICE_HOST='your_host'
ENCRYPTION_SERVICE_PORT=50051

DB_HOST='your_host'
DB_PORT=5432
DB_NAME=helios
DB_USER=postgres
DB_PASSWORD='your_postgres_password'
```

### 4. Create the Database

The `helios` database must exist in PostgreSQL **before** running migrations.

#### Option A — Using psycopg2 (no extra tools needed)

```powershell
# Windows (PowerShell)
& ".venv\Scripts\python.exe" -c "import psycopg2; from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT; conn = psycopg2.connect(host='localhost', port=5432, user='postgres', password='your_postgres_password'); conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT); conn.cursor().execute('CREATE DATABASE helios'); conn.close(); print('Database helios created successfully')"
```

#### Option B — Using psql

```bash
psql -U postgres -c "CREATE DATABASE helios;"
```

#### Option C — Using pgAdmin

Open pgAdmin, connect to your PostgreSQL server, and create a new database named `helios`.

### 5. Initialize and Run Migrations

```powershell
# Initialize the migrations directory (only the first time)
& ".venv\Scripts\python.exe" -m flask db init

# Generate migration files based on models
& ".venv\Scripts\python.exe" -m flask db migrate -m "Initial migration"

# Apply migrations to the database
& ".venv\Scripts\python.exe" -m flask db upgrade
```

> **Note:** On Linux/macOS, replace `& ".venv\Scripts\python.exe"` with `.venv/bin/python`.

### 6. Run the Application

```powershell
# Windows (PowerShell)
& ".venv\Scripts\python.exe" run.py
```

```bash
# Linux / macOS
.venv/bin/python run.py
```

The application will be available at `http://127.0.0.1:5000`.

## Database with Docker

If you prefer to run PostgreSQL from a Docker container, create a `docker-compose.yml` in the project root:

```yaml
services:
  postgres:
    image: postgres:16-alpine
    container_name: helios_db
    restart: unless-stopped
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: helios
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: your_postgres_password
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d helios"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  pgdata:
```

```bash
# Start the container
docker compose up -d

# Verify the container is healthy
docker compose ps

# Check logs
docker compose logs -f postgres

# Stop the container
docker compose down
```

> **Important:** When using Docker, the `POSTGRES_DB: helios` variable automatically creates the database on first startup. No manual creation is needed.
