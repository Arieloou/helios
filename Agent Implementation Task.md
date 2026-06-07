# Helios - Agent Implementation Task Plan

Based on Implementation Plan.md requirements analysis.

---

## Summary of Implemented vs Unimplemented

| Module | Status | Requirements |
|--------|--------|--------------|
| Encryption Service | ✅ Implemented | RNF-01 |
| Basic Auth Controller | ⚠️ Partial (needs DB + RBAC) | RF-01, RF-02 |
| Asset Controller | ⚠️ Partial (no DB, no CID) | RF-06, RF-07 |
| **Assessment Management** | ❌ Not implemented | RF-03, RF-04, RF-05 |
| **Asset CID Valuation** | ❌ Not implemented | RF-06, RF-07, RF-08, RF-09 |
| **MAGIRIT Risk Mapping** | ❌ Not implemented | RF-10, RF-11, RF-12 |
| **ISO Audit & Maturity** | ❌ Not implemented | RF-13, RF-14, RF-15 |
| **Risk Recalculation** | ❌ Not implemented | RF-16 |
| **Ollama AI Copilot** | ❌ Not implemented | RF-17 |
| **Treatment Plans** | ❌ Not implemented | RF-18, RF-19, RF-20 |
| **Executive Dashboards** | ❌ Not implemented | RF-21, RF-22, RF-23 |

---

## Agent 1: Assessment Management Agent

**Description**: Implement the Evaluation Management module (Gestión de Evaluaciones) for contextual isolation.

**Requirements**: RF-03, RF-04, RF-05; CU-02

### Backend (Flask):
1. **Assessment Model** (`app_core/app/models/assesment.py`):
   - Fields: `id`, `name`, `description`, `period`, `status` (active/archived/closed), `created_by`, `created_at`, `updated_at`, `closed_at`
   - Relationships: user creator, assets, mappings, controls, treatments

2. **Assessment Service** (`app_core/app/services/assessment_service.py`):
   - CRUD operations for assessments
   - Context isolation logic (set active assessment, filter by active assessment)
   - Status transitions (archive, close)

3. **Assessment Controller** (`app_core/app/controllers/assessment_controller.py`):
   - Routes: list, create, edit, delete, select_active, archive, close

### Frontend (Jinja2):
4. **Templates**:
   - `app_core/app/templates/assessments/index.html` - List all assessments with status badges
   - `app_core/app/templates/assessments/create.html` - Create new assessment form
   - `app_core/app/templates/assessments/edit.html` - Edit assessment
   - `app_core/app/templates/assessments/select.html` - Select active assessment

---

## Agent 2: Asset Management with CID Agent

**Description**: Implement inventory management with CID valuation (Confidenciality, Integrity, Availability).

**Requirements**: RF-06, RF-07, RF-08, RF-09; CU-03, CU-04

### Backend (Flask):
1. **Asset Model** (`app_core/app/models/asset.py`):
   - Fields: `id`, `assessment_id`, `name`, `asset_type`, `description`, `confidentiality` (1-5), `integrity` (1-5), `availability` (1-5), `v_total` (calculated), `created_at`, `updated_at`
   - Relationships: assessment, asset_threat_mappings

2. **Asset Service** (`app_core/app/services/asset_service.py`):
   - CRUD operations
   - V_total calculation: `V_total = max(C, I, D)`
   - Batch import from CSV validation

3. **Asset Controller** (`app_core/app/controllers/assetcontroller.py`):
   - Enhance existing routes with DB operations
   - Add: edit, delete, import_csv

4. **Import Service** (`app_core/app/services/import_service.py`):
   - CSV validation and batch import
   - Error reporting (valid/invalid records)

### Frontend (Jinja2):
5. **Templates**:
   - Update `app_core/app/templates/assets/index.html` - Add CID columns, V_total, filters
   - Update `app_core/app/templates/assets/create.html` - Add CID sliders (1-5)
   - Add `app_core/app/templates/assets/edit.html`
   - Add `app_core/app/templates/assets/import.html` - CSV upload

