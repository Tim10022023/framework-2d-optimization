# Architecture & Technical Reference

This document describes the system architecture, code organization, and technical conventions.

## Project Structure

```
framework-2d-optimization/
├─ backend/              # FastAPI REST API + SQLite persistence
│  ├─ app/
│  │  ├─ api/            # API route handlers (functions, sessions)
│  │  ├─ core/           # Core logic (function evaluator, session store)
│  │  ├─ db/             # Database (models, session)
│  │  └─ main.py         # FastAPI app setup
│  ├─ tests/             # pytest test suite
│  └─ requirements.txt
├─ frontend/             # React + TypeScript + Vite
│  ├─ src/
│  │  ├─ components/     # React components (panels, plots)
│  │  ├─ api.ts          # HTTP client for backend
│  │  ├─ types.ts        # TypeScript type definitions
│  │  └─ App.tsx         # Main React component
│  ├─ index.html
│  └─ package.json
├─ bot/                  # Python client library & student bot template
│  ├─ blackbox_client.py # HTTP client for API
│  ├─ student_bot_template.py # Template for student algorithms
│  ├─ stress_test.py     # Load testing utility
│  └─ requirements.txt
├─ docs/                 # User guides & documentation
├─ build.py             # CI/CD build orchestrator
├─ health_check.py      # Service health verification
└─ docker-compose.yaml  # Full stack orchestration
```

## Build, Test & Lint

### Full Build Pipeline
```powershell
python build.py
```
This runs: backend tests → frontend lint → TypeScript check → Docker build

### Backend (FastAPI + Python)
```powershell
cd backend
pip install -r requirements.txt
pytest tests/                    # Run all tests
python -m uvicorn app.main:app --reload  # Run API
```

### Frontend (React + TypeScript + Vite)
```powershell
cd frontend
npm install
npm run dev                  # Development server
npm run build               # Production build
npm run lint                # Lint code
npx tsc --noEmit           # Type check
```

### Docker Compose
```powershell
docker compose up           # Start services (local development)
docker compose up --build   # Rebuild images
```

## High-Level Architecture

### Backend (FastAPI)

**Database**: SQLite + SQLAlchemy ORM
- Location: `backend/app.db`
- Models in `backend/app/db/models.py`
- Tables: sessions, participants, evaluations, snapshots

**Core Logic** (`backend/app/core/`):
- `store.py`: Session management, participant tracking, leaderboard computation
- `functions.py`: 2D function evaluators (Sphere, Rosenbrock, etc.)

**API Routes** (`backend/app/api/`):
- `functions.py`: GET /functions - list available optimization functions
- `sessions.py`: Session lifecycle (create, join, evaluate, leaderboard, export, end)

**Key Endpoints**:
- `POST /sessions` - Create session
- `GET /sessions/{code}/public` - Get session info (for bots)
- `POST /sessions/{code}/join` - Join as participant
- `POST /sessions/{code}/evaluate` - Evaluate point (x, y)
- `GET /sessions/{code}/leaderboard` - Get current rankings
- `GET /sessions/{code}/snapshot` - Get step-by-step path
- `GET /sessions/{code}/export` - Export full session data
- `POST /sessions/{code}/end` - End session (teacher only)

**Session State Machine**:
- Status: "created" → "running" → "ended"
- Only evaluate points when status="running"
- Max steps per session configurable at creation

### Frontend (React + TypeScript + Vite)

**Routing**: Single-page app with React Router
- `/` - Home (teacher/participant login)
- Teacher mode: Create, monitor, inspect sessions
- Participant mode: Join, click points, view leaderboard

**Components** (`frontend/src/components/`):
- `TeacherCreatePanel.tsx` - Session creation
- `TeacherActiveSessionPanel.tsx` - Live monitoring
- `TeacherInspectPanel.tsx` - Step-by-step path analysis
- `ParticipantPanel.tsx` - Point clicking interface
- `LeaderboardPanel.tsx` - Rankings display
- `FunctionContourPlot.tsx` - 2D heatmap visualization
- `FunctionSurfacePlot.tsx` - 3D surface visualization

**State Management**:
- `sessionStorage` for tab-local session ID and role
- API calls via `src/api.ts` (fetch-based)
- No external state library (Redux, Zustand, etc.)

**Key Libraries**:
- Vite - Build tool with HMR
- React Router - Navigation
- plotly.js - Interactive plots
- qrcode.react - QR code generation

