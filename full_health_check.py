import subprocess
import time
import requests
import sys
import os

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"
DOCKER_COMPOSE_FILE = "repos/framework-2d-optimization/docker-compose.yaml"

def run_shell(cmd, cwd=None):
    """Executes a shell command and returns True if successful."""
    print(f"\n> Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd)
    return result.returncode == 0

def wait_for_service(url, timeout=30):
    """Wait for a service to become available at the given URL."""
    print(f"Waiting for {url}...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print(f"✅ Service at {url} is up!")
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(2)
    print(f"❌ Timeout: Service at {url} did not respond within {timeout}s.")
    return False

def check_backend_api():
    """Verify backend API health and basic functionality."""
    print("\n--- Verifying Backend API ---")
    try:
        # 1. Health Endpoint
        res = requests.get(f"{BACKEND_URL}/health")
        if res.status_code != 200:
            print("❌ Backend health check failed.")
            return False
        print("✅ Backend health check passed.")

        # 2. List Functions
        res = requests.get(f"{BACKEND_URL}/functions")
        if res.status_code != 200:
            print("❌ Failed to list functions.")
            return False
        functions = res.json().get("functions", [])
        print(f"✅ Function list retrieved ({len(functions)} available).")
        
        # 3. Create Session (Functional Test)
        res = requests.post(f"{BACKEND_URL}/sessions", json={
            "function_id": functions[0]["id"], 
            "goal": "min", 
            "max_steps": 10
        })
        if res.status_code != 200:
            print(f"❌ Failed to create session: {res.text}")
            return False
        session_data = res.json()
        print(f"✅ Session created: {session_data['session_code']}")
        
        return True
    except Exception as e:
        print(f"❌ Backend check failed with error: {e}")
        return False

def check_frontend():
    """Verify frontend service is reachable."""
    print("\n--- Verifying Frontend ---")
    try:
        res = requests.get(FRONTEND_URL)
        if res.status_code == 200:
            print(f"✅ Frontend is reachable at {FRONTEND_URL}")
            return True
        else:
            print(f"❌ Frontend returned status {res.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend check failed: {e}")
        return False

def main():
    print("=== 🚀 Starting Full Health Test ===")
    
    # 1. Docker Build & Up
    if not run_shell(f"docker-compose -f {DOCKER_COMPOSE_FILE} up --build -d"):
        print("❌ Failed to start Docker containers.")
        sys.exit(1)

    try:
        # 2. Wait for services to be ready
        if not wait_for_service(f"{BACKEND_URL}/health"):
            sys.exit(1)
            
        # 3. Run Checks
        api_ok = check_backend_api()
        frontend_ok = check_frontend()

        if api_ok and frontend_ok:
            print("\n" + "="*40)
            print("🎉 ALL SYSTEMS GO: Workspace is healthy!")
            print("="*40)
        else:
            print("\n" + "!"*40)
            print("⚠️ HEALTH CHECK FAILED: Some systems are down.")
            print("!"*40)
            sys.exit(1)

    finally:
        # Optional: Ask user if they want to keep the containers running
        print("\nNote: Docker containers are still running in the background.")
        print(f"Use 'docker-compose -f {DOCKER_COMPOSE_FILE} down' to stop them.")

if __name__ == "__main__":
    main()
