import os
import sys
import json
import csv
import time
import platform
import subprocess
import requests
import statistics
from datetime import datetime
from typing import Any, Dict, List, Optional

# Add bot directory to sys.path to import BlackBoxClient
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "bot")))

try:
    from blackbox_client import BlackBoxClient
except ImportError:
    print("Error: Could not import BlackBoxClient. Make sure bot/blackbox_client.py exists.")
    sys.exit(1)

def get_git_hash() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("ascii").strip()
    except Exception:
        return "unknown"

def get_env_info() -> Dict[str, Any]:
    return {
        "python_version": platform.python_version(),
        "os": platform.system(),
        "os_release": platform.release(),
        "cpu_count": os.cpu_count(),
        "timestamp": datetime.now().isoformat(),
        "git_hash": get_git_hash()
    }

def create_benchmark_session(api_url: str, function_id: str = "sphere_shifted") -> str:
    """Creates a fresh stress session and returns the session code."""
    try:
        r = requests.post(f"{api_url.rstrip('/')}/sessions", json={
            "function_id": function_id,
            "goal": "min",
            "max_steps": 10000000 # High limit for benchmarking
        }, timeout=10)
        r.raise_for_status()
        code = r.json()["session_code"]
        print(f"Created fresh benchmark session: {code}")
        return code
    except Exception as e:
        print(f"Failed to create benchmark session: {e}")
        sys.exit(1)

def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def save_results(name: str, results: Dict[str, Any], output_dir: str = "benchmarks/results"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"benchmark_{name}_{timestamp}"
    
    # Save JSON
    json_path = os.path.join(output_dir, f"{filename}.json")
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved JSON results to {json_path}")
    
    # Save to summary CSV
    csv_path = os.path.join(output_dir, f"benchmark_{name}_{timestamp}.csv")
    
    # Flatten summary metrics for CSV
    summary = results.get("summary", {})
    params = results.get("parameters", {})
    
    # We flatten everything for the CSV
    flat_params = flatten_dict(params, "param")
    flat_summary = flatten_dict(summary, "metric")
    
    row = {**flat_params, **flat_summary}
    fieldnames = sorted(row.keys())
    
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(row)
    print(f"Saved CSV summary to {csv_path}")

def aggregate_metrics(metrics_list: List[float]) -> Dict[str, float]:
    if not metrics_list:
        return {}
    return {
        "mean": statistics.mean(metrics_list),
        "median": statistics.median(metrics_list),
        "min": min(metrics_list),
        "max": max(metrics_list),
        "std_dev": statistics.stdev(metrics_list) if len(metrics_list) > 1 else 0,
        "p95": statistics.quantiles(metrics_list, n=20)[18] if len(metrics_list) >= 20 else None
    }
