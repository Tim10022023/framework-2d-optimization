# Copilot Instructions for 2D Optimization Framework

This is an educational tool for teaching 2D optimization. Students optimize a blackbox function while instructors monitor progress, analyze paths, and reveal results after sessions end.

## Project Structure

```
framework-2d-optimization/
├─ backend/          # FastAPI REST API + SQLite persistence
├─ frontend/         # React + TypeScript + Vite
├─ bot/              # Python client library + student bot template
├─ docs/             # User guides
├─ docker-compose.yaml
└─ Dockerfile
```

**Key insight**: This is a **full-stack application** with clear separation. Backend is a REST API (no server-side rendering); frontend is a client-side React app. The bot/ directory is independent Python code for students to run locally.

## Build, Test & Lint

### Quick Build with Health Checks (Recommended)
```powershell
# Full build pipeline: dependencies → linting → type-check → tests → Docker build
python build.py
```
This runs all checks before building Docker images. Fails fast on any issues.

### Backend (Python/FastAPI)
```powershell
cd backend

# Install dependencies
pip install -r requirements.txt

# Run tests (all)
pytest tests/

# Run single test
pytest tests/test_api.py::test_health -v

# Run API (with auto-reload for development)
python -m uvicorn app.main:app --reload

# Check API health
curl http://localhost:8000/health
# Full API docs: http://localhost:8000/docs
```

**Note**: Tests use pytest + pytest-asyncio + httpx for async testing.

### Frontend (React/TypeScript/Vite)
```powershell
cd frontend

# Install dependencies
npm install

# Development server
npm run dev   # Runs at http://localhost:5173

# Build production
npm run build

# Lint code
npm run lint   # Runs before Docker build

# Type check (catch TypeScript errors early)
npx tsc --noEmit
```

### Full Stack (Docker Compose)
```powershell
# Build and start services with health checks
docker compose up --build

# Services become available at:
# - Frontend: http://localhost:5173
# - Backend API: http://localhost:8000
# - Swagger docs: http://localhost:8000/docs

# Verify services are healthy
python health_check.py
```

**Health checks are automatic**: Both services include health checks. Docker will restart containers that become unhealthy.

### Python Bot
```powershell
cd bot
pip install -r requirements.txt

# Edit SESSION_CODE in student_bot_template.py first
python student_bot_template.py
```

## High-Level Architecture

### Backend (FastAPI)

**Database**: SQLite + SQLAlchemy ORM
- Location: `backend/app.db` (persisted)
- Models: `backend/app/db/models.py`
- Database session setup: `backend/app/db/session.py`

**API Routes** (`backend/app/api/`):
- `functions.py`: List available 2D optimization functions (e.g., Sphere, Rosenbrock, Rastrigin)
- `sessions.py`: Core endpoints for session lifecycle, joining, evaluating points, leaderboards, snapshots, exports

**Core Logic**:
- Function evaluation is handled server-side for blackbox secrecy
- Sessions track:
  - Participants (humans) and Bots (internal: Random Search, Hill Climb; external: student bots)
  - Individual clicks/evaluations with (x, y, z) tuples
  - Max steps per session (configurable)
  - Status (created, running, ended)
- Snapshots capture path state for step-by-step inspection
- Reveal shows function contour/surface plot after session ends
- Exports return full session data as JSON

**Available Functions**: Sphere, Booth, Himmelblau, Rosenbrock, Eggholder, Rastrigin, Schwefel, Levy, Griewank (negated/shifted), Easom

### Frontend (React + TypeScript)

**Build tool**: Vite with React SWC plugin (fast)

**Routing**: React Router DOM (simple single-page app)
- `/` → Home (teacher/participant join)
- Teacher views: create session, monitor active session, inspect paths
- Participant views: join session, place points, see leaderboard

**Component Organization** (`frontend/src/components/`):
- Teacher panels: TeacherCreatePanel.tsx, TeacherActiveSessionPanel.tsx, TeacherInspectPanel.tsx, ExportPanel.tsx
- Participant/shared: ParticipantPanel.tsx, LeaderboardPanel.tsx, PointsListPanel.tsx, StatsPanel.tsx
- Plotting: FunctionContourPlot.tsx, FunctionSurfacePlot.tsx, PlotCanvas.tsx (uses plotly.js)
- Utilities: StatusBar.tsx

**State Management**: 
- sessionStorage for tab-local session ID and role (teacher/participant)
- API calls via `src/api.ts` (fetch-based, no external state library)

**Key Libraries**:
- plotly.js for interactive 2D/3D plots
- qrcode.react for generating QR codes
- React Router for navigation

