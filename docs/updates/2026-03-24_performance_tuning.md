# Technical Report: Performance Optimization and Scalability Assessment (2026-03-24)

## Objective
To identify and mitigate latency issues observed under concurrent access (20+ users) and to benchmark the system's capacity in a containerized environment.

## Methodology
Performance assessment was conducted using an automated stress test (`bot/stress_test.py`).
- **Test Environment:** Containerized deployment (Docker Compose) on Windows 11 (win32).
- **Workload Parameters:** 50 concurrent threads, each executing 1 join request and 20 sequential evaluate requests (Total N=1,050 requests).
- **Baseline Observation:** Prior to optimization, burst loads of 50 concurrent clients resulted in significant latency spikes and intermittent connection timeouts.

## Optimization Implementation

### 1. Persistence Layer (SQLite + SQLAlchemy)
- **Concurrency Control:** Enabled Write-Ahead Logging (WAL) and set `synchronous=NORMAL` via SQLAlchemy events to improve concurrent write throughput.
- **Indexing:** Applied explicit indexes on `ParticipantModel.session_id` and `ClickModel.participant_id` to reduce lookup complexity for relationship-heavy queries.
- **Aggregate Queries:** Refactored `add_click` and `compute_leaderboard` to utilize SQL aggregate functions (`func.count`, `func.min`, `func.max`) instead of loading full object graphs into application memory.

### 2. API Design (FastAPI)
- **Data Minimization:** Introduced `get_session_basic` and `get_participants_count` to serve metadata requests without retrieving associated participant or click data.
- **Caching:** Implemented a short-lived (TTL=1.0s) in-memory cache for high-frequency polling endpoints (`/sessions/{code}`, `/sessions/{code}/public`) to minimize redundant I/O.

### 3. Client-Side Coordination (React)
- **Polling Frequency:** Increased the global polling interval from 1,500ms to 3,000ms.
- **Conditional Snapshots:** Restricted snapshot data retrieval to scenarios where visual bot paths are explicitly requested.

## Empirical Results (Post-Optimization)
Measurements obtained from a burst load of 50 simulated clients:
- **Total Workflow Runtime:** 12.88 seconds.
- **Mean Request Latency ($\mu$):** 602.54 ms.
- **Median Latency ($\tilde{x}$):** 605.66 ms.
- **Maximum Observed Latency:** 814.86 ms.
- **Error Rate:** 0.0% (N=1,050 requests).

## Conclusion
The implemented optimizations significantly reduced the per-request computational and I/O overhead. In a local containerized environment, the system demonstrates stable sub-second response times under a burst load of 50 concurrent simulated clients. Actual classroom performance remains subject to network-specific factors.
