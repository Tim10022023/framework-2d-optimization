# Architecture & Technical Reference

This document describes the system architecture, code organization, and technical conventions of the 2D Optimization Framework.

## 🏗 High-Level Architecture

The system is designed as a high-performance, asynchronous educational platform capable of supporting 60+ concurrent students in a real-time "black box" optimization game.

### Tech Stack
- **Backend:** FastAPI (Python 3.14+), SQLAlchemy 2.0 (Async), PostgreSQL, Redis.
- **Frontend:** React (TypeScript), Vite, Plotly.js for 2D/3D visualizations.
- **Real-time:** WebSockets with Redis Pub/Sub for cross-instance broadcasting.
- **Infrastructure:** Docker & Docker Compose for orchestration.

---

## 📂 Project Structure

```text
framework-2d-optimization/
├── backend/                # FastAPI Application
│   ├── app/
│   │   ├── api/            # Route handlers (REST & WebSockets)
│   │   ├── core/           # Business logic, caching, & evaluators
│   │   ├── db/             # PostgreSQL models & async session setup
│   │   └── static/         # Reveal images for functions
│   └── tests/              # Pytest suite (Unit & Integration)
├── frontend/               # React Application
│   ├── src/
│   │   ├── components/     # UI Panels & Plotly visualizations
│   │   ├── api.ts          # API Client & WebSocket manager
│   │   └── types.ts        # Shared TypeScript definitions
├── bot/                    # Client Libraries & Templates
│   ├── blackbox_client.py  # API Client with RPN Interpreter
│   ├── student_bot_template.py # Starter code for students
│   └── stress_test.py      # Performance testing utility
├── docs/                   # Documentation & Guides
├── scripts/                # Build, Health Check, & Maintenance scripts
└── docker-compose.yaml     # Local development orchestration
```

---

## ⚙️ Backend Implementation details

### 1. Asynchronous Foundation
The backend is entirely asynchronous. Database interactions use `asyncpg` via SQLAlchemy's `AsyncSession`, and all I/O-bound tasks are non-blocking. This allows a single instance to handle hundreds of concurrent requests efficiently.

### 2. Caching Strategy (Redis)
To minimize database load, we use Redis for aggressive caching:
- **High-Frequency Polling:** `session_basic`, `participants_count`, and `leaderboard` are cached with a 1s TTL.
- **Snapshots:** Large session snapshots are cached with a 5s TTL.
- **Invalidation:** Caches are programmatically invalidated on mutable events (e.g., `add_click`, `join_session`, `set_session_status`).

### 3. Real-time Updates (WebSockets)
Instead of relying solely on HTTP polling, the frontend connects to `/{code}/ws`. 
- **Broadcasting:** When an event occurs (e.g., a student clicks a point), the backend publishes a message to a Redis channel.
- **Scalability:** Multiple backend instances can subscribe to the same Redis channel, allowing WebSockets to scale horizontally.

### 4. Local Evaluation Workflow (Phase 2)
To prevent API saturation from automated bots:
- **Obfuscation:** The server provides an RPN (Reverse Polish Notation) bytecode representation of the function.
- **Execution:** The `blackbox_client.py` includes a lightweight RPN interpreter that evaluates points locally (0ms network latency).
- **Syncing:** Bots batch their results and submit them via `POST /sync_trajectory`.
- **Anti-Cheat:** The server randomly samples points from the trajectory and verifies them against the true function.

---

## 🎨 Frontend Implementation

### 1. State Management
The frontend uses standard React hooks (`useState`, `useMemo`, `useEffect`) for simplicity. Global state is avoided to keep the component hierarchy shallow and maintainable.

### 2. Visualizations
- **Plotly.js:** Used for interactive 2D heatmaps (`FunctionContourPlot`) and 3D surface plots (`FunctionSurfacePlot`).
- **Real-time Path:** The "Teacher Inspect" panel allows stepping through a student's optimization path in real-time.

---

## 🧪 Testing & Quality Assurance

### 1. Build Pipeline (`scripts/build.py`)
A unified script that ensures every commit is production-ready:
1. Runs `pytest` on the backend.
2. Lints the frontend (`eslint`).
3. Type-checks the frontend (`tsc`).
4. Verifies the frontend production build.
5. Builds Docker images.

### 2. Health Checks (`scripts/health_check.py`)
Verifies service availability, backend-to-database connectivity, and Redis responsiveness.

---

## 🚀 Performance Metrics

- **Capacity:** Verified for 200+ concurrent bots and 60+ concurrent UI users.
- **Latency:** Average API response < 50ms (with Redis cache hits).
- **Throughput:** Capable of handling 500+ evaluations per second via `sync_trajectory`.

---

## 🔧 Maintenance

### Adding a New Function
1. Implement the math and metadata in `backend/app/core/functions.py`.
2. Add the RPN bytecode to `get_blackbox_payload`.
3. Register the function in the `FUNCTIONS` dictionary.
4. Add a reveal image to `backend/app/static/function_images/`.