**Environment Variables** (`frontend/.env`):
```
VITE_API_URL=http://localhost:8000
VITE_PUBLIC_APP_URL=http://localhost:5173
VITE_TEACHER_PIN=CHANGE_ME
```

### Python Bot Client

**`bot/blackbox_client.py`**: Simple HTTP client library for interfacing with the API
- `join_session(code)`: Register as a bot
- `propose_point(x, y)`: Submit a point and get evaluation result

**`bot/student_bot_template.py`**: Template for students to implement their optimization algorithm
- Students only modify `propose_point(x, y)` method
- Runs in a loop until max_steps reached or session ends

**`bot/stress_test.py`**: Utility for load testing (spawns multiple bot instances in parallel)

## Key Conventions & Patterns

### Backend

**Request/Response Pattern**:
- All endpoints return JSON (Pydantic models auto-serialize)
- Error responses use appropriate HTTP status codes (400, 404, 500)
- No custom error handling framework—FastAPI/HTTPException used directly

**Session State Machine**:
- Status values: "created", "running", "ended"
- Transitions: created → running (all participants ready) → ended (teacher action)
- Only evaluate points when status="running"

**Naming**:
- Database tables are plural (sessions, participants, evaluations)
- API endpoints are REST-style (POST /sessions, GET /sessions/{code})
- Model classes match table names (Session, Participant, Evaluation)

### Frontend

**Component Naming**: Descriptive, PascalCase (e.g., TeacherCreatePanel, FunctionContourPlot)

**Props Pattern**: 
- Props are typed explicitly (no any types)
- Avoid prop drilling—keep component hierarchy shallow when possible

**Styling**:
- CSS modules not used; global CSS in `src/index.css` and per-file CSS imports
- No tailwind or CSS-in-JS framework

**API Integration**:
- Calls happen in useEffect hooks
- No loading states/error boundaries implemented—add these when enhancing
- sessionStorage for persisting user context across browser reloads

**TypeScript Patterns**:
- types.ts exports all shared types
- Strict mode enabled in tsconfig.app.json
- React components typed as `React.FC<Props>`

### Environment & Configuration

**Docker**:
- Single Dockerfile at root (multi-stage, builds both backend and frontend)
- docker-compose.yaml defines services with volume mounts for persistence
- Database persisted at `opt2d_data` volume (maps to `/app/backend/data`)
- CORS configured via `BACKEND_CORS_ORIGINS` environment variable

**Database Migration**: 
- No migration tool (Alembic not used)
- Models defined in SQLAlchemy; tables created on app startup via `Base.metadata.create_all(bind=engine)`
- Add new migrations by modifying models and restarting

## Testing Notes

- Backend tests are in `backend/tests/`
- No frontend tests currently configured
- Load testing via `bot/stress_test.py` (run independently, outside Docker)

## Health Checks & Verification

**Automated health checks run:**
1. **During Docker build** (linting, type-check, tests)
   - Frontend: ESLint and TypeScript type checking before Docker image creation
   - Build script (`build.py`): Runs all tests and linting before Docker build
2. **During Docker runtime** (service health monitoring)
   - Backend: Checks `/health` endpoint every 10s
   - Frontend: Checks HTTP 200 response every 10s
   - Containers auto-restart if unhealthy

**Manual health verification:**
```powershell
# After starting services
python health_check.py

# Or check individual endpoints
curl http://localhost:8000/health         # Backend
curl http://localhost:5173                # Frontend
curl http://localhost:8000/docs           # API Swagger docs
```

**Build and verification workflow:**
```powershell
# 1. Run full build with checks
python build.py

# 2. Start services
docker compose up

# 3. Verify everything is healthy
python health_check.py
```

## Common Tasks

**Adding a new function**:
1. Implement function in `backend/app/core/` (create new file or add to existing)
2. Register in `backend/app/api/functions.py` (GET /functions endpoint)
3. Add corresponding reveal image to `backend/app/static/function_images/`

**Debugging a session**:
1. Use teacher "Inspect" panel to step through a participant's or bot's path
2. Use browser DevTools to inspect sessionStorage (session code, role)
3. Check backend logs: `python -m uvicorn app.main:app --reload` shows all requests

**Scaling considerations**:
- ~5–10 bots run stably; 20+ bots show slowdowns
- SQLite suitable for this scale; upgrade to PostgreSQL for larger deployments
- No async optimizations in evaluator—requests are sequential per session

---

**For deeper context**, see:
- `README.md` for project overview and quick start
- `dev_log.md` for technical decisions, stresstest results, and skalierung notes
- `docs/` folder for user guides (participant, teacher, student-bot)
