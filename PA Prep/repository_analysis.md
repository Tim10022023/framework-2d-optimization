# Repository Analysis Report

## 1. Executive Summary
The "Framework 2D Optimization" is an interactive educational platform designed for teaching 2D optimization concepts through a "black box" simulation game. Students (participants) attempt to find the global optimum of hidden mathematical functions by either manual interaction (clicking) or deploying automated optimization bots. Instructors (teachers) manage sessions, monitor real-time progress via leaderboards and live maps, and eventually reveal the underlying function landscape for pedagogical analysis.

The system is built with a high-performance, asynchronous backend (FastAPI, PostgreSQL, Redis) and a modern reactive frontend (React, Vite, Plotly). A key architectural innovation is the use of **RPN (Reverse Polish Notation) bytecode** for local evaluation on the client side, which allows bots to perform millions of evaluations without overloading the network, while maintaining the "black box" nature through obfuscation.

## 2. Repository Structure
The repository is organized into distinct service-oriented directories:

- **`backend/`**: Contains the FastAPI application.
  - `app/api/`: REST and WebSocket route definitions.
  - `app/core/`: Business logic, including function evaluation (`functions.py`), session management, and state storage (`store.py`).
  - `app/db/`: Database models and asynchronous session handling.
  - `app/static/`: Pre-rendered reveal images for functions.
- **`frontend/`**: The React + Vite application.
  - `src/components/`: UI panels for teachers and participants, including Plotly visualizations.
  - `src/api.ts`: Central API client and WebSocket manager.
- **`bot/`**: Client-side library and templates.
  - `blackbox_client.py`: Core client with RPN interpreter and batch syncing.
  - `student_bot_template.py` & `genetic_algorithm_template.py`: Educational starting points.
- **`docs/`**: Markdown guides for architecture, deployment, and student/teacher roles.
- **`scripts/`**: Utility scripts for CI/CD (`build.py`), health checks, and workspace verification.
- **`deploy/`**: (Internal/Infrastructure related files).
- **`PA Prep/`**: Folder containing project reconstruction, context, and this analysis report.

## 3. Technology Stack

### Backend
- **FastAPI**: Main web framework for REST and WebSockets.
- **SQLAlchemy 2.0 (Async)**: ORM for database interactions.
- **asyncpg**: Asynchronous PostgreSQL driver.
- **Pydantic**: Data validation and settings management.

### Frontend
- **React (TypeScript)**: UI library.
- **Vite**: Modern frontend build tool.
- **Plotly.js**: Used for 2D Heatmaps (`FunctionContourPlot`) and 3D Surface Plots (`FunctionSurfacePlot`).
- **HTML5 Canvas**: Custom implementation for high-performance point visualization (`PlotCanvas.tsx`).

### Database and Persistence
- **PostgreSQL**: Primary relational database for sessions, participants, and click data.

### Caching / Messaging / Real-Time Communication
- **Redis**: Multi-purpose cache (TTL-based) and Pub/Sub broker for cross-instance WebSocket broadcasting.
- **WebSockets**: Native FastAPI support for real-time event distribution.

### Bot/Client Tooling
- **Python**: Primary language for bot development and stress testing.
- **Requests**: For standard API communication in bots.

### Testing and Quality Assurance
- **Pytest**: Backend unit and integration testing (`backend/tests/`).
- **ESLint & TypeScript**: Frontend linting and type safety.

### Deployment and Operations
- **Docker & Docker Compose**: Orchestration of backend, frontend, database, and Redis.

## 4. Functional Overview
The system supports two primary roles: **Teacher** and **Participant**.

- **Teacher/Session Management**: Teachers create sessions by selecting a target function and setting bounds (`backend/app/api/sessions.py` -> `create_new_session`).
- **Function Selection**: Hidden 2D functions are selected from a predefined library (e.g., Ackley, Rastrigin) in `backend/app/core/functions.py`.
- **Participant Interaction**: Students join sessions, clicking on a 2D search space to evaluate points (`frontend/src/components/PlotCanvas.tsx`).
- **Leaderboard/Ranking**: A real-time leaderboard tracks the best `z` value (score) and total clicks per participant.
- **Bot-Based Optimization**: Students can use the Python template to implement algorithms like Hill Climbing or Genetic Algorithms.
- **Trajectory Synchronization**: "Phase 2" bots evaluate thousands of points locally via RPN and sync them in batches (`POST /sync_trajectory`) to reduce latency.
- **Reveal Mode**: After a session, the teacher reveals the landscape. The frontend uses Plotly to render the 3D topography and overlays student search paths (`frontend/src/components/TeacherInspectPanel.tsx`).

