import argparse
import random
import time
import threading
import statistics
from typing import List, Dict, Any
from benchmark_utils import (
    BlackBoxClient, 
    get_env_info, 
    create_benchmark_session, 
    save_results, 
    aggregate_metrics
)

def run_single_bot(
    api_url: str, 
    session_code: str, 
    bot_idx: int, 
    points_per_bot: int, 
    results: List[Dict[str, Any]], 
    seed: int
):
    random.seed(seed + bot_idx)
    client = BlackBoxClient(api_url, session_code)
    bot_name = f"BenchBot-A-{bot_idx:03d}"
    
    bot_data = {
        "name": bot_name,
        "points_done": 0,
        "latencies_ms": [],
        "errors": 0
    }
    
    try:
        client.join(bot_name)
    except Exception as e:
        print(f"[{bot_name}] Join failed: {e}")
        bot_data["errors"] += 1
        results.append(bot_data)
        return

    for _ in range(points_per_bot):
        x = random.uniform(-5, 5)
        y = random.uniform(-5, 5)
        
        start_time = time.perf_counter()
        try:
            client.evaluate(x, y)
            latency = (time.perf_counter() - start_time) * 1000.0
            bot_data["latencies_ms"].append(latency)
            bot_data["points_done"] += 1
        except Exception as e:
            bot_data["errors"] += 1
            # Continue to next point if one fails
            
    results.append(bot_data)

def run_benchmark(args):
    print(f"--- Starting Benchmark A: Individual REST Evaluation ---")
    
    session_code = args.session_code or create_benchmark_session(args.url, args.function)
    
    all_runs = []
    all_latencies_across_runs = []
    
    # Warmup
    if args.warmup > 0:
        print(f"Performing warmup ({args.warmup} points per bot)...")
        warmup_results = []
        threads = []
        for i in range(args.bots):
            t = threading.Thread(target=run_single_bot, args=(
                args.url, session_code, i, args.warmup, warmup_results, args.seed
            ))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        print("Warmup completed.")

    for run_idx in range(args.runs):
        print(f"Run {run_idx + 1}/{args.runs}...")
        run_results = []
        threads = []
        
        start_time = time.perf_counter()
        for i in range(args.bots):
            t = threading.Thread(target=run_single_bot, args=(
                args.url, session_code, i, args.points, run_results, args.seed + run_idx * 1000
            ))
            t.start()
            threads.append(t)
            
        for t in threads:
            t.join()
        end_time = time.perf_counter()
        
        duration = end_time - start_time
        total_points = sum(r["points_done"] for r in run_results)
        total_errors = sum(r["errors"] for r in run_results)
        run_latencies = [l for r in run_results for l in r["latencies_ms"]]
        all_latencies_across_runs.extend(run_latencies)
        
        run_summary = {
            "run_index": run_idx,
            "duration_s": duration,
            "total_points": total_points,
            "total_errors": total_errors,
            "points_per_second": total_points / duration if duration > 0 else 0,
            "latency_metrics_ms": aggregate_metrics(run_latencies)
        }
        all_runs.append(run_summary)
        print(f"  Done: {total_points} points in {duration:.2f}s ({run_summary['points_per_second']:.2f} pts/s)")

    # Aggregate all runs
    total_points_all = sum(r["total_points"] for r in all_runs)
    total_errors_all = sum(r["total_errors"] for r in all_runs)
    avg_duration = statistics.mean([r["duration_s"] for r in all_runs])
    avg_pts_per_s = statistics.mean([r["points_per_second"] for r in all_runs])
    
    final_results = {
        "benchmark": "individual_eval_baseline",
        "parameters": vars(args),
        "environment": get_env_info(),
        "session_code": session_code,
        "runs": all_runs,
        "summary": {
            "avg_duration_s": avg_duration,
            "avg_points_per_second": avg_pts_per_s,
            "total_points_all_runs": total_points_all,
            "total_requests_all_runs": total_points_all + total_errors_all,
            "total_errors_all_runs": total_errors_all,
            "error_rate": total_errors_all / (total_points_all + total_errors_all) if (total_points_all + total_errors_all) > 0 else 0,
            "latency_ms": aggregate_metrics(all_latencies_across_runs)
        }
    }
    
    save_results("individual_eval", final_results, args.output_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark A: Individual REST Evaluation Baseline")
    parser.add_argument("--url", default="http://localhost:8000", help="API URL")
    parser.add_argument("--bots", type=int, default=10, help="Number of concurrent bots")
    parser.add_argument("--points", type=int, default=50, help="Points per bot")
    parser.add_argument("--runs", type=int, default=3, help="Number of benchmark runs")
    parser.add_argument("--warmup", type=int, default=10, help="Warmup points per bot")
    parser.add_argument("--session-code", help="Existing session code (optional)")
    parser.add_argument("--function", default="sphere_shifted", help="Function ID for new session")
    parser.add_argument("--output-dir", default="benchmarks/results", help="Directory to save results")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    run_benchmark(args)
