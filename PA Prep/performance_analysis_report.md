# Performance Analysis and Benchmarking Report: Framework 2D Optimization

This report analyzes the repository's performance testing capabilities for Chapter 6.1 of the scientific thesis.

## 1. Existing performance-related files

The repository contains several scripts and documents dedicated to performance, stress testing, and architectural scalability:

- **`bot/stress_test.py`**: A multi-threaded stress test script. It simulates multiple bots performing synchronous `POST /evaluate` requests to measure backend latency and request-per-second (RPS) throughput.
- **`bot/ga_stress_test.py`**: A multiprocessing-based stress test focusing on Phase 2 features. It evaluates the RPN interpreter's speed and the `POST /sync_trajectory` batch synchronization endpoint.
- **`scripts/create_stress_session.py`**: A utility script to programmatically create a test session, ensuring a clean and reproducible starting state for benchmarks.
- **`PA Prep/bot_analysis_report.md`**: Analysis of the bot framework, including performance considerations for local RPN evaluation and batch syncing.
- **`PA Prep/backend_analysis_report.md`**: Technical overview of the backend's scalability features, such as Redis caching, asynchronous I/O, and database downsampling.
- **`ROADMAP.md`**: Contains high-level performance goals and a "Summary of Impact" (e.g., "Network Traffic: Reduced by ~99%").

**Distinction:**
- **Test Code:** `bot/stress_test.py`, `bot/ga_stress_test.py`.
- **Benchmark Utilities:** `scripts/create_stress_session.py`.
- **Documentation/Analysis:** `PA Prep/*.md`, `ROADMAP.md`.
- **Generated Logs/Results:** **NONE FOUND.** No historical benchmark results (CSV, JSON, or Log) are currently stored in the repository.

## 2. Existing benchmark scenarios

### Scenario A: Synchronous API Stress (Phase 1 Baseline)
- **Script:** `bot/stress_test.py`
- **Tested Scenario:** High-concurrency synchronous point evaluation.
- **Components:** Bot Client (Threads) -> FastAPI Backend -> PostgreSQL DB.
- **Parameters:** `NUM_BOTS` (default 50), `STEPS_PER_BOT` (20), `SLEEP_BETWEEN_STEPS` (0.0).
- **Metrics:** Request latency (Mean, Median, Max), total runtime, error rate.
- **Output:** Formatted console output with stats per bot.
- **Thesis Relevance:** Crucial for demonstrating the limitations of the Phase 1 architecture (one request per click).

### Scenario B: Asynchronous Batch Scaling (Phase 2 Performance)
- **Script:** `bot/ga_stress_test.py`
- **Tested Scenario:** Local RPN-based search with periodic batch synchronization.
- **Components:** Bot Client (Multiprocessing) -> FastAPI Backend -> Redis (Caching) -> PostgreSQL DB (Downsampling).
- **Parameters:** `BOT_COUNT` (50), `EVALS_PER_BOT` (10,000), `SYNC_INTERVAL` (1,000), `GA_POPULATION` (50).
- **Metrics:** Success rate of batch sync, best fitness found.
- **Output:** Console logs per bot process.
- **Thesis Relevance:** High. This script validates the core scalability hypothesis of the project (Requirement NF4).

## 3. Bot-related performance tests

The current infrastructure focuses on two primary bot performance aspects:

- **Local RPN Evaluation Speed:** While `ga_stress_test.py` performs 10,000 evaluations per bot, it does not explicitly measure "evaluations per second" (evals/s). However, the architecture is designed to support $>10^4$ evals/s by avoiding network calls.
- **Batch Synchronization:** `ga_stress_test.py` demonstrates the efficiency of sending 1,000 points in a single `POST /sync_trajectory` call.
- **Requests Avoided:** The batch sync mechanism theoretically reduces the number of HTTP requests by a factor equal to the `SYNC_INTERVAL` (e.g., 1,000x reduction).
- **Backend Load:** By offloading evaluation to the client and using server-side verification/downsampling, the backend load is decoupled from the optimization frequency.

## 4. Backend/API performance tests

The backend tests are currently driven by the bot client scripts:

- **Manual Point Evaluation:** Tested via `stress_test.py`.
- **Sync Trajectory:** Tested via `ga_stress_test.py`. Includes random-sampling anti-cheat verification.
- **Caching:** The backend report confirms Redis usage for `leaderboard` and `snapshot` endpoints, but no specific benchmark script isolates cache-hit vs. cache-miss performance.
- **Downsampling:** `core/store.py` implements stride-based downsampling during trajectory sync, but the overhead of this operation is not currently measured.

## 5. Existing results and evidence

No concrete numeric result files (CSV, JSON) exist. However, qualitative claims are found in documentation:

| Source | Claimed Metric | Scenario | Suitability for Thesis |
| :--- | :--- | :--- | :--- |
| `ROADMAP.md` | "Network Traffic: Reduced by ~99%" | Batch Sync vs. Point Eval | Use as a theoretical target. |
| `Analysis Reports` | "200+ concurrent bots" | High-load session | Needs empirical verification. |
| `Analysis Reports` | ">10,000 evals/s" | Local RPN evaluation | Needs explicit timing in scripts. |