## 5. Backend Architecture
The backend follows a layered architecture optimized for high concurrency.

- **Entry Point**: `backend/app/main.py` initializes the FastAPI app, manages the database lifespan, and starts the Redis Pub/Sub listener.
- **Business Logic (`core/store.py`)**: This is the system's "brain." It handles:
  - **Downsampling**: Instead of saving every point from a bot's trajectory (which could be millions), it uses a stride-based approach to save only representative points to the DB, keeping the database lean.
  - **Caching**: Implements a 1s TTL cache for the leaderboard and a 5s TTL for session snapshots to protect the database from high-frequency polling.
- **Real-Time Distribution (`core/websocket.py`)**: Uses a `ConnectionManager` that integrates with Redis Pub/Sub. When a change occurs (e.g., a new point is submitted), an event is published to Redis, and all connected backend instances broadcast it to their respective clients.
- **Database Layer (`db/models.py`)**: Models are optimized with summary fields (e.g., `best_z` on `ParticipantModel`) to avoid expensive `JOIN` and `MAX` queries during leaderboard calculations.

## 6. API and Communication Model
- **REST API**:
  - `POST /sessions`: Create a session.
  - `POST /sessions/{id}/join`: Join a session (returns RPN payload).
  - `POST /sessions/{id}/evaluate`: Single point evaluation (Phase 1).
  - `POST /sessions/{id}/sync_trajectory`: Batch submission (Phase 2).
  - `GET /sessions/{id}/snapshot`: Fetch current session state for visualization.
- **WebSockets**:
  - `/ws`: Single endpoint for all real-time events (`point_added`, `participant_joined`, `session_state_changed`).
- **Communication Strategy**: Standard CRUD operations use REST. Real-time updates use WebSockets. High-frequency polling is mitigated by aggressive Redis caching.

## 7. Data Model and Persistence
- **SessionModel**: Stores metadata (function name, bounds, state: CREATED/ACTIVE/FINISHED).
- **ParticipantModel**: Tracks student info and **cached best scores** (`best_z`, `total_clicks`).
- **ClickModel**: Stores `(x, y, z)` coordinates. Optimized for bulk insertion.
- **Persistence Strategy**: Metadata and significant optimization points are persisted in PostgreSQL. Transient high-frequency data (like temporary leaderboard states) is managed in memory/Redis.

## 8. Optimization Function Handling
- **Library**: Functions like `Sphere`, `Rosenbrock`, `Ackley`, and `Himmelblau` are defined in `backend/app/core/functions.py`.
- **RPN Encoding**: To support local evaluation without revealing the formula, functions are converted into RPN bytecode (e.g., `[OP_X, OP_Y, OP_MUL]` for `x*y`).
- **Local Evaluation**: The `BlackBoxClient` in `bot/blackbox_client.py` contains an interpreter that executes this bytecode.
- **Anti-Cheat**: The server randomly samples points from batch submissions and re-evaluates them to verify the reported `z` values match the actual function landscape.

## 9. Frontend Architecture
- **State Management**: Uses React hooks (`useState`, `useMemo`) and `localStorage` to persist session IDs.
- **Dual View**: `App.tsx` toggles between `TeacherDashboard` and `ParticipantUI` based on context.
- **PlotCanvas**: A custom HTML5 Canvas component (`frontend/src/components/PlotCanvas.tsx`) handles drawing thousands of points efficiently without the overhead of SVG/DOM elements.
- **Reveal Visuals**: `FunctionContourPlot.tsx` and `FunctionSurfacePlot.tsx` use Plotly.js. The underlying grid is generated on-the-fly using the `lib/benchmarkFunctions.ts` library to match backend logic.

