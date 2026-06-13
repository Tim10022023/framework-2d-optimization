# Backend Implementation Analysis: Framework 2D Optimization

This report provides a technical analysis of the backend implementation for the "Framework 2D Optimization" project, intended for inclusion in Chapter 5.1 of the scientific thesis.

## 1. Backend Technology Stack

The backend is designed for high-concurrency and real-time educational interaction.

- **Framework and Language:** Python 3.12+ with **FastAPI**. The choice of FastAPI leverages asynchronous I/O (ASGI) to handle hundreds of concurrent bot evaluations.
- **Main Libraries:** 
    - `pydantic` for data validation and schema definition.
    - `asyncio` for non-blocking task orchestration.
    - `math` and `random` for benchmark function evaluation and anti-cheat sampling.
- **Database/ORM:** **PostgreSQL** (via `asyncpg` driver) managed by **SQLAlchemy 2.0 (Async)**. The system uses asynchronous sessions (`AsyncSession`) to prevent blocking during heavy write operations.
- **Redis Usage:** Integrated via `redis.asyncio` for:
    - TTL-based caching of high-frequency endpoints.
    - **Pub/Sub** for cross-instance WebSocket event broadcasting.
- **WebSocket Usage:** Native FastAPI WebSockets for real-time state distribution.
- **Validation/Configuration:** Environment-based configuration via a `settings` object (`pydantic-settings`).

## 2. Backend Folder and Module Structure

The backend follows a clear separation of concerns:

```text
backend/app/
├── api/                # Route Controllers
│   ├── functions.py    # Endpoint for listing benchmark functions
│   └── sessions.py     # Core game logic (Session, Join, Evaluate, WebSocket)
├── core/               # Business Logic & Infrastructure
│   ├── config.py       # Global settings and environment variables
│   ├── functions.py    # Benchmark definitions, RPN bytecode, and evaluation
│   ├── redis.py        # Redis client lifecycle management
│   ├── store.py        # Persistence logic, downsampling, and verification
│   └── websocket.py    # WebSocket connection management and Pub/Sub listener
├── db/                 # Persistence Layer
│   ├── models.py       # SQLAlchemy ORM models (Session, Participant, Click)
│   └── session.py      # Async engine and session factory setup
├── static/             # Static assets (pre-rendered function reveal images)
└── main.py             # Application entry point and lifespan management
```

### Module Responsibilities:
- `api/`: Defines REST endpoints and handles HTTP status codes.
- `core/store.py`: Acts as the "Service Layer," managing the transition between memory, cache, and database. It handles complex operations like **downsampling** and **anti-cheat verification**.
- `core/functions.py`: Encapsulates mathematical logic and the **RPN obfuscation** generator.
- `db/models.py`: Defines the relational schema with summary fields (e.g., `best_z`) for performance.

## 3. REST API Endpoints