---

## Agent 3: MAGERIT Risk Mapping Agent

**Description**: Implement the risk mapping engine with threat/vulnerability relationships.

**Requirements**: RF-10, RF-11, RF-12; CU-05

### Backend (Flask):
1. **Data Models** (`app_core/app/models/risk_models.py`):
   - `Threat`: id, name, category, description (from MAGERIT catalog)
   - `Vulnerability`: id, name, category, description (from ISO 27001)
   - `AssetThreatMapping`: id, asset_id, threat_id, probability (P: 1-5), degradation (D: 0-1), impact (I), risk_inherent (RI)

2. **Risk Service** (`app_core/app/services/magerit_service.py`):
   - Create mapping relationships (Asset → Threat → Vulnerability)
   - Calculate Impact: `I = V_total × D`
   - Calculate Risk Inherent: `RI = I × P`
   - Recalculate on changes

3. **Risk Controller** (`app_core/app/controllers/risk_controller.py`):
   - Routes: list_mappings, create_mapping, edit_mapping, delete_mapping

4. **Catalog Data** (`app_core/app/data/catalogs.py`):
   - Seed data for threats (MAGIRIT) and vulnerabilities (ISO 27001)

### Frontend (Jinja2):
5. **Templates**:
   - `app_core/app/templates/risk/mappings.html` - List all mappings with RI scores
   - `app_core/app/templates/risk/create_mapping.html` - Select asset, threat, vulnerability, P, D
   - `app_core/app/templates/risk/matrix.html` - Risk matrix view

---

## Agent 4: ISO Audit & Maturity Agent

**Description**: Implement ISO 27002 questionnaire generation and maturity calculation.

**Requirements**: RF-13, RF-14, RF-15; CU-06

### Backend (Flask):
1. **ISO Data Models** (`app_core/app/models/iso_models.py`):
   - `ISOControl`: id, control_id, domain, title, description
   - `ControlQuestion`: id, control_id, question_text, options (JSON)
   - `ControlResponse`: id, assessment_id, control_id, question_id, response, score
   - `ControlMaturity`: id, assessment_id, control_id, maturity_percentage (0-1)

2. **ISO Service** (`app_core/app/services/iso27002_service.py`):
   - Generate contextual questionnaire based on vulnerability mappings
   - Calculate maturity: `M = sum(scores) / max_possible_score`
   - Map vulnerabilities to applicable ISO controls

3. **ISO Controller** (`app_core/app/controllers/iso_controller.py`):
   - Routes: get_questionnaire, save_response, save_partial, calculate_maturity

4. **Control Catalog** (`app_core/app/data/iso_controls.py`):
   - Seed ISO 27002:2022 controls with questions

### Frontend (Jinja2):
5. **Templates**:
   - `app_core/app/templates/iso/questionnaire.html` - Dynamic questionnaire by control
   - `app_core/app/templates/iso/response_form.html` - Answer questions with partial save
   - `app_core/app/templates/iso/maturity_report.html` - Maturity percentage per control

---

## Agent 5: Risk Recalculation Engine Agent

**Description**: Implement reactive risk recalculation for residual risk.

**Requirements**: RF-16; RNF-03

### Backend (Flask):
1. **Reactive Service** (`app_core/app/services/risk_recalculation_service.py`):
   - Track dependency chains: control → mapping → asset
   - On maturity change: recalculate RR = RI × (1 - M) for affected mappings
   - Batch recalculation for all mappings in assessment
   - Event-driven triggers (not polling)

2. **Residual Risk Model** (`app_core/app/models/risk_models.py`):
   - Add to `AssetThreatMapping`: `residual_risk` (RR), `maturity` (M)

3. **Risk Calculation Service** (`app_core/app/services/risk_calculation_service.py`):
   - Centralize formulas: V_total, I, RI, RR
   - Recalculation methods