## 10. Bot and Client Library
- **BlackBoxClient**: Provides `join()`, `evaluate()`, and `sync_trajectory()`.
- **Interpreter**: `evaluate_local(x, y)` allows students to test their GA or local search algorithms against the "hidden" function at CPU speeds.
- **Templates**:
  - `student_bot_template.py`: Demonstrates Hill Climbing.
  - `genetic_algorithm_template.py`: A full-featured GA showing crossover and mutation.

## 11. Scalability and Performance Design
- **Async DB**: `asyncpg` prevents I/O blocking during heavy bot submissions.
- **Batching**: Moving from Phase 1 (1 request/point) to Phase 2 (1 request/1000 points) improved scalability by ~100x.
- **Redis TTL**: Caching polling endpoints ensures that 100+ students refreshing the leaderboard won't crash the database.
- **Downsampling**: The `store.py` logic ensures the `clicks` table grows linearly rather than exponentially.

## 12. Deployment and Operations
- **Docker Compose**: Orchestrates `db` (Postgres), `redis`, `backend` (FastAPI), and `frontend` (Vite dev server or static build).
- **Health Checks**: `scripts/health_check.py` verifies all services are reachable and functional.
- **Build Pipeline**: `scripts/build.py` handles Docker builds and image tagging.

## 13. Testing and Quality Assurance
- **Backend Tests**: `backend/tests/test_api.py` covers the core lifecycle.
- **Stress Tests**: `bot/stress_test.py` and `bot/ga_stress_test.py` simulate heavy loads.
- **Type Safety**: TypeScript used across the frontend to prevent runtime errors in API data handling.

## 14. Security, Integrity, and Limitations
- **Obfuscation**: RPN provides a layer of security but is not cryptographically secure; a determined student could decompile the bytecode.
- **Session Isolation**: Participants are scoped to their `session_id`.
- **Integrity**: Server-side verification of `z` values prevents simple coordinate-spoofing in bots.

## 15. Requirements Derived from the Implementation

### Functional Requirements
- **F1 (Session Management)**: Create, start, and finish optimization sessions.
- **F2 (Black-Box Evaluation)**: Evaluate 2D coordinates without revealing the function formula.
- **F3 (Real-Time Leaderboard)**: Display ranking based on the best found value.
- **F4 (Trajectory Sync)**: Support batch submission of search paths for bot performance.

### Non-Functional Requirements
- **NF1 (Scalability)**: Support up to 50 concurrent optimization bots.
- **NF2 (Low Latency)**: Real-time updates via WebSockets (< 200ms propagation).
- **NF3 (Integrity)**: Verify bot-submitted results server-side.

## 16. Architecture Decisions
- **FastAPI/Async**: Chosen for high-concurrency WebSocket and DB handling.
- **Redis Pub/Sub**: Essential for horizontal scaling of WebSockets across multiple backend instances.
- **PostgreSQL**: Selected for robust ACID compliance and relational data integrity for session exports.
- **RPN Bytecode**: Strategic choice to balance "black-box" mystery with local computation performance.

## 17. Suggested Material for Academic Chapters

### Chapter 3: Analysis and Requirements Definition
- Focus on the "Classroom Optimization" use case. Use the functional requirements (F1-F4) derived above.
- Mention the transition from high-frequency polling to event-driven updates as a key technical requirement.

### Chapter 4: Concept and Architecture
- Describe the tiered architecture: Client (Bot) -> RPN Interpreter -> Batch Sync -> Async Backend -> Redis/Postgres.
- Use a sequence diagram showing the `join -> get_rpn -> local_eval -> sync_batch -> broadcast` flow.

### Chapter 5: Implementation
- Highlight the `core/store.py` downsampling logic and the `core/websocket.py` Redis integration.
- Provide a code snippet of the RPN interpreter loop from `bot/blackbox_client.py`.

## 18. Open Questions
- **Deployment Strategy**: Is there a specific cloud provider or local server cluster targeted for the final classroom use?
- **Auth**: Currently, the system uses "Participant Names" for session joining. Is a more robust OAuth/Login system planned?
- **Persistence**: How long should session data be retained post-reveal?