**Critical Note:** Current results are largely anecdotal or "architectural estimates". For Chapter 6.1, fresh empirical data must be generated using the scripts described in Section 10.

## 6. Reproducibility assessment

| Script | Ease of Use | Dependency | Limitations |
| :--- | :--- | :--- | :--- |
| `stress_test.py` | Medium | Requires manual `SESSION_CODE` update. | Uses threading (Python GIL) which limits real concurrency. |
| `ga_stress_test.py` | Medium | Requires manual `SESSION_CODE` update. | Uses multiprocessing, which is more realistic but harder to manage. |
| `create_stress_session.py` | High | None. | Only creates the session; does not run the test. |

**Reproducibility Gaps:**
- Hardcoded `API_URL` and `SESSION_CODE` in most scripts.
- No single "run-all-benchmarks" command.
- Performance depends heavily on the host machine's CPU and database latency.

## 7. Scientific quality of the current benchmarks

**Strengths:**
- Multi-process simulation (`ga_stress_test.py`) accurately models multiple students.
- Measurements of min/median/max latency in `stress_test.py`.

**Weaknesses:**
- **No Warm-up:** Scripts start measuring immediately, ignoring JIT or cache-filling effects.
- **No Aggregation:** `ga_stress_test.py` does not provide a summary of total throughput or average sync time across all processes.
- **Hard-coded Constants:** Limits the ability to test different "Load Curves" (e.g., increasing bot count from 1 to 100).
- **Lack of Repetition:** No logic for multiple runs to calculate standard deviation.

## 8. Recommended clean benchmark design for the thesis

Proposed plan for Chapter 6.1 with 3 core scenarios:

### Scenario 1: Scalability Baseline (NF4, NF1)
- **Title:** Synchronous vs. Batch Synchronization Throughput.
- **Purpose:** Compare total points processed per second by the backend.
- **Setup:** 1 Session, 50 Bots.
- **Parameters:** Compare `stress_test.py` (Mode A) vs. `ga_stress_test.py` with `SYNC_INTERVAL=100` (Mode B).
- **Metrics:** Total points synced / Total runtime.
- **Mapping:** NF4 (Scalability), NF1 (Performance).

### Scenario 2: RPN Interpreter Efficiency (F8)
- **Title:** Local Evaluation Overhead.
- **Purpose:** Measure how many function evaluations a standard client can perform per second.
- **Setup:** Local client, various function complexities (Sphere vs. Eggholder).
- **Metrics:** Evaluations per second (evals/s).
- **Mapping:** F8 (Local Evaluation).

### Scenario 3: Backend Latency under Load (NF5, NF6)
- **Title:** API Responsiveness during High-Volume Sync.
- **Purpose:** Measure if the UI polling endpoints (leaderboard) remain responsive while bots are flooding `sync_trajectory`.
- **Setup:** 50 GA bots syncing, 1 separate script measuring `GET /leaderboard` latency.
- **Metrics:** Response time of read-only endpoints vs. Write-load.
- **Mapping:** NF5 (Responsiveness), NF6 (Availability).

## 9. Suggested result tables and figures

- **Table 6.1:** "Comparison of Network Overhead: Individual vs. Batch Sync" (Columns: Mode, Requests, Points, Avg Latency, Failures).
- **Table 6.2:** "RPN Evaluation Speed across Benchmark Functions" (Columns: Function, Opcode Count, Evals/sec).
- **Chart 6.1:** "Backend Response Time vs. Concurrent Participant Count" (Line chart showing latency for 10, 50, 100, 200 bots).

## 10. Needed refactoring before rerunning

To make the benchmarks "Thesis-Ready":
1. **CLI Parameterization:** Add `argparse` to `stress_test.py` and `ga_stress_test.py` for `--bots`, `--steps`, `--interval`, and `--url`.
2. **Automated Session Lifecycle:** Integrate `create_stress_session.py` logic into the benchmark scripts so they create their own test environment.
3. **Structured Output:** Save results to `benchmarks/results_{timestamp}.json` or `.csv`.
4. **Summary Statistics:** Implement global counters (using `multiprocessing.Value` or `Queue`) to aggregate total evals/s across all bot processes.
5. **Warm-up Phase:** Add a 2-second "warm-up" period before starting measurements.

## 11. Draft interpretation for Chapter 6.1

> "The performance evaluation demonstrates that the transition from a synchronous point-by-point evaluation (Phase 1) to a decoupled RPN-based local search with batch synchronization (Phase 2) results in a significant increase in system throughput. While Phase 1 was limited by the network round-trip time (RTT) of approximately [X] ms per point, the Phase 2 architecture allows bots to perform optimization at the CPU's maximum capacity, only interacting with the server periodically. This approach reduces the API load by [Y]% and ensures that the teacher's dashboard remains responsive even during high-frequency optimization runs by over 50 concurrent agents."

---
*Analysis completed for thesis preparation.*
