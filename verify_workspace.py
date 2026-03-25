import subprocess
import sys
import os
import time

def run_command(cmd, cwd=None, env=None):
    print(f"Running: {cmd} (in {cwd or '.'})")
    result = subprocess.run(cmd, shell=True, cwd=cwd, env=env)
    return result.returncode == 0

def verify():
    print("=== Workspace Verification ===")
    
    backend_dir = "repos/framework-2d-optimization/backend"
    python_exe = r"C:\Users\neuba\AppData\Local\Programs\Python\Python311\python.exe"
    
    # 1. Install dependencies
    if not run_command(f"{python_exe} -m pip install -r {backend_dir}/requirements.txt"):
        print("❌ Failed to install dependencies.")
        return False
    
    # 2. Run API tests (unit/integration)
    env = os.environ.copy()
    env["PYTHONPATH"] = "."
    if not run_command(f"{python_exe} -m pytest tests/test_api.py", cwd=backend_dir, env=env):
        print("❌ API tests failed.")
        return False
    
    # 3. Start backend in background and run simulation
    print("Starting backend for simulation...")
    # Use uvicorn to start the app
    proc = subprocess.Popen(
        [python_exe, "-m", "uvicorn", "app.main:app", "--port", "8000"],
        cwd=backend_dir,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    time.sleep(3) # Wait for backend to start
    
    try:
        # Check health
        if not run_command(f"{python_exe} repos/framework-2d-optimization/.gemini_local/skills/2d-opt-manager/scripts/verify_api.py"):
            print("❌ Backend verification failed.")
            return False
            
        # Run simulation
        if not run_command(f"{python_exe} repos/framework-2d-optimization/.gemini_local/skills/2d-opt-manager/scripts/run_simulation.py"):
            print("❌ Simulation failed.")
            return False
            
    finally:
        print("Stopping backend...")
        proc.terminate()
        proc.wait()

    print("\n✅ WORKSPACE VERIFIED: Agent is ready for its first goal.")
    return True

if __name__ == "__main__":
    if not verify():
        sys.exit(1)