4. **Signal/Event System** (`app_core/app/services/event_system.py`):
   - Emit events on: maturity_changed, mapping_updated, asset_modified
   - Subscribe services to react

### Frontend (Jinja2):
5. **Templates**:
   - Update existing views to show RR alongside RI
   - Add visual indicators for risk reduction (color change RI→RR)

---

## Agent 6: Ollama AI Copilot Agent

**Description**: Implement local AI analysis for asset coherence and recommendations.

**Requirements**: RF-17; RNF-02; CU-07

### Backend (Flask):
1. **Ollama Client** (`app_core/app/services/ollama_client.py`):
   - Connect to local Ollama API (localhost:11434)
   - Generate prompts from asset data
   - Parse AI responses

2. **AI Analysis Service** (`app_core/app/services/ai_analysis_service.py`):
   - Compile asset JSON: {name, C, I, D, v_total, threats, vulnerabilities, maturity_scores}
   - Send to Ollama with system prompt
   - Extract: coherence observations, control recommendations
   - Error handling for Ollama unavailable

3. **Ollama Controller** (`app_core/app/controllers/ai_controller.py`):
   - Route: `/ai/analyze/<asset_id>`
   - Async processing (return immediately, poll for results)

### Frontend (Jinja2):
4. **Templates**:
   - Add "Analyze with AI" button to asset detail view
   - `app_core/app/templates/ai/analysis_result.html` - Display AI observations
   - `app_core/app/templates/ai/loading.html` - Loading state

---

## Agent 7: Treatment Plans Agent

**Description**: Implement risk treatment plans with task management.

**Requirements**: RF-18, RF-19, RF-20; CU-08

### Backend (Flask):
1. **Treatment Models** (`app_core/app/models/treatment_models.py`):
   - `TreatmentPlan`: id, assessment_id, mapping_id, strategy (mitigate/accept/transfer), status, created_at
   - `TreatmentTask`: id, plan_id, description, responsible, due_date, status (pending/in_progress/completed), progress_percentage

2. **Treatment Service** (`app_core/app/services/treatment_service.py`):
   - Identify unacceptable risks (RR > threshold, zone red)
   - Create treatment plans with strategy
   - Update task status and progress

3. **Treatment Controller** (`app_core/app/controllers/treatment_controller.py`):
   - Routes: list_unacceptable_risks, create_plan, update_plan, list_tasks, update_task

4. **Risk Classifier** (`app_core/app/services/risk_classifier.py`):
   - Classify risk levels: Low (1-4), Medium (5-9), High (10-16), Critical (17-25)
   - Zone mapping for 5x5 matrix

### Frontend (Jinja2):
5. **Templates**:
   - `app_core/app/templates/treatment/risks.html` - List unacceptable risks
   - `app_core/app/templates/treatment/create_plan.html` - Select strategy
   - `app_core/app/templates/treatment/tasks.html` - Task board with status
   - `app_core/app/templates/treatment/task_detail.html` - Update progress

---

## Agent 8: Executive Dashboards Agent

**Description**: Implement 5x5 risk matrix visualization and risk journey.

**Requirements**: RF-21, RF-22, RF-23; CU-09

### Backend (Flask):
1. **Dashboard Service** (`app_core/app/services/dashboard_service.py`):
   - Aggregate data: all mappings, RI, RR by assessment
   - Calculate matrix positions: (Impact × Probability)
   - Export data for Power BI (JSON/CSV)

2. **Dashboard Controller** (`app_core/app/controllers/dashboard_controller.py`):
   - Routes: overview, matrix_view, risk_journey, export_data
   - Filter by active assessment

3. **Export Service** (`app_core/app/services/export_service.py`):
   - Generate CSV/JSON exports
   - Power BI compatible format

### Frontend (Jinja2):
4. **Templates**:
   - `app_core/app/templates/dashboard/overview.html` - Executive summary
   - `app_core/app/templates/dashboard/matrix.html` - 5x5 heatmap visualization
   - `app_core/app/templates/dashboard/risk_journey.html` - RI→RR movement visualization
   - `app_core/app/templates/dashboard/export.html` - Export options

