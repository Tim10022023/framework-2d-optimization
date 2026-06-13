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
    evals_per_bot: int, 
    sync_interval: int,
    results: List[Dict[str, Any]], 
    seed: int
):
    random.seed(seed + bot_idx)
    client = BlackBoxClient(api_url, session_code)
    bot_name = f"BenchBot-C-{bot_idx:03d}"
    
    bot_data = {
        "name": bot_name,
        "evals_done": 0,
        "syncs_done": 0,
        "sync_durations_ms": [],
        "errors": 0,
        "best_z": float('inf')
    }
    
    try:
        client.join(bot_name)
    except Exception as e:
        print(f"[{bot_name}] Join failed: {e}")
        bot_data["errors"] += 1
        results.append(bot_data)
        return

    trajectory = []
    for step in range(1, evals_per_bot + 1):
        x = random.uniform(-5, 5)
        y = random.uniform(-5, 5)
        
        # Local evaluation
        z = client.evaluate_local(x, y)
        bot_data["best_z"] = min(bot_data["best_z"], z)
        bot_data["evals_done"] += 1
        
        trajectory.append({"x": x, "y": y, "z": z, "step": step})
        
        if step % sync_interval == 0:
            start_time = time.perf_counter()
            try:
                client.sync_trajectory(trajectory)
                latency = (time.perf_counter() - start_time) * 1000.0
                bot_data["sync_durations_ms"].append(latency)
                bot_data["syncs_done"] += 1
                trajectory = []
            except Exception as e:
                bot_data["errors"] += 1
                # Continue
                
    # Final sync
    if trajectory:
        start_time = time.perf_counter()
        try:
            client.sync_trajectory(trajectory)
            latency = (time.perf_counter() - start_time) * 1000.0
            bot_data["sync_durations_ms"].append(latency)
            bot_data["syncs_done"] += 1
        except Exception as e:
            bot_data["errors"] += 1
            
    results.append(bot_data)

def run_benchmark(args):
    print(f"--- Starting Benchmark C: Batch Synchronization / Parallel Bot Scaling ---")
    
    session_code = args.session_code or create_benchmark_session(args.url, args.function)
    
    all_runs = []
    all_sync_latencies_across_runs = []
    
    # Warmup (simple version)
    if args.warmup > 0:
        print(f"Performing warmup...")
        warmup_results = []
        threads = []
        for i in range(args.bots):
            t = threading.Thread(target=run_single_bot, args=(
                args.url, session_code, i, args.warmup, args.batch_size, warmup_results, args.seed
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
                args.url, session_code, i, args.evals_per_bot, args.batch_size, run_results, args.seed + run_idx * 1000
            ))
            t.start()
            threads.append(t)
            
        for t in threads:
            t.join()
        end_time = time.perf_counter()
        
        duration = end_time - start_time
        total_evals = sum(r["evals_done"] for r in run_results)
        total_syncs = sum(r["syncs_done"] for r in run_results)
        total_errors = sum(r["errors"] for r in run_results)
        run_sync_times = [l for r in run_results for l in r["sync_durations_ms"]]
        all_sync_latencies_across_runs.extend(run_sync_times)
        best_z_overall = min([r["best_z"] for r in run_results])
        
        run_summary = {
            "run_index": run_idx,
            "duration_s": duration,
            "total_evals": total_evals,
            "total_sync_requests": total_syncs,
            "total_errors": total_errors,
            "evals_per_second": total_evals / duration if duration > 0 else 0,
            "syncs_per_second": total_syncs / duration if duration > 0 else 0,
            "sync_latency_ms": aggregate_metrics(run_sync_times),
            "best_z": best_z_overall
        }
        all_runs.append(run_summary)
        print(f"  Done: {total_evals} evals in {duration:.2f}s ({run_summary['evals_per_second']:.2f} evals/s)")
        print(f"  Syncs: {total_syncs} requests, avg sync latency: {run_summary['sync_latency_ms'].get('mean', 0):.2f}ms")

    # Aggregate all runs
    avg_duration = statistics.mean([r["duration_s"] for r in all_runs])
    avg_evals_per_s = statistics.mean([r["evals_per_second"] for r in all_runs])
    total_evals_all = sum(r["total_evals"] for r in all_runs)
    total_syncs_all = sum(r["total_sync_requests"] for r in all_runs)
    total_errors_all = sum(r["total_errors"] for r in all_runs)
    
    final_results = {
        "benchmark": "batch_sync_scaling",
        "parameters": vars(args),
        "environment": get_env_info(),
        "session_code": session_code,
        "runs": all_runs,
        "summary": {
            "avg_duration_s": avg_duration,
            "avg_evals_per_second": avg_evals_per_s,
            "total_evals_all_runs": total_evals_all,
            "total_sync_requests_all_runs": total_syncs_all,
            "request_reduction_vs_individual_percent": (1 - total_syncs_all / total_evals_all) * 100 if total_evals_all > 0 else 0,
            "total_errors_all_runs": total_errors_all,
            "error_rate": total_errors_all / (total_syncs_all + total_errors_all) if (total_syncs_all + total_errors_all) > 0 else 0,
            "sync_latency_ms": aggregate_metrics(all_sync_latencies_across_runs)
        }
    }
    
    save_results("batch_sync", final_results, args.output_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark C: Batch Synchronization / Parallel Bot Scaling")
    parser.add_argument("--url", default="http://localhost:8000", help="API URL")
    parser.add_argument("--bots", type=int, default=10, help="Number of concurrent bots")
    parser.add_argument("--evals-per-bot", type=int, default=1000, help="Evaluations per bot")
    parser.add_argument("--batch-size", type=int, default=100, help="Batch size / sync interval")
    parser.add_argument("--runs", type=int, default=3, help="Number of benchmark runs")
    parser.add_argument("--warmup", type=int, default=100, help="Warmup evaluations per bot")
    parser.add_argument("--session-code", help="Existing session code (optional)")
    parser.add_argument("--function", default="sphere_shifted", help="Function ID for new session")
    parser.add_argument("--output-dir", default="benchmarks/results", help="Directory to save results")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    run_benchmark(args)
