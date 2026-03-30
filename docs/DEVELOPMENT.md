# Development and Maintenance Guide

Technical documentation for developing, testing, and maintaining the 2D Optimization Framework.

## 🚀 Getting Started

### Prerequisites
- Python 3.14+ (for backend/scripts)
- Node.js 18+ & npm (for frontend)
- Docker & Docker Compose (for containerized dev)
- Redis (recommended for caching)
- PostgreSQL (recommended for production/scaling)

### Local Development Flow

#### 1. Quick Start with Docker (Recommended)
```powershell
# Build and start all services (Postgres, Redis, Backend, Frontend)
docker compose up --build
```
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

#### 2. Manual Setup (No Docker)
**Backend:**
```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

**Frontend:**
```powershell
cd frontend
npm install
npm run dev
```

---

## 🛠 Build & Health Check Pipeline

We use a unified build script `scripts/build.py` to ensure code quality before deployment.

### 1. Full Build Pipeline
```powershell
python scripts/build.py
```
This script performs:
1. **Backend Tests:** Runs `pytest backend/tests/`
2. **Frontend Linting:** Runs `npm run lint` in the frontend directory
3. **Frontend Type Check:** Runs `npx tsc --noEmit`
4. **Frontend Build:** Runs `npm run build` to verify production assets
5. **Docker Build:** Rebuilds images if all tests pass

### 2. Runtime Health Checks
Once the services are running, verify them with:
```powershell
python scripts/health_check.py
```
This checks if:
- Backend `/health` returns `ok`
- Frontend is serving on port 5173
- Database connectivity is active

---

## 🏗 Project Architecture & Scaling

### Tech Stack
- **Backend:** FastAPI (Async), SQLAlchemy 2.0 (Async), PostgreSQL, Redis.
- **Frontend:** React (TypeScript), Vite, Plotly.js.
- **Real-time:** WebSockets with Redis Pub/Sub for broadcasting.

### Performance & Scaling
Current architecture is optimized for 60+ concurrent students:
- **Async I/O:** Backend never blocks on DB/Network.
- **Caching:** Redis stores high-frequency polling data (1s TTL) and snapshots (5s TTL).
- **Local Evaluation:** Student bots run the math locally via RPN bytecode, reducing API load by 99%.
- **WebSockets:** UI updates via events instead of constant polling.

### Stress Testing
Use the provided stress test script to simulate high load:
```powershell
python bot/stress_test.py --n 50 --steps 100
```

---

## 🧪 Testing

### Backend Unit Tests
```powershell
cd backend
python -m pytest tests/
```

### Manual API Testing
The Swagger UI at `/docs` is the primary tool for manual endpoint testing.

---

## 🔧 Maintenance Tasks

### Adding New Functions
1. Define the math and metadata in `backend/app/core/functions.py`.
2. Implement the RPN bytecode in `get_blackbox_payload`.
3. Add a reveal image to `backend/app/static/function_images/`.

### Database Migrations
Currently, tables are created on startup via `Base.metadata.create_all`. For schema changes in production, consider adding Alembic.

### Environment Variables
See `docs/DEPLOYMENT.md` for a full list of configuration variables.