| HTTP Method | Path | Purpose | Request Body / Params | Response | Req. IDs |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/functions` | List available functions | None | `list[FunctionSpec]` | F6 |
| `POST` | `/sessions` | Create a new session | `CreateSessionBody` | `SessionMeta` | F1 |
| `GET` | `/sessions/{code}` | Get session metadata | `code: str` | `SessionBasic` | F1, F5 |
| `POST` | `/sessions/{code}/join` | Join as participant/bot | `JoinSessionBody` | `JoinResult` (incl. RPN) | F5, NF7 |
| `POST` | `/sessions/{code}/evaluate` | Single point eval (Phase 1) | `EvaluateBody` | `EvalResult` | F2 |
| `POST` | `/sessions/{code}/sync_trajectory` | Batch trajectory sync (Phase 2) | `SyncTrajectoryBody` | `SyncResult` | F4, NF1 |
| `GET` | `/sessions/{code}/leaderboard` | Get current ranking | `code: str` | `Leaderboard` | F3 |
| `GET` | `/sessions/{code}/snapshot` | Decimated search path data | `code: str` | `Snapshot` | F8, NF2 |
| `POST` | `/sessions/{code}/end` | Close the session | `admin_token` (Header) | `SessionStatus` | F1 |
| `GET` | `/sessions/{code}/export` | Full session data for reveal | `admin_token` (Header) | `FullSessionExport` | F7 |

## 4. WebSocket Implementation

The system implements a real-time event bus at `/{code}/ws`.

- **Endpoints:** A single WebSocket endpoint per session handles all connected clients (Participants and Teachers).
- **Events:** The server broadcasts JSON payloads:
    - `participant_joined`: New student enters.
    - `click_added`: Individual point evaluation result.
    - `leaderboard_updated`: Sent after significant score changes.
    - `session_ended`: Notifies UI to switch to "Reveal" mode.
- **Scalability:** The `ConnectionManager` uses a **Redis Pub/Sub listener** (`session_updates` channel). This ensures that if a point is submitted to Instance A, clients connected to Instance B also receive the update.
- **Handling:** Connections are stored in a session-scoped `Set` to prevent duplicate messaging and handle sudden disconnects gracefully.

## 5. Database Model and Persistence

The schema is optimized for write-heavy trajectory submissions.

- **`SessionModel`**: Persistent metadata. Tracks the function, goal (min/max), and lifecycle status.
- **`ParticipantModel`**: Represents a student or bot.
    - **Performance Optimization**: Stores `best_z` and `total_clicks` as redundant summary fields. This allows the leaderboard to be computed without scanning millions of rows in the `clicks` table.
- **`ClickModel`**: Stores `(x, y, z)` and the `step` number.
- **Persistence Strategy**:
    - **Full persistence**: Metadata and manual clicks are always saved.
    - **Selective persistence**: Bot trajectories are downsampled (stride-based) to store only ~50 representative points per batch to keep the DB size manageable while preserving the search path's visual structure.

## 6. Redis Usage

Redis is critical for mitigating database bottlenecks under bot-induced load.

- **Caching Strategy:**
    - `session_basic:{code}`, `participants_count:{code}`, `leaderboard:{code}`: **1s TTL**. Protects against high-frequency UI polling.
    - `snapshot:{code}`: **5s TTL**. Caches the expensive downsampled search paths.
- **Invalidation:** Caches are programmatically deleted (`redis.delete`) during mutation events (`add_click`, `join_session`, `set_session_status`).
- **Pub/Sub:** Channel `session_updates` is used to synchronize WebSocket broadcasts across multiple backend workers/containers.

## 7. RPN and Local Black-Box Evaluation Support

To solve the "Network Saturation" problem (NF1), the system offloads computation to the client.

- **Generation:** Functions in `core/functions.py` are manually mapped to RPN bytecode (e.g., `[OP_X, OP_CONST, 3.7, OP_SUB, OP_CONST, 2.0, OP_POW, ...]`).
- **Payload:** When a bot joins, it receives this bytecode. It uses a local interpreter (in the Python client) to evaluate millions of points with 0ms network latency.
- **Verification (Anti-Cheat):** Upon receiving `POST /sync_trajectory`, the server:
    1. Randomly samples 5 points from the batch.
    2. Re-evaluates them using the server-side Python function.
    3. If `abs(submitted_z - true_z) > 1e-4`, the batch is rejected (Integrity check NF3).
- **Sync Flow:** Bots optimize locally -> periodic batch sync -> server verification -> downsampled storage -> WebSocket broadcast.

## 8. Error Handling and Validation

- **Validation:** Pydantic schemas in `api/sessions.py` enforce type safety for all incoming JSON payloads.
- **Handling:** Standardized `HTTPException` usage:
    - `400 Bad Request`: Invalid goal, unknown function, or verification failure.
    - `401 Unauthorized`: Invalid admin token for protected teacher routes.
    - `404 Not Found`: Missing session or participant.
    - `409 Conflict`: Session ended or max steps exceeded.
- **Safeguards:** Database transactions (`await db.commit()`) ensure that participant metrics and click data remain synchronized even if a crash occurs mid-batch.

## 9. Implementation Flow Examples

1. **Creating a Session**: Teacher sends `POST /sessions`. Server generates a unique 6-character code and an admin token, creates a `SessionModel`, and returns metadata.
2. **Joining a Session**: Participant sends `POST /join`. Server creates `ParticipantModel`, invalidates the `participants_count` cache, and returns the **RPN bytecode**.
3. **Submitting a Manual Point**: Participant sends `POST /evaluate`. Server computes `z`, saves a `ClickModel`, updates `ParticipantModel.best_z`, invalidates `leaderboard` cache, and broadcasts `click_added` via WebSocket.
4. **Synchronizing a Bot Trajectory**: Bot sends `POST /sync_trajectory` with 1000 points. Server verifies 5 random points, performs stride-based downsampling, saves ~50 points to DB, updates total step count, and triggers a leaderboard update broadcast.

## 10. Thesis-Relevant Interpretation (Chapter 5.1)

The implementation highlights several key engineering decisions for educational frameworks:
- **Scalability through Decoupling:** The RPN local evaluation is the most critical innovation, allowing the framework to scale from a few students to an entire lecture hall without server collapse.
- **Performance/Storage Trade-off:** The downsampling logic in `store.py` demonstrates a pragmatic approach to handling Big Data in a visualization context—storing enough for a meaningful plot but not enough to bloat the database.
- **Real-Time Responsiveness:** The combination of Redis Pub/Sub and WebSockets ensures that the teacher's "Live Map" remains fluid even when multiple backend instances are serving different groups of students.

**Suggested Material for Chapter 5.1:**
- **Code Snippet**: The RPN Opcode definitions and the `add_trajectory` verification logic.
- **Diagram**: A sequence diagram showing the RPN-based evaluation and batch syncing flow.
- **Metric**: The comparison of network requests (1 per point vs. 1 per 1000 points).

---
*Report generated on Montag, 1. Juni 2026.*
