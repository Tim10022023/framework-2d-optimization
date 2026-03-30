# Performance & Scalability Roadmap

As the `framework-2d-optimization` project scales to support 60+ concurrent students, the current synchronous API bottleneck must be addressed. This roadmap outlines architectural upgrades and a completely overhauled "Local Evaluation" workflow for the student bot.

## Phase 1: Database and Backend Architecture Upgrade (COMPLETED)

Status: [DONE]
- [x] **PostgreSQL Migration:** Replaced SQLite with PostgreSQL for concurrent write safety.
- [x] **Async I/O:** Converted SQLAlchemy to `asyncpg` and FastAPI endpoints to `async def`.
- [x] **Redis Caching:**
    - [x] Cached `get_session_basic` (1s TTL) to absorb frontend polling.
    - [x] Cached `get_participants_count` (1s TTL).
    - [x] Cached `compute_leaderboard` (1s TTL).
- [x] **WebSockets:**
    - [x] Implemented `/sessions/{code}/ws` for real-time event broadcasting.
    - [x] Events: `click_added`, `participant_joined`, `leaderboard_updated`, `session_ended`.
    - [x] Frontend: Updated `App.tsx` to use WebSockets with polling as a fallback.

---

## Phase 2: Upgraded Student Workflow (Local Evaluation without Leaking) (COMPLETED)

Status: [DONE]
- [x] **Obfuscated Payload:** Implemented RPN bytecode generation in `functions.py`.
- [x] **Local Evaluation:** Added RPN interpreter to `blackbox_client.py` for zero-latency searching.
- [x] **Trajectory Syncing:** New `POST /sync_trajectory` endpoint for batch submission of points.
- [x] **Anti-Cheat:** Server-side verification of a random sample of trajectory points.
- [x] **Performance:** Reduced network overhead by 99% for optimized bots.

---

## Phase 3: Teacher UX and Verification

### 1. The "Live Map"
- Since the server is now handling far fewer requests, we can dedicate bandwidth to streaming real-time data to the Teacher dashboard via WebSockets.
- The UI will display a "Live Map" showing 60 moving dots representing where each student's algorithm is currently exploring.

### 2. Anti-Cheat Mechanisms
- Because evaluation happens locally, a student *could* theoretically spoof the submitted `z` score.
- The backend will enforce a lightweight verification step upon receiving a `sync_trajectory` batch: it recalculates 2-3 points from the batch to ensure the submitted `z` values match the actual function output.

## Summary of Impact
- **Network Traffic:** Reduced by ~99%.
- **API Load:** Negligible.
- **Student Experience:** Optimization algorithms will run at full CPU speed rather than being limited by network latency.
- **Security:** The function formula remains hidden inside a compiled artifact.