5. **JavaScript**:
   - Canvas/SVG rendering for 5x5 matrix
   - Animated risk journey (arrows from RI to RR positions)

---

## Agent 9: Auth & RBAC Enhancement Agent

**Description**: Enhance authentication with proper database, RBAC, and security features.

**Requirements**: RF-01, RF-02; CU-01; RNF-01, RNF-12

### Backend (Flask):
1. **Enhanced User Model** (`app_core/app/models/user.py`):
   - Fields: id, username, email, password_hash, role (admin/agent), is_active, failed_attempts, locked_until, created_at
   - Relationships: created_assessments

2. **Auth Service** (`app_core/app/services/auth_service.py`):
   - Password hashing with bcrypt
   - Login validation with rate limiting (max 5 attempts, lock 15 min)
   - Session management with Flask-Login
   - Role verification

3. **RBAC Decorators** (`app_core/app/services/rbac.py`):
   - `@login_required` - Verify authenticated
   - `@role_required(['admin', 'agent'])` - Verify role
   - Permission checks for resources

4. **User Controller** (`app_core/app/controllers/user_controller.py`):
   - Admin CRUD: create_user, list_users, edit_user, deactivate_user

### Frontend (Jinja2):
5. **Templates**:
   - Update `app_core/app/templates/auth/login.html` - Add error handling, rate limit messages
   - `app_core/app/templates/auth/register.html` - Admin creates users
   - `app_core/app/templates/users/index.html` - User management (Admin only)
   - Update `app_core/app/templates/base.html` - Show role-based menu items

---

## Agent 10: Database & Infrastructure Agent

**Description**: Set up PostgreSQL, SQLAlchemy, and application factory.

**Requirements**: RNF-06, RNF-07, RNF-09

### Backend (Flask):
1. **Database Configuration** (`app_core/app/database.py`):
   - SQLAlchemy engine, session, base
   - PostgreSQL connection via environment variables

2. **Models Base** (`app_core/app/models/base.py`):
   - Base model with timestamps, soft delete

3. **Migration Scripts** (`app_core/migrations/`):
   - Alembic or Flask-Migrate setup
   - Initial migration for all tables

4. **Application Factory Update** (`app_core/app/__init__.py`):
   - Initialize DB, login manager
   - Register all blueprints

---

## Implementation Order Recommendation

```
Phase 1: Foundation
├── Agent 10: Database & Infrastructure
└── Agent 9: Auth & RBAC Enhancement

Phase 2: Core Modules
├── Agent 1: Assessment Management
└── Agent 2: Asset Management with CID

Phase 3: Risk Calculation
├── Agent 3: MAGERIT Risk Mapping
├── Agent 4: ISO Audit & Maturity
└── Agent 5: Risk Recalculation Engine

Phase 4: Advanced Features
├── Agent 6: Ollama AI Copilot
├── Agent 7: Treatment Plans
└── Agent 8: Executive Dashboards
```

---

## Risk Calculation Formulas (MAGIRIT)

- **Valor total del activo**: `V_total = máx(Confidencialidad, Integridad, Disponibilidad)`
- **Impacto**: `I = V_total × Degradación (D)` donde D se captura como un porcentaje (0 a 1)
- **Riesgo Inherente**: `RI = I × Probabilidad (P)` donde P se captura en una escala de 1 a 5
- **Riesgo Residual**: `RR = RI × (1 − Madurez (M))` donde M se calcula dinámicamente a partir de los cuestionarios ISO

---

## System Actors

- **Administrador**: Gestiona usuarios, configuración del sistema y el ciclo de vida de las evaluaciones; puede consultar los dashboards y los resultados del análisis.
- **Agente de Seguridad de la Información**: Ejecuta el análisis de riesgos de extremo a extremo — inventario y valoración de activos, mapeo de amenazas y vulnerabilidades, cuestionarios de madurez, planes de tratamiento y consulta de dashboards.