**Environment** (`frontend/.env`):
```
VITE_API_URL=http://localhost:8000
VITE_TEACHER_PIN=CHANGE_ME
```

### Python Bot Client

**`bot/blackbox_client.py`**: HTTP client library
- `join_session(name, is_bot=True)` - Register with session
- `evaluate(x, y)` - Submit point and get evaluation
- `get_public_info()` - Fetch session info

**`bot/student_bot_template.py`**: Template for student algorithms
- Students implement `propose_point(step, history, best_z) → (x, y)`
- Automatically handles join, evaluate loop, error handling

**`bot/stress_test.py`**: Load testing utility
- Spawns N concurrent bots
- Tracks timing, errors, success rate
- Reports throughput metrics

## Design Patterns & Conventions

### Backend

**REST Conventions**:
- All endpoints return JSON (Pydantic models)
- Error responses use HTTP status codes (400, 404, 409, 500)
- No custom error framework—FastAPI HTTPException directly

**Database**:
- No migrations (Alembic not used)
- Tables created on startup via `Base.metadata.create_all()`
- Foreign keys use participant IDs and session codes

**API Design**:
- Admin operations (end session, export) require `x_admin_token` header
- Session code is always in URL path
- All mutable operations are POST, reads are GET

### Frontend

**Component Patterns**:
- Named exports, PascalCase filenames
- Props typed explicitly (no `any`)
- Hooks for state/effects (useEffect, useState, useMemo)
- Shallow component hierarchy (avoid prop drilling)

**Styling**:
- Global CSS in `src/index.css`
- Per-component CSS imports (no CSS modules)
- No tailwind or CSS-in-JS framework

**TypeScript**:
- Strict mode enabled
- `types.ts` exports all shared types
- Components typed as `React.FC<Props>`

## Health Checks

**Two-layer approach:**

1. **Build-time checks** (`build.py`):
   - Backend: `pytest tests/`
   - Frontend: `npm run lint` + `tsc --noEmit`
   - Docker: Build both images
   - Fails fast on first error

2. **Runtime checks** (Docker Compose):
   - Backend: `curl http://localhost:8000/health` every 10s
   - Frontend: HTTP 200 response every 10s
   - Auto-restarts on failure

**Manual verification**:
```powershell
python health_check.py         # Quick service check
python full_health_check.py    # Full integration test
```

## Available Optimization Functions

- **Sphere** (shifted)
- **Booth**
- **Himmelblau**
- **Rosenbrock**
- **Eggholder**
- **Rastrigin** (shifted)
- **Schwefel**
- **Levy**
- **Griewank** (negated/shifted for maximization)
- **Easom**

Reveal images stored in `backend/app/static/function_images/`

## Deployment

### Local Docker
```powershell
python build.py                 # Validate & build
docker compose up               # Run services
python health_check.py          # Verify health
```

### Production (Tar Export)
```powershell
docker image save opt2d-backend:latest -o backend.tar
docker image save opt2d-frontend:latest -o frontend.tar
# Upload tars to server, then:
docker image load -i backend.tar
docker image load -i frontend.tar
docker compose -f docker-compose.upload.yaml up
```

See `deployment_portainer.md` for server setup details.

## Performance & Scaling

**Tested & Verified**:
- ✅ 25 concurrent UI users: ~100ms response time (snappy)
- ✅ 50 concurrent bots: 100% success, ~325ms per request
- ✅ 100 concurrent bots: 100% success, ~700ms per request
- ✅ 200 concurrent bots: 100% success, ~1.4s per request

**Bottlenecks** (SQLite + synchronous):
- Sequential request processing per session
- SQLite concurrent write limitations
- No async/parallel evaluation

**Suitable for**: Classrooms (5-50 students), demo/workshops

**For higher load**: Upgrade to PostgreSQL + async backend, add load balancing

## Common Tasks

**Add new optimization function**:
1. Implement in `backend/app/core/functions.py`
2. Register in `backend/app/api/functions.py`
3. Add reveal image to `backend/app/static/function_images/`

**Debug a session**:
1. Use teacher "Inspect" panel to step through path
2. Check browser DevTools → sessionStorage for session ID
3. Run backend locally: `python -m uvicorn app.main:app --reload`
4. Check API docs: `http://localhost:8000/docs`

**Deploy updates**:
1. Make code changes
2. Run `python build.py` (validates everything)
3. Export images to tars
4. Upload to server
5. Load images and run compose
