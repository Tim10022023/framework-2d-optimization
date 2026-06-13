# Performance Benchmarks

This directory contains the benchmarking suite for evaluating the framework's performance, as required for the thesis "Development of a scalable framework for interactive teaching of 2D optimization algorithms through Black-Box simulation".

## Prerequisites

- Python 3.8+
- `requests` library
- Backend running at `http://localhost:8000` (via Docker Compose)

## Benchmark Scenarios

### 1. Benchmark A: Individual REST Evaluation Baseline
Measures the performance of synchronous point-by-point evaluation (Phase 1 approach).

**Command:**
```bash
python run_individual_eval.py --bots 20 --points 100 --runs 3
```

**Metrics:**
- Throughput (points per second)
- Latency (min/mean/max/p95)
- Error rate

### 2. Benchmark B: Local RPN Evaluation Speed
Measures how many function evaluations a bot can perform locally using the RPN interpreter (Phase 2 core).

**Command:**
```bash
python run_rpn_eval.py --points 100000 --runs 5
```

**Metrics:**
- Local throughput (evaluations per second)
- RPN payload size impact

### 3. Benchmark C: Batch Synchronization / Parallel Bot Scaling
Measures the Phase 2 approach where bots evaluate locally and periodically synchronize via `POST /sync_trajectory`.

**Command:**
```bash
python run_batch_sync.py --bots 50 --evals-per-bot 10000 --batch-size 1000 --runs 3
```

**Metrics:**
- Effective throughput (synchronized points per second)
- Sync request latency
- Network load reduction (compared to Benchmark A)

## Output

Results are saved in `benchmarks/results/` as:
- `benchmark_<name>_<timestamp>.json`: Detailed run data and metadata.
- `benchmark_summary_<timestamp>.csv`: Flat summary for easy import into Excel/SPSS.

## Mapping to Thesis Requirements

| Benchmark | Requirement | Purpose |
|-----------|-------------|---------|
| A | NF2, NF4 baseline | Baseline for scalability comparison. |
| B | F8, NF4 | Verifies efficiency of RPN evaluation. |
| C | NF1, NF4, NF6 | Demonstrates scalability with batching and parallel bots. |
