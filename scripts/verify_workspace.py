import subprocess
import sys
import os

def run_command(cmd, cwd=None, env=None):
    """Execute a shell command and return True if successful."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, env=env)
    return result.returncode == 0

def verify():
    """Verify that the workspace is set up correctly."""
    print("=== Workspace Verification ===\n")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(script_dir, "backend")
    
    # 1. Install backend dependencies
    print("📦 Installing backend dependencies...")
    if not run_command("pip install -r requirements.txt", cwd=backend_dir):
        print("❌ Failed to install backend dependencies.")
        return False
    print("✅ Backend dependencies installed.\n")
    
    # 2. Install frontend dependencies
    print("📦 Installing frontend dependencies...")
    frontend_dir = os.path.join(script_dir, "frontend")
    if not run_command("npm install", cwd=frontend_dir):
        print("❌ Failed to install frontend dependencies.")
        return False
    print("✅ Frontend dependencies installed.\n")
    
    # 3. Run backend tests
    print("🧪 Running backend tests...")
    env = os.environ.copy()
    env["PYTHONPATH"] = "."
    if not run_command("pytest tests/test_api.py -v", cwd=backend_dir, env=env):
        print("❌ Backend tests failed.")
        return False
    print("✅ Backend tests passed.\n")
    
    # 4. Lint frontend
    print("🔍 Linting frontend code...")
    if not run_command("npm run lint", cwd=frontend_dir):
        print("⚠️  Frontend linting found issues (non-blocking).")
    print("✅ Frontend lint check complete.\n")
    
    # 5. Type check frontend
    print("📘 Type checking frontend code...")
    if not run_command("npx tsc --noEmit", cwd=frontend_dir):
        print("❌ Frontend type check failed.")
        return False
    print("✅ Frontend type check passed.\n")

    print("="*50)
    print("✅ WORKSPACE VERIFIED: Ready for development!")
    print("="*50)
    return True

if __name__ == "__main__":
    if not verify():
        sys.exit(1)
