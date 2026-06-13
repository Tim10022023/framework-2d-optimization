# Gemini CLI: Framework 2D Optimization

Interactive educational platform for teaching 2D optimization concepts through a "black box" game.

## Project Overview

- **Core Purpose:** Students optimize unknown 2D functions by clicking points or submitting algorithms. Instructors monitor progress and reveal the function landscape after the session ends.
- **Backend:** FastAPI (Python), SQLAlchemy 2.0 (Async), PostgreSQL, Pydantic.
- **Frontend:** React (TypeScript), Vite, Plotly.js for 2D/3D visualizations.
- **Infrastructure:** Docker & Docker Compose for orchestration.
- **Clients:** Python-based student bot template and stress testing utilities.

## Core Mandates & Technical Standards

- **Backend Logic:** Core business logic (session state, function evaluation) resides in `backend/app/core/`. Routers in `backend/app/api/` should remain thin.
- **Database:** Uses PostgreSQL with asynchronous execution via `asyncpg`. Models are defined in `backend/app/db/models.py`.
- **Frontend State:** Managed via standard React hooks (`useState`, `useMemo`, `useEffect`). No global state library (Redux/Zustand) is used; keep it that way for simplicity.
- **Visualization:** Plotly.js is used for both 2D heatmap (`FunctionContourPlot`) and 3D surface (`FunctionSurfacePlot`) views.
- **Communication:** Frontend communicates with the backend via `frontend/src/api.ts` (fetch-based).

## Building and Running

### Full Pipeline (Recommended)
```powershell
docker compose up --build      # Builds and starts Postgres (5432), backend (8000), and frontend (5173)
```

### Local Development (Manual)
- **Database:** Requires a running PostgreSQL instance at `localhost:5432`.
- **Backend:**
  ```powershell
  cd backend
  pip install -r requirements.txt
  python -m uvicorn app.main:app --reload
  ```
- **Frontend:**
  ```powershell
  cd frontend
  npm install
  npm run dev
  ```
- **Verification:**
  ```powershell
  python scripts/health_check.py
  ```

## Directory Structure

```text
framework-2d-optimization/
├── backend/            # FastAPI REST API
│   ├── app/
│   │   ├── api/        # Endpoint definitions (functions, sessions)
│   │   ├── core/       # Evaluators, store, and session logic
│   │   ├── db/         # SQLite models and session setup
│   │   └── static/     # Reveal images for optimization functions
│   └── tests/          # Pytest suite
├── frontend/           # React + Vite application
│   ├── src/
│   │   ├── components/ # UI panels and Plotly visualizations
│   │   ├── api.ts      # API client
│   │   └── types.ts    # Shared TypeScript definitions
├── bot/                # Python client and student templates
├── docs/               # Architecture, Guides, and Deployment notes
├── scripts/            # Build, health check, and workspace scripts
└── docker-compose.yaml # Service orchestration
```

## Development Workflow

1.  **Backend Changes:** Update `backend/app/core/` for logic or `backend/app/api/` for endpoints. Always run `pytest backend/tests/` before committing.
2.  **Frontend Changes:** Update `frontend/src/components/`. Ensure types match `backend/app/api/` models. Run `npm run lint` and `npx tsc --noEmit` to verify.
3.  **New Functions:** Implement the function in `backend/app/core/functions.py`, register it in `backend/app/api/functions.py`, and add a reveal image to `backend/app/static/function_images/`.
4.  **Testing:** Use `bot/stress_test.py` to verify backend performance under load (target: 50+ concurrent bots).

## Testing & Quality Assurance

- **Unit Tests:** `backend/tests/test_api.py` covers core session lifecycle.
- **Linting:** Frontend uses ESLint (`npm run lint`).
- **Type Safety:** Frontend uses TypeScript strict mode (`npx tsc --noEmit`).
- **Health Checks:** `scripts/health_check.py` performs runtime service verification.

## Future Improvement Considerations

- **Scalability:** Current SQLite/Sync backend is verified for ~200 concurrent bots. For higher loads, consider PostgreSQL + Async FastAPI.
- **State Management:** If UI complexity grows significantly, a state management library like Zustand may be introduced, but current hook-based state is preferred for simplicity.
- **Migrations:** Database tables are created on startup. Consider adding Alembic if schema changes become frequent or complex.

## Progress & Current State

### Architectural Upgrades
- **PostgreSQL & Async I/O:** Migrated from SQLite to PostgreSQL using `asyncpg` and `AsyncSession` for concurrent write safety and scalability.
- **Redis Caching:** Implemented 1s TTL caching for high-frequency polling endpoints (`session_basic`, `participants_count`, `leaderboard`) and 5s TTL for `snapshot`.
- **WebSockets:** Real-time event broadcasting via `/ws` endpoint with Redis Pub/Sub support.
- **Local Evaluation (Phase 2):**
    - **RPN Bytecode:** Server provides obfuscated mathematical representation to clients.
    - **Batch Syncing:** `POST /sync_trajectory` allows bots to submit results in bulk, reducing network overhead by 99%.
    - **Anti-Cheat:** Server-side random sampling verification of submitted `z` values.

### Roadmap Progress
- **Phase 1: High-Frequency Polling -> Real-Time Updates.** [DONE]
- **Phase 2: Scalable Optimization & GA Support.** [DONE]
    - [x] RPN Bytecode & Local Evaluation. [DONE]
    - [x] Batch Trajectory Syncing. [DONE]
    - [x] Scalable Snapshot (Downsampling). [DONE]
    - [x] Educational GA Bot Template. [DONE]
- **Phase 3: Teacher UX (Live Map) and Anti-Cheat verification.** [TODO]
