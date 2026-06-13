import argparse
import random
import time
import statistics
from typing import List, Dict, Any
from benchmark_utils import (
    BlackBoxClient, 
    get_env_info, 
    create_benchmark_session, 
    save_results, 
    aggregate_metrics
)

def run_benchmark(args):
    print(f"--- Starting Benchmark B: Local RPN Evaluation Speed ---")
    
    session_code = args.session_code or create_benchmark_session(args.url, args.function)
    
    client = BlackBoxClient(args.url, session_code)
    try:
        join_data = client.join("BenchBot-B-RPN")
        rpn_payload = join_data.get("blackbox", [])
        payload_len = len(rpn_payload)
    except Exception as e:
        print(f"Failed to join session: {e}")
        return

    random.seed(args.seed)
    
    all_runs = []
    all_latencies_across_runs = []
    
    # Warmup
    if args.warmup > 0:
        print(f"Performing warmup ({args.warmup} evals)...")
        for _ in range(args.warmup):
            client.evaluate_local(random.uniform(-5, 5), random.uniform(-5, 5))
        print("Warmup completed.")

    for run_idx in range(args.runs):
        print(f"Run {run_idx + 1}/{args.runs}...")
        
        run_latencies = []
        
        start_time = time.perf_counter()
        for _ in range(args.points):
            x = random.uniform(-5, 5)
            y = random.uniform(-5, 5)
            
            t0 = time.perf_counter()
            client.evaluate_local(x, y)
            t1 = time.perf_counter()
            run_latencies.append((t1 - t0) * 1000.0) # ms
            
        end_time = time.perf_counter()
        
        duration = end_time - start_time
        all_latencies_across_runs.extend(run_latencies)
        
        run_summary = {
            "run_index": run_idx,
            "duration_s": duration,
            "total_evals": args.points,
            "evals_per_second": args.points / duration if duration > 0 else 0,
            "eval_latency_ms": aggregate_metrics(run_latencies)
        }
        all_runs.append(run_summary)
        print(f"  Done: {args.points} evals in {duration:.4f}s ({run_summary['evals_per_second']:.2f} evals/s)")

    avg_duration = statistics.mean([r["duration_s"] for r in all_runs])
    avg_evals_per_s = statistics.mean([r["evals_per_second"] for r in all_runs])
    total_evals_all = sum(r["total_evals"] for r in all_runs)
    
    final_results = {
        "benchmark": "rpn_eval_speed",
        "parameters": vars(args),
        "environment": get_env_info(),
        "payload_info": {
            "rpn_payload_length": payload_len,
            "function_id": args.function
        },
        "runs": all_runs,
        "summary": {
            "avg_duration_s": avg_duration,
            "avg_evals_per_second": avg_evals_per_s,
            "total_evals_all_runs": total_evals_all,
            "latency_ms": aggregate_metrics(all_latencies_across_runs)
        }
    }
    
    save_results("rpn_eval", final_results, args.output_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark B: Local RPN Evaluation Speed")
    parser.add_argument("--url", default="http://localhost:8000", help="API URL")
    parser.add_argument("--points", type=int, default=10000, help="Evaluations per run")
    parser.add_argument("--runs", type=int, default=5, help="Number of benchmark runs")
    parser.add_argument("--warmup", type=int, default=1000, help="Warmup evaluations")
    parser.add_argument("--session-code", help="Existing session code (optional)")
    parser.add_argument("--function", default="sphere_shifted", help="Function ID for new session")
    parser.add_argument("--output-dir", default="benchmarks/results", help="Directory to save results")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    run_benchmark(args)